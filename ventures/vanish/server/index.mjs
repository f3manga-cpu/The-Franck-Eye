import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../public');
const port=Number(process.env.PORT||3000);
const origin=process.env.PUBLIC_ORIGIN||`http://localhost:${port}`;
const stripeKey=process.env.STRIPE_SECRET_KEY||'';
const stripeWebhookSecret=process.env.STRIPE_WEBHOOK_SECRET||'';
const stripePaymentLink=process.env.STRIPE_PAYMENT_LINK_URL||'';
const priceId=process.env.STRIPE_PRICE_ID||'price_1UXMbHJglFhP7gGVTdQ9mD67';
const adminToken=process.env.ADMIN_TOKEN||'';
const isProduction=process.env.NODE_ENV==='production';
const legalApproved=process.env.LEGAL_APPROVED==='true';
const checkoutEnabled=Boolean(process.env.ACCEPT_REAL_PAYMENTS==='true'&&process.env.DURABLE_STORAGE_CONFIRMED==='true'&&adminToken.length>=24&&(stripeKey||/^https:\/\/buy\.stripe\.com\/[A-Za-z0-9]+$/.test(stripePaymentLink))&&stripeWebhookSecret&&legalApproved&&priceId&&(origin.startsWith('https://')||!isProduction));
const preview=!isProduction;
const imageAlt='VANISH — an ephemeral digital moment and a trace on the shared wall';
const amount=999900;
const now=()=>Date.now();
const dataDir=path.resolve(process.env.DATA_DIR||path.resolve(here,'../data'));
fs.mkdirSync(dataDir,{recursive:true});
const db=new DatabaseSync(path.join(dataDir,'vanish.sqlite'));
db.exec(`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
 CREATE TABLE IF NOT EXISTS orders (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 session_id TEXT UNIQUE NOT NULL,
 payment_intent TEXT,
 paid_at INTEGER NOT NULL,
 started_at INTEGER,
 receipt_id TEXT UNIQUE NOT NULL,
 status TEXT NOT NULL DEFAULT 'paid');
 CREATE TABLE IF NOT EXISTS inscriptions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 order_id INTEGER NOT NULL UNIQUE REFERENCES orders(id),
 slot INTEGER UNIQUE,
 body TEXT NOT NULL,
 submitted_at INTEGER NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending',
 reviewed_at INTEGER);
 CREATE INDEX IF NOT EXISTS idx_inscriptions_status ON inscriptions(status,id);`);
if (!db.prepare('PRAGMA table_info(inscriptions)').all().some(c=>c.name==='strokes')) db.exec("ALTER TABLE inscriptions ADD COLUMN strokes TEXT NOT NULL DEFAULT '[]'");
// For existing deployments created before wall placement was introduced.
const columns=db.prepare('PRAGMA table_info(inscriptions)').all().map(c=>c.name);
if(!columns.includes('slot'))db.exec('ALTER TABLE inscriptions ADD COLUMN slot INTEGER');
db.exec('CREATE UNIQUE INDEX IF NOT EXISTS idx_wall_slot ON inscriptions(slot) WHERE slot IS NOT NULL');
const security={
 'cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'strict-origin-when-cross-origin',
 'x-frame-options':'DENY','permissions-policy':'camera=(), microphone=(), geolocation=()',
 'content-security-policy':"default-src 'self'; script-src 'self' 'sha256-Rm/brVHj5HExIGXAJkhPJBChPnvadstG36aMyV3lVZE='; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
};
const send=(res,status,payload,kind='application/json; charset=utf-8')=>{res.writeHead(status,{...security,'content-type':kind});res.end(kind.startsWith('application/json')?JSON.stringify(payload):payload);};
const fail=(res,code,msg)=>send(res,code,{error:msg});
async function readBody(req,max=16384){let chunks=[],len=0;for await(const c of req){len+=c.length;if(len>max)throw Object.assign(new Error('Too large'),{status:413});chunks.push(c);}return Buffer.concat(chunks);}
function stripeSignatureValid(signature,raw,secret,at=now()){
 if(!signature||!secret)return false;
 const parts={};for(const p of signature.split(',')){const i=p.indexOf('=');if(i>0)(parts[p.slice(0,i)]??=[]).push(p.slice(i+1));}
 const t=Number(parts.t?.[0]);if(!Number.isInteger(t)||Math.abs(at-t*1000)>300000)return false;
 const expected=crypto.createHmac('sha256',secret).update(`${t}.${raw.toString('utf8')}`).digest('hex');
 return (parts.v1||[]).some(v=>/^[0-9a-f]{64}$/i.test(v)&&crypto.timingSafeEqual(Buffer.from(v,'hex'),Buffer.from(expected,'hex')));
}
function paidSession(s){return Boolean(s&&s.object==='checkout.session'&&s.mode==='payment'&&s.payment_status==='paid'&&s.currency==='usd'&&s.amount_total===amount&&s.metadata?.product==='vanish-one-moment'&&typeof s.id==='string');}
function registerPayment(s){if(!paidSession(s))return null;
 let o=db.prepare('SELECT * FROM orders WHERE session_id=?').get(s.id);if(o)return o;
 db.prepare('INSERT OR IGNORE INTO orders (session_id,payment_intent,paid_at,receipt_id) VALUES (?,?,?,?)').run(s.id,typeof s.payment_intent==='string'?s.payment_intent:s.payment_intent?.id||null,now(),crypto.randomBytes(20).toString('base64url'));
 return db.prepare('SELECT * FROM orders WHERE session_id=?').get(s.id);
}
async function stripe(endpoint,{method='GET',params}={}){
 if(!stripeKey)throw new Error('Stripe not configured');
 const resp=await fetch('https://api.stripe.com/v1/'+endpoint,{method,headers:{authorization:`Bearer ${stripeKey}`,...(params?{'content-type':'application/x-www-form-urlencoded'}:{})},body:params?new URLSearchParams(params):undefined,signal:AbortSignal.timeout(15000)});
 const obj=await resp.json();if(!resp.ok)throw new Error(obj.error?.message||'Stripe request failed');return obj;
}
const sessionIdGood=s=>/^cs_(test_|live_)[A-Za-z0-9_]{10,200}$/.test(String(s||''));
const receiptGood=s=>/^[A-Za-z0-9_-]{20,40}$/.test(String(s||''));
const serial=o=>`V-${String(o.id).padStart(6,'0')}`;
const view=o=>{
 const inscription=db.prepare('SELECT body,status,slot,strokes FROM inscriptions WHERE order_id=?').get(o.id);
 const expiresAt=o.started_at==null?null:o.started_at+12000;
 return {serial:serial(o),receiptId:o.receipt_id,status:o.status,started:o.started_at!=null,expired:expiresAt!=null&&now()>=expiresAt,expiresAt,inscription:inscription?{body:inscription.body,status:inscription.status,slot:inscription.slot,strokes:JSON.parse(inscription.strokes||'[]')}:null};
};
function normalizeMark(value){if(typeof value!=='string')return null;
 let s=value.normalize('NFKC').replace(/[\u0000-\u001F\u007F-\u009F\u200B-\u200D\uFEFF]/g,'').replace(/\s+/g,' ').trim();
 if(s.length<1||[...s].length>64||/[<>]/.test(s)||/https?:|www\.|@/i.test(s))return null;
 return s;
}
function normalizeStrokes(value){
 if(value==null)return [];
 if(!Array.isArray(value)||value.length>24)return null;
 let total=0;const result=[];
 for(const stroke of value){
  if(!Array.isArray(stroke)||stroke.length<2||stroke.length>200)return null;
  total+=stroke.length;if(total>900)return null;
  const pts=[];
  for(const pt of stroke){if(!Array.isArray(pt)||pt.length!==2||!pt.every(n=>Number.isInteger(n)&&n>=0&&n<=1000))return null;pts.push(pt);}
  result.push(pts);
 }return result;
}
const bursts=new Map();function allow(ip){const t=now(),xs=(bursts.get(ip)||[]).filter(v=>v>t-60000);if(xs.length>12)return false;xs.push(t);bursts.set(ip,xs);if(bursts.size>2500)bursts.clear();return true;}
const mime={'.xml':'application/xml; charset=utf-8','.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml','.ico':'image/x-icon','.txt':'text/plain; charset=utf-8'};
function reqAdmin(req){return Boolean(adminToken.length>=24&&req.headers.authorization===`Bearer ${adminToken}`);}
const server=http.createServer(async(req,res)=>{
 try{
 const u=new URL(req.url,origin),p=u.pathname;

 if(p==='/og-preview.webp' && (req.method==='GET'||req.method==='HEAD')){
  const card=Buffer.from(fs.readFileSync(path.join(root,'og-image.b64'),'utf8'),'base64');
  res.writeHead(200,{...security,'content-type':'image/webp','content-length':card.length,'cache-control':'public,max-age=86400'});
  return req.method==='HEAD'?res.end():res.end(card);
 }
 if(p==='/health'&&req.method==='GET')return send(res,200,{ok:true,checkoutEnabled,wall:true});
 if(p==='/healthz'&&req.method==='GET')return send(res,200,{status:'ok',storage:'sqlite',checkoutEnabled});
 if(p==='/robots.txt'&&req.method==='GET')return send(res,200,`User-agent: *\nDisallow: /api/\nDisallow: /admin.html\nDisallow: /mark/\nSitemap: ${origin}/sitemap.xml\n`,'text/plain; charset=utf-8');
 if(p==='/sitemap.xml'&&req.method==='GET')return send(res,200,`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>${origin}/</loc></url></urlset>`,'application/xml; charset=utf-8');
 if(p==='/api/config'&&req.method==='GET')return send(res,200,{checkoutEnabled,preview,amount:9999,brand:'VANISH'});
 if(p==='/api/wall'&&req.method==='GET'){
  const page=Math.max(1,Math.min(20000,Number.parseInt(u.searchParams.get('page')||'1')||1));const per=u.searchParams.get('per')==='18'?18:30;
  const marks=db.prepare(`SELECT o.receipt_id,o.id,i.slot,i.body,i.strokes,i.submitted_at FROM inscriptions i JOIN orders o ON o.id=i.order_id WHERE i.status='visible' AND o.status='paid' AND i.slot BETWEEN ? AND ? ORDER BY i.slot ASC`).all((page-1)*per+1,page*per);
  const busy=db.prepare(`SELECT slot FROM inscriptions WHERE status IN ('visible','pending') AND slot BETWEEN ? AND ?`).all((page-1)*per+1,page*per).map(m=>m.slot);
  const total=db.prepare("SELECT MAX(slot) n FROM inscriptions WHERE status IN ('visible','pending')").get().n||0;
  return send(res,200,{page,hasNext:total>page*per,busy,marks:marks.map(m=>({slot:m.slot,serial:`V-${String(m.id).padStart(6,'0')}`,receiptId:m.receipt_id,text:m.body,strokes:JSON.parse(m.strokes||'[]')}))});
 }
 if(p==='/api/checkout'&&req.method==='POST'){
  if(!checkoutEnabled)return fail(res,503,'Purchasing is not currently available.');
  if(!allow(req.socket.remoteAddress||''))return fail(res,429,'Try again later.');
  if(!stripeKey && stripePaymentLink)return send(res,200,{url:stripePaymentLink});
  const s=await stripe('checkout/sessions',{method:'POST',params:{
   mode:'payment', 'line_items[0][price]':priceId,'line_items[0][quantity]':'1',
   'metadata[product]':'vanish-one-moment',
   'payment_intent_data[metadata][product]':'vanish-one-moment',
   success_url:`${origin}/?session_id={CHECKOUT_SESSION_ID}`,cancel_url:`${origin}/?cancel=1`,
   'billing_address_collection':'auto',
   'consent_collection[terms_of_service]':'required',
   'custom_text[submit][message]':'One 12-second digital moment followed by one optional wall inscription, subject to review.'
  }});
  return send(res,200,{url:s.url});
 }
 if(p==='/api/stripe-webhook'&&req.method==='POST'){
  const raw=await readBody(req,1024*1024);
  if(!stripeSignatureValid(req.headers['stripe-signature'],raw,stripeWebhookSecret))return fail(res,400,'Bad signature');
  const e=JSON.parse(raw.toString('utf8'));
  if(['checkout.session.completed','checkout.session.async_payment_succeeded'].includes(e.type))registerPayment(e.data?.object);
  if(e.type==='charge.refunded'&&e.data?.object?.payment_intent)db.prepare(`UPDATE orders SET status='refunded' WHERE payment_intent=?`).run(e.data.object.payment_intent);
  return send(res,200,{received:true});
 }
 if(p==='/api/payment'&&req.method==='GET'){
  const id=u.searchParams.get('session_id');if(!sessionIdGood(id))return fail(res,400,'Invalid session');
  let order=db.prepare('SELECT * FROM orders WHERE session_id=?').get(id);
  if(!order&&stripeKey)order=registerPayment(await stripe('checkout/sessions/'+encodeURIComponent(id)));
  if(!order)return fail(res,403,'Payment not verified');
  return send(res,200,view(order));
 }
 if(p==='/api/experience/start'&&req.method==='POST'){
  const id=JSON.parse((await readBody(req)).toString('utf8')).sessionId;
  if(!sessionIdGood(id))return fail(res,400,'Invalid session');
  let order=db.prepare('SELECT * FROM orders WHERE session_id=?').get(id);
  if(!order&&stripeKey)order=registerPayment(await stripe('checkout/sessions/'+encodeURIComponent(id)));
  if(!order||order.status!=='paid')return fail(res,403,'Payment not verified');
  db.prepare(`UPDATE orders SET started_at=? WHERE session_id=? AND started_at IS NULL AND status='paid'`).run(now(),id);
  return send(res,200,view(db.prepare('SELECT * FROM orders WHERE session_id=?').get(id)));
 }
 if(p==='/api/experience/inscribe'&&req.method==='POST'){
  const data=JSON.parse((await readBody(req)).toString('utf8'));
  if(!sessionIdGood(data.sessionId))return fail(res,400,'Invalid session');
  const mark=data.text?.trim()?normalizeMark(data.text):'';const strokes=normalizeStrokes(data.strokes);if(mark===null||strokes===null||(!mark&&!strokes.length))return fail(res,400,'Use up to 64 characters, or draw a mark. No links.');
  const slot=data.slot??(db.prepare('SELECT COALESCE(MAX(slot),0)+1 AS n FROM inscriptions').get().n);if(!Number.isInteger(slot)||slot<1||slot>100000)return fail(res,400,'Select a valid wall space.');
  const o=db.prepare('SELECT * FROM orders WHERE session_id=?').get(data.sessionId);
  if(!o||o.status!=='paid'||o.started_at==null||now()<o.started_at+12000)return fail(res,403,'Not available yet.');
  if(db.prepare('SELECT id FROM inscriptions WHERE order_id=?').get(o.id))return fail(res,409,'Inscription already submitted.');
  // A space may be claimed while a buyer completes checkout. Never strand a paid buyer:
  // automatically allocate the next unclaimed space rather than failing fulfillment.
  let assigned=slot;
  try{db.prepare('INSERT INTO inscriptions (order_id,slot,body,strokes,submitted_at) VALUES (?,?,?,?,?)').run(o.id,assigned,mark,JSON.stringify(strokes),now());}
  catch(e){
   if(!(e.code==='ERR_SQLITE_ERROR' && (e.errcode===2067||e.errcode===1555)))throw e;
   if(db.prepare('SELECT id FROM inscriptions WHERE order_id=?').get(o.id))return fail(res,409,'Inscription already submitted.');
   assigned=db.prepare('SELECT COALESCE(MAX(slot),0)+1 AS n FROM inscriptions').get().n;
   db.prepare('INSERT INTO inscriptions (order_id,slot,body,strokes,submitted_at) VALUES (?,?,?,?,?)').run(o.id,assigned,mark,JSON.stringify(strokes),now());
  }
  return send(res,201,view(o));
 }
 if(p.startsWith('/api/receipt/')&&req.method==='GET'){
  const rid=p.slice('/api/receipt/'.length);if(!receiptGood(rid))return fail(res,404,'Not found');
  const o=db.prepare('SELECT * FROM orders WHERE receipt_id=? AND status=?').get(rid,'paid');if(!o)return fail(res,404,'Not found');
  const mark=db.prepare("SELECT body,slot,strokes FROM inscriptions WHERE order_id=? AND status='visible'").get(o.id);
  return send(res,200,{serial:serial(o),text:mark?.body||null,slot:mark?.slot||null,strokes:mark?JSON.parse(mark.strokes||'[]'):[]});
 }
 if(p==='/api/admin/pending'&&req.method==='GET'){
  if(!reqAdmin(req))return fail(res,401,'Unauthorized');
  const marks=db.prepare(`SELECT i.id,i.slot,i.body,i.strokes,i.submitted_at,o.id order_id FROM inscriptions i JOIN orders o ON o.id=i.order_id WHERE i.status='pending' AND o.status='paid' ORDER BY i.id ASC LIMIT 100`).all();
  return send(res,200,{marks:marks.map(m=>({...m,strokes:JSON.parse(m.strokes||'[]')}))});
 }
 if(p==='/api/admin/moderate'&&req.method==='POST'){
  if(!reqAdmin(req))return fail(res,401,'Unauthorized');
  const d=JSON.parse((await readBody(req)).toString('utf8'));
  if(!Number.isInteger(d.id)||!['visible','rejected'].includes(d.status))return fail(res,400,'Bad data');
  const out=db.prepare("UPDATE inscriptions SET status=?,reviewed_at=? WHERE id=? AND status='pending'").run(d.status,now(),d.id);
  return send(res,out.changes?200:404,{updated:out.changes});
 }
 if(p.startsWith('/mark/')&&req.method==='GET'){
  const rid=p.slice('/mark/'.length);if(!receiptGood(rid))return fail(res,404,'Not found');
  const o=db.prepare('SELECT * FROM orders WHERE receipt_id=? AND status=?').get(rid,'paid');
  if(!o)return fail(res,404,'Not found');
  const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const title=`${serial(o)} — VANISH`;
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8').replace(/<title>[^<]*<\/title>/,`<title>${esc(title)}</title>`).replace('</head>',`<meta name="robots" content="noindex,follow"><meta property="og:type" content="website"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="A moment happened here."><meta property="og:url" content="${origin}/mark/${rid}"></head>`);
  return send(res,200,html,'text/html; charset=utf-8');
 }
 if(req.method!=='GET'&&req.method!=='HEAD')return fail(res,405,'Method not allowed');
 const file=path.resolve(root,'.'+decodeURIComponent(p==='/'?'/index.html':p));
 if(!file.startsWith(root+path.sep))return fail(res,403,'Forbidden');
 let stat;try{stat=fs.statSync(file);}catch{return fail(res,404,'Not found');}if(!stat.isFile())return fail(res,404,'Not found');
 res.writeHead(200,{...security,'content-type':mime[path.extname(file)]||'application/octet-stream','cache-control':p==='/'?'no-cache':'public,max-age=3600'});
 if(req.method==='HEAD')return res.end();
  if(p==='/'||p==='/index.html'){let html=fs.readFileSync(file,'utf8');html=html.replace('content="/assets/portal.webp"', 'content="'+origin+'/og-preview.webp"');html=html.replace('</head>', '<link rel="canonical" href="'+origin+'/"><meta property="og:url" content="'+origin+'/"></head>');return res.end(html); }
  fs.createReadStream(file).pipe(res);
 }catch(e){console.error(e);return fail(res,e.status||500,e.status===413?'Request too large':'Request could not be completed');}
});
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))server.listen(port,()=>console.log(`VANISH on ${origin} — checkout ${checkoutEnabled?'ENABLED':'disabled'} / preview ${preview}`));
export {server,db,paidSession,stripeSignatureValid,registerPayment,normalizeMark,normalizeStrokes,view};
