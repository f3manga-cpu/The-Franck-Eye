import test from 'node:test';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {server,db,paidSession,stripeSignatureValid,normalizeMark,registerPayment,view,normalizeStrokes} from '../server/index.mjs';
test('payment verification rejects non-paid or altered session',()=>{
 const s={id:'cs_test_abcdef1234567890',object:'checkout.session',mode:'payment',payment_status:'paid',currency:'usd',amount_total:999900,metadata:{product:'vanish-one-moment'}};
 assert.equal(paidSession(s),true);assert.equal(paidSession({...s,amount_total:999}),false);assert.equal(paidSession({...s,payment_status:'unpaid'}),false);assert.equal(paidSession({...s,metadata:{product:'other'}}),false);
});
test('stripe signature requires correct secret and timestamp',()=>{
 const secret='whsec_fake-test';const raw=Buffer.from('{"hello":true}');const t=1700000000;const sig=crypto.createHmac('sha256',secret).update(`${t}.${raw}`).digest('hex');
 assert.equal(stripeSignatureValid(`t=${t},v1=${sig}`,raw,secret,t*1000),true);assert.equal(stripeSignatureValid(`t=${t},v1=${sig}`,raw,'wrong',t*1000),false);assert.equal(stripeSignatureValid(`t=${t},v1=${sig}`,raw,secret,t*1000+999999),false);
});
test('wall inscription input is normalized and length limited',()=>{
 assert.equal(normalizeMark('  A   vanished\n fortune   '),'A vanished fortune');assert.equal(normalizeMark('https://example.org'),null);assert.equal(normalizeMark('x'.repeat(65)),null);assert.equal(normalizeMark('<script>'),null);
});
test('verified session registers once and creates one receipt',()=>{
 const s={id:'cs_test_abcdef1234567890',object:'checkout.session',mode:'payment',payment_status:'paid',currency:'usd',amount_total:999900,metadata:{product:'vanish-one-moment'}};
 const a=registerPayment(s),b=registerPayment(s);assert.equal(a.id,b.id);assert.equal(view(a).started,false);assert.equal(view(a).receiptId.length>=20,true);
});
test('API wall does not expose pending inscriptions',async()=>{
 await new Promise(res=>server.listen(0,'127.0.0.1',res));const port=server.address().port;
 const url=`http://127.0.0.1:${port}`;try{const c=await fetch(url+'/api/config').then(r=>r.json());assert.equal(c.amount,9999);assert.equal(c.checkoutEnabled,false);
 const w=await fetch(url+'/api/wall').then(r=>r.json());assert.ok(Array.isArray(w.marks));assert.equal(w.marks.length,0);
 const payment=await fetch(url+'/api/checkout',{method:'POST',body:'{}'});assert.equal(payment.status,503);
 const unauthorized=await fetch(url+'/api/experience/inscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'cs_test_abcdef1234567890',text:'FLEX'})});assert.equal(unauthorized.status,403);
 }finally{await new Promise(res=>server.close(res));}
});
test('one paid order gets one inscription; public wall only shows moderated text',async()=>{
 const session=`cs_test_${crypto.randomBytes(12).toString('hex')}`;
 const o=registerPayment({id:session,object:'checkout.session',mode:'payment',payment_status:'paid',currency:'usd',amount_total:999900,metadata:{product:'vanish-one-moment'}});
 db.prepare('UPDATE orders SET started_at=? WHERE id=?').run(Date.now()-15000,o.id);
 await new Promise(res=>server.listen(0,'127.0.0.1',res));const uri=`http://127.0.0.1:${server.address().port}`;
 try{
  const r=await fetch(uri+'/api/experience/inscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:session,text:'Now you see me.'})});
  assert.equal(r.status,201);const result=await r.json();assert.equal(result.inscription.status,'pending');assert.equal(result.inscription.body,'Now you see me.');
  const twice=await fetch(uri+'/api/experience/inscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:session,text:'Second inscription'})});assert.equal(twice.status,409);
  let data=await fetch(uri+'/api/receipt/'+result.receiptId).then(r=>r.json());assert.equal(data.text,null);
  db.prepare("UPDATE inscriptions SET status='visible' WHERE order_id=?").run(o.id);
  data=await fetch(uri+'/api/receipt/'+result.receiptId).then(r=>r.json());assert.equal(data.text,'Now you see me.');
  const wall=await fetch(uri+'/api/wall').then(r=>r.json());assert.ok(wall.marks.some(m=>m.receiptId===result.receiptId&&m.text==='Now you see me.'));
 }finally{db.prepare('DELETE FROM inscriptions WHERE order_id=?').run(o.id);db.prepare('DELETE FROM orders WHERE id=?').run(o.id);await new Promise(res=>server.close(res));}
});

test('tactile marks have bounded normalized coordinates',()=>{
 assert.deepEqual(normalizeStrokes([[[0,0],[1000,1000]]]),[[[0,0],[1000,1000]]]);
 assert.equal(normalizeStrokes([[[0,0],[-5,100]]]),null);
 assert.equal(normalizeStrokes(Array(25).fill([[0,0],[5,5]])),null);
 assert.equal(normalizeStrokes([[[0,0],[Infinity,1]]]),null);
});
test('a verified buyer can leave only one handwritten mark',async()=>{
 const sess='cs_test_'+crypto.randomBytes(12).toString('hex');
 const o=registerPayment({id:sess,object:'checkout.session',mode:'payment',payment_status:'paid',currency:'usd',amount_total:999900,metadata:{product:'vanish-one-moment'}});
 db.prepare('UPDATE orders SET started_at=? WHERE id=?').run(Date.now()-15000,o.id);
 await new Promise(res=>server.listen(0,'127.0.0.1',res));const base=`http://127.0.0.1:${server.address().port}`;
 try{const r=await fetch(base+'/api/experience/inscribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({sessionId:sess,text:'',strokes:[[[100,500],[900,500]]]})});
 assert.equal(r.status,201);const j=await r.json();assert.deepEqual(j.inscription.strokes,[[[100,500],[900,500]]]);
 assert.equal((await fetch(base+'/api/experience/inscribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({sessionId:sess,text:'another mark'})})).status,409);
 db.prepare("UPDATE inscriptions SET status='visible' WHERE order_id=?").run(o.id);
 const pub=await fetch(base+'/api/receipt/'+j.receiptId).then(r=>r.json());assert.deepEqual(pub.strokes,[[[100,500],[900,500]]]);
 }finally{db.prepare('DELETE FROM inscriptions WHERE order_id=?').run(o.id);db.prepare('DELETE FROM orders WHERE id=?').run(o.id);await new Promise(res=>server.close(res));}
});
