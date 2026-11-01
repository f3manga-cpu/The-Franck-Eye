#!/usr/bin/env python3
"""Public-source chess ecosystem audit. No player/minor profiling; all assertions source-traceable."""
import csv, re, json, os, hashlib, io, time, random, math, unicodedata, collections
from pathlib import Path
from datetime import datetime, timezone
import requests
import networkx as nx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

OUT = Path("research/echecs_2026/results")
OUT.mkdir(parents=True, exist_ok=True)
RAW = OUT / "raw"; RAW.mkdir(exist_ok=True)
S = requests.Session()
S.headers.update({"User-Agent":"PublicResearchChessGraph/0.1 (research reproducibility; low rate; non-commercial)"})
manifest=[]
events=[]; grants=[]; anomalies=[]; warnings=[]

def fetch(url, label, max_bytes=40000000, timeout=65):
    rec={"label":label,"url":url,"retrieved_utc":datetime.now(timezone.utc).isoformat(),"status":"error"}
    try:
        r=S.get(url,timeout=timeout,stream=True,allow_redirects=True)
        rec.update({"http_status":r.status_code,"final_url":r.url})
        r.raise_for_status()
        chunks=[]; n=0
        for chunk in r.iter_content(1024*256):
            n += len(chunk)
            if n>max_bytes: raise ValueError("resource exceeds size cap")
            chunks.append(chunk)
        raw=b"".join(chunks)
        rec.update({"status":"ok","bytes":n,"sha256":hashlib.sha256(raw).hexdigest()})
        if raw[:10].lower().startswith(b"<!doctype") and label.startswith("plf"):
            raise ValueError("HTML returned for CSV")
        return raw
    except Exception as e:
        rec["error"]=repr(e);warnings.append(label+": "+str(e)[:120]);return None
    finally:
        manifest.append(rec)

def textnorm(x):
    x=unicodedata.normalize('NFKD',str(x or ''))
    x=''.join(c for c in x if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',re.sub(r'[^A-Z0-9]+',' ',x.upper())).strip()

def number(v):
    s=str(v or "").strip().replace("\u202f","").replace("\xa0","").replace(" ","")
    if not s:return None
    s=re.sub(r'[^0-9,.-]','',s)
    if not s:return None
    if ',' in s and '.' in s: s=s.replace('.','').replace(',','.')
    elif ',' in s: s=s.replace(',','.')
    try:return float(s)
    except:return None

def save_csv(name, rows, fieldnames):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='ignore');w.writeheader();w.writerows(rows)

def parse_table(raw, origin, label):
    if not raw:return []
    text=raw.decode("utf-8-sig",errors="replace")
    dialect=csv.Sniffer()
    try:d=dialect.sniff(text[:8000],delimiters=';,|\t')
    except:d=csv.excel
    rr=list(csv.DictReader(io.StringIO(text),dialect=d))
    for r in rr:r["_dataset"]=label;r["_url"]=origin
    return rr

# 1. Whole government fiscal-support annex, not just cherry-picked chess names.
plf_urls=[
 ("plf2025_state","https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf25-donnees-de-l-annexe-jaune-effort-financier-de-l-etat-en-faveur-des-associations/exports/csv?use_labels=true"),
 ("plf2025_state_alt","https://www.data.gouv.fr/api/1/datasets/r/9527d4a9-6e81-4109-913e-830f8d5b5c86")
]
rows=[]; selected_source=""
for label,url in plf_urls:
    raw=fetch(url,label)
    if raw:
        possible=parse_table(raw,url,label)
        if len(possible)>5000:
            rows=possible;selected_source=url
            (RAW/"state_plf2025.csv").write_bytes(raw)
            break
        warnings.append(label+" too few parsed rows: "+str(len(possible)))

def rowmatches(row):
    vals=" ".join(str(v or "") for k,v in row.items() if not str(k).startswith('_'))
    return bool(re.search(r'\b(?:E[CH]IQUIER|ECHECS|ECHIQUEEN|CHESS|SCHACH|ECHEC)\b',textnorm(vals)))
chess_rows=[r for r in rows if rowmatches(r)]
headers=list(rows[0]) if rows else []
with (OUT/"source_schema.json").open("w") as f: json.dump({"plf_columns":headers,"example_redacted":{k:(str(v)[:80] if not re.search('nom|prenom|name',k,re.I) else '[redacted]') for k,v in (rows[0] if rows else {}).items()}},f,indent=2,ensure_ascii=False)
save_csv("plf2025_chess_hits.csv",chess_rows,headers)

# Identify funding columns by content+headers. Raw row kept for review, avoid inventing categories.
def findcol(cols, words):
    for w in words:
        for c in cols:
            if w in textnorm(c):return c
    return None

def collect_grants(dataset_rows, tag):
    if not dataset_rows:return
    col=list(dataset_rows[0])
    namecol=findcol(col,['DENOMINATION','NOM ASSOCIATION','NOM ORGANISME','BENEFICIAIRE','RAISON SOCIALE','TIERS'])
    sirencol=findcol(col,['SIREN','SIRET'])
    amountcols=[c for c in col if any(w in textnorm(c) for w in ['MONTANT','CREDITS','SOMME','SUBVENTION','VERSE','TOTAL']) and not any(w in textnorm(c) for w in ['DESCRIPTION','TYPE','NATURE'])]
    programcol=findcol(col,['PROGRAMME','MINISTERE','FINANCEUR','MISSION','SERVICE VERSANT'])
    for r in dataset_rows:
        entity=r.get(namecol,'') if namecol else ''
        if not entity:
            continue
        ident=str(r.get(sirencol,'') if sirencol else '').replace(' ','').strip()
        if ident and not re.fullmatch(r'\d{9}|\d{14}',ident): ident=''
        pay=r.get(programcol,'') if programcol else "Etat / source "+tag
        amounts=[(c,number(r.get(c))) for c in amountcols]
        amounts=[(c,a) for c,a in amounts if a is not None]
        if not amounts:amounts=[("",None)]
        # Avoid double counting different financial columns; explicitly separate measures.
        for c,a in amounts:
            grants.append({"beneficiary":entity,"siren_siret":ident,"funder_program":str(pay),
                           "amount":a,"amount_field":c,"dataset":tag,"evidence_url":r.get("_url","")})

collect_grants(chess_rows,"PLF2025")

# 2. Opportunistic secondary open local subsidy datasets via API metadata.
# We ingest datasets only if tabular, under 20 MB, relevant to associations and with accessible links.
api="https://www.data.gouv.fr/api/1/datasets/?q=subventions%20associations&page_size=100"
raw=fetch(api,"datagouv_catalog_subventions",max_bytes=6000000)
if raw:
    try:
        payload=json.loads(raw)
        datasets=payload.get("data",[])
        candidates=[]
        for d in datasets:
            for res in d.get("resources",[]):
                fmt=(res.get("format") or "").lower()
                size=res.get("filesize") or res.get("size") or 0
                if fmt=="csv" and 1000 < size < 13000000 and res.get("url"):
                    candidates.append((d.get("title",""),res["url"],size))
        seen=set()
        for title,url,size in candidates[:18]:
            if url in seen:continue
            seen.add(url)
            b=fetch(url,"local_subsidies:"+title,max_bytes=14000000)
            if not b:continue
            try:
                tbl=parse_table(b,url,"Local:"+title)
                hits=[r for r in tbl if rowmatches(r)]
                if hits:
                    cols=list(hits[0]);save_csv("local_"+str(len(seen))+"_chess_hits.csv",hits,cols)
                    collect_grants(hits,"Local:"+title)
            except Exception as exc: warnings.append("parse local "+title+": "+str(exc))
    except Exception as exc: warnings.append("metadata parsing: "+str(exc))

save_csv("public_funding_edges.csv",grants,
         ["beneficiary","siren_siret","funder_program","amount","amount_field","dataset","evidence_url"])

# 3. Consistent bounded sample of FFE tournament cards for 2023-2026.
# No players are scraped or connected; ONLY public organizer/arbitrator roles.
base="https://www.echecs.asso.fr/FicheTournoi.aspx?Ref="
random.seed(20261101)
ref_ranges={2023:(56000,60500),2024:(61000,65400),2025:(66000,70100),2026:(70400,73900)}
samples=[]
for year,(a,b) in ref_ranges.items():
    samples += [(year,ref) for ref in random.sample(range(a,b),60)]
samples += [(2024,63120),(2025,66882),(2026,70779),(2026,70947),(2025,67722),(2026,72266)]
seen_ref=set()
for year,ref in samples:
    if ref in seen_ref:continue
    seen_ref.add(ref)
    url=base+str(ref)
    raw=fetch(url,"ffe_tournament:"+str(ref),max_bytes=1000000,timeout=18)
    if not raw:continue
    soup=BeautifulSoup(raw,"html.parser")
    for bad in soup(["script","style","noscript"]):bad.decompose()
    txt=soup.get_text(" ",strip=True)
    if "Organisateur" not in txt and "Arbitre" not in txt:continue
    # robust extraction independent of HTML table layout
    entry={"ref":ref,"reference_year_bucket":year,"title":"","location":"","organiser":"","arbiter":"","date":"","evidence_url":url}
    title=soup.title.get_text(" ",strip=True) if soup.title else ""
    entry["title"]=title
    for tr in soup.select("tr"):
        cells=[x.get_text(" ",strip=True) for x in tr.find_all(["th","td"],recursive=False)]
        if len(cells)<2:continue
        label=textnorm(cells[0]).replace(" ","")
        value=" ".join(cells[1:])[:350]
        for pattern,key in [("ORGANISATEUR","organiser"),("ARBITRE","arbiter"),("DATES","date"),("LIEU","location")]:
            if label.startswith(pattern) and not entry[key]:entry[key]=value
    if not entry["organiser"] and not entry["arbiter"]:
        for key,pattern in [("organiser",r'Organisateur\s*:\s*(.{4,100}?)(?:\s+Arbitre\s*:|\s+Adresse\s*:)'),("arbiter",r'Arbitre\s*:\s*(.{4,100}?)(?:\s+Adresse\s*:|\s+Contact\s*:)')]:
            m=re.search(pattern,txt,re.I)
            if m:entry[key]=m.group(1).strip()
    if entry["organiser"] or entry["arbiter"]:
        events.append(entry)
    time.sleep(0.12)
save_csv("ffe_events_sample.csv",events,["ref","reference_year_bucket","title","location","organiser","arbiter","date","evidence_url"])

# 4. Graph: no inferences from mere homonyms; finance and event layers separate.
G=nx.MultiGraph()
for e in events:
    tid="TOURNAMENT:"+str(e["ref"]);G.add_node(tid,type="tournament",label=e["title"][:80],source=e["evidence_url"])
    for field,role in [("organiser","organises"),("arbiter","arbitrates")]:
        name=e.get(field,"").strip()
        if len(name)>2:
            nid=role.upper()+":"+textnorm(name)
            G.add_node(nid,type=role,label=name)
            G.add_edge(nid,tid,relationship=role,year=e["reference_year_bucket"],source=e["evidence_url"])
for e in grants:
    name=e["beneficiary"];origin=e["funder_program"];amt=e["amount"]
    b="ASSOC:"+ (e["siren_siret"] if e["siren_siret"] else textnorm(name))
    f="FUNDING:"+textnorm(origin)
    G.add_node(b,type="recipient",label=name)
    G.add_node(f,type="funder_or_program",label=origin)
    G.add_edge(b,f,relationship="grant_row",amount=amt,amount_field=e["amount_field"],source=e["evidence_url"],dataset=e["dataset"])

simple=nx.Graph(G)
if simple.number_of_nodes():
    communities=list(nx.community.louvain_communities(simple,seed=42)) if simple.number_of_edges() else [set(simple)]
    commid={n:i for i,c in enumerate(communities) for n in c}
    central=nx.betweenness_centrality(simple,k=min(100,len(simple)),seed=42) if simple.number_of_nodes()>2 else {}
else: communities=[];commid={};central={}
nodes=[{"id":str(n),"type":d.get("type",""),"label":d.get("label",""),"community":commid.get(n,-1),
        "degree":simple.degree(n),"betweenness":round(central.get(n,0),7)} for n,d in simple.nodes(data=True)]
edges=[{"source":u,"target":v,"relationship":d.get("relationship",""),"amount":d.get("amount"),
        "amount_field":d.get("amount_field",""),"dataset":d.get("dataset",""),"year":d.get("year"),
        "evidence_url":d.get("source","")} for u,v,d in G.edges(data=True)]
save_csv("graph_nodes.csv",nodes,["id","type","label","community","degree","betweenness"])
save_csv("graph_edges.csv",edges,["source","target","relationship","amount","amount_field","dataset","year","evidence_url"])
repeats=[]
role_counts=collections.defaultdict(lambda:{"events":set(),"years":set(),"roles":set(),"urls":set()})
for e in events:
    for role,k in [("organiser","organises"),("arbiter","arbitrates")]:
        name=e.get(role,"").strip()
        if name:
            d=role_counts[(role,textnorm(name))]
            d["events"].add(e["ref"]);d["years"].add(e["reference_year_bucket"]);d["roles"].add(role);d["urls"].add(e["evidence_url"])
for (role,normalized),d in role_counts.items():
    if len(d["events"])>=2:
        repeats.append({"name":normalized,"role":role,"event_count":len(d["events"]),"year_buckets":",".join(map(str,sorted(d["years"]))),"sources":" | ".join(sorted(d["urls"]))})
repeats.sort(key=lambda x:(-x["event_count"],x["name"]))
save_csv("recurring_public_roles.csv",repeats,["name","role","event_count","year_buckets","sources"])
grouped=collections.defaultdict(list)
for e in grants:
    if e["amount"] is not None:
        grouped[(textnorm(e["beneficiary"]),e["amount_field"],e["dataset"])].append(e["amount"])
# no summing across distinct amount_field definitions or overlapping source tables.
totals=[{"beneficiary":k[0],"measure":k[1],"dataset":k[2],"rows":len(v),"sum":round(sum(v),2)} for k,v in grouped.items()]
totals.sort(key=lambda x:-abs(x["sum"]))
save_csv("amounts_by_entity_measure.csv",totals,["beneficiary","measure","dataset","rows","sum"])

summary={
 "generated_utc":datetime.now(timezone.utc).isoformat(),
 "method":"government full-annex plus bounded FFE tournament sample; separated graph layers",
 "public_state_rows_parsed":len(rows),
 "government_state_chess_matched_rows":len(chess_rows),
 "local_related_grant_measures":len(grants)-len(chess_rows),
 "number_funding_measure_rows":len(grants),
 "sampled_ffe_reference_pages_attempted":len(seen_ref),
 "ffe_events_with_public_organizer_or_arbitrator":len(events),
 "graph_nodes":len(nodes),"graph_edges":len(edges),
 "louvain_communities":len(communities),
 "recurring_public_roles":len(repeats),
 "most_central_nodes":sorted(nodes,key=lambda x:-x["betweenness"])[:30],
 "recurring_roles_top":repeats[:40],
 "top_beneficiaries_by_field":totals[:35],
 "source_manifest_count":len(manifest),
 "successful_source_fetches":sum(x["status"]=="ok" for x in manifest),
 "failed_source_fetches":sum(x["status"]!="ok" for x in manifest),
 "limitations":[
  "The first public state dataset is not all public/private flows; financial measures must not be summed across fields.",
  "Random samples of numbered FFE event pages are not a complete national tournament census, so frequency is not national prevalence.",
  "Shared names without a common identifier are not proof of identity or family ties.",
  "Club and state financial entities are not joined to an event organizer without a reliable identifier.",
  "Event participation data and minor player profiles deliberately excluded."
 ]}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT/"source_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT/"limitations.txt").write_text("\n".join(summary["limitations"]+warnings[:1000]),encoding="utf-8")
nx.write_graphml(simple,OUT/"network.graphml")
print(json.dumps({k:v for k,v in summary.items() if not isinstance(v,list)},ensure_ascii=False,indent=2))
