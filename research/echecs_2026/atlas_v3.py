import requests,re,csv,json,random,os,time,collections,unicodedata,math,hashlib
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,date,timezone
from pathlib import Path
import networkx as nx

OUT=Path("research/echecs_2026/atlas_v3/results");OUT.mkdir(parents=True,exist_ok=True)
BASE="https://www.echecs.asso.fr/"
DEPTS=[f"{i:02d}" for i in range(1,96)]+["2A","2B","971","972","973","974","976"]
ANCHORS={72269,67722,67723,67717,67718,67719,67720,67721,72264,72265,72266,72267,72268,72270,70779,66882,70947,72295,67714,67715,67716}
def norm(s):
 s=unicodedata.normalize("NFKD",str(s or ""))
 return re.sub(r"[^A-Z0-9]+"," ","".join(c for c in s.upper() if not unicodedata.combining(c))).strip()
def get(url,timeout=25):
 for attempt in range(2):
  try:
   r=requests.get(url,timeout=timeout,headers={"User-Agent":"FFEHistoricalPublicGraphResearch/1.0"})
   if r.status_code==200:return r.text
   if r.status_code in [403,404]:break
  except Exception:pass
  time.sleep(.7)
 return None
def write(name,rows,fields):
 with (OUT/name).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
errors=[];sources=[]
def idx(dep):
 url=BASE+"ListeTournois.aspx?Action=TOURNOICOMITE&ComiteRef="+dep
 html=get(url)
 if not html:errors.append("index "+dep);return []
 soup=BeautifulSoup(html,"html.parser");res=[]
 for tr in soup.select("tr"):
  td=tr.find_all("td",recursive=False)
  if len(td)<5:continue
  val=[x.get_text(" ",strip=True) for x in td]
  if not re.fullmatch(r"\d{5,6}",val[0]):continue
  link=tr.select_one('a[href*="FicheTournoi.aspx?Ref="]')
  if not link:continue
  res.append(dict(ref=int(val[0]),town=val[1],dept=val[2],title=val[3],date_short=val[4],source=url))
 sources.append(dict(url=url,rows=len(res),sha256=hashlib.sha256(html.encode()).hexdigest()))
 return res
with ThreadPoolExecutor(max_workers=5) as ex:
 records=[a for fut in as_completed([ex.submit(idx,d) for d in DEPTS]) for a in fut.result()]
known={e["ref"]:e for e in records}
for ref in ANCHORS:known.setdefault(ref,dict(ref=ref,town="",dept="",title="Tournoi FFE "+str(ref),date_short="",source=""))
write("national_index_first_pages.csv",list(known.values()),["ref","town","dept","title","date_short","source"])
print("INDEX",len(records),len(known),flush=True)

random.seed(20261101)
entries=list(known.values())
high=lambda d:any(z in norm(d["title"]) for z in ["NATIONAL","CHAMPIONNAT DE FRANCE","TROPHEE","VICHY","MARINA VIVA","PORTICCIO","VANDOEUVRE","AIX","INTERNATIONAL","CAP D AGDE"])
entries.sort(key=lambda d:(0 if d["ref"] in ANCHORS else 1 if high(d) else 2,-d["ref"]))
count=int(os.getenv("ATLAS_EVENTS","360"))
sel=entries[:min(count*3//4,len(entries))]
remaining=entries[len(sel):];random.shuffle(remaining);sel=(sel+remaining[:max(0,count-len(sel))])[:count]
def event(i):
 ref=i["ref"];url=BASE+f"FicheTournoi.aspx?Ref={ref}"
 html=get(url)
 if not html:return None
 soup=BeautifulSoup(html,"html.parser")
 for t in soup(["script","style","noscript"]):t.decompose()
 txt=soup.get_text(" ",strip=True)
 def field(k):
  match=re.search(r"\b"+k+r"\s*:\s*(.*?)(?=\s+(?:Prise en compte|Homologu|Nombre de rondes|Cadence|Appariements|Organisateur|Arbitre|Dates|Inscription Senior|Inscription Jeunes|Télécharger les parties|Joueurs\s*\|)|$)",txt,re.I)
  return match.group(1).strip() if match else ""
 dates=field("Dates")
 years=re.findall(r"\b20\d{2}\b",dates)
 if not years:return None
 year=int(years[0])
 if not 2022<=year<=2026:return None
 mon={"JANVIER":1,"FEVRIER":2,"MARS":3,"AVRIL":4,"MAI":5,"JUIN":6,"JUILLET":7,"AOUT":8,"SEPTEMBRE":9,"OCTOBRE":10,"NOVEMBRE":11,"DECEMBRE":12}
 match=re.search(r"(\d{1,2})\s+([A-Za-zéûôîèà]+)\s+(20\d{2})",dates)
 day=""
 if match:
  try:day=date(int(match.group(3)),mon[norm(match.group(2))],int(match.group(1))).isoformat()
  except:pass
 if day and day>"2026-11-01":return None
 return dict(**i,year=year,date=day,date_text=dates,organizer=field("Organisateur"),arbiter=field("Arbitre"),rounds=field("Nombre de rondes"),url=url)
with ThreadPoolExecutor(max_workers=6) as ex:
 events=[v for fut in as_completed([ex.submit(event,e) for e in sel]) if (v:=fut.result())]
events.sort(key=lambda x:(x["date"],x["ref"]))
print("EVENTS",len(events),flush=True)
write("events.csv",events,["ref","title","town","dept","year","date","date_text","organizer","arbiter","rounds","url","source","date_short"])
event_by_id={e["ref"]:e for e in events}

# Exclude youth categories from named longitudinal tracking, except the two adult grandmasters explicitly studied.
def roster(e):
 ref=e["ref"];url=BASE+f"Resultats.aspx?URL=Tournois/Id/{ref}/{ref}&Action=Ls"
 html=get(url,35);records=[];clubs=collections.Counter();total=0
 if html:
  soup=BeautifulSoup(html,"html.parser")
  for tr in soup.select("tr.papi_liste_f,tr.papi_liste_c"):
   t=[x.get_text(" ",strip=True) for x in tr.find_all("td",recursive=False)]
   if len(t)<8 or not t[0].isdigit():continue
   total+=1;name=t[2];cat=t[4];club=t[7];clubs[club]+=1
   if cat.lower().startswith(("sen","vet")) or norm(name) in {"FRESSINET LAURENT","MAURIZZI MARC ANDRIA"}:
    records.append(dict(ref=ref,name=name,key=norm(name),category=cat,club=club,club_key=norm(club),league=t[6],elo=t[3],source=url))
 return dict(ref=ref,players=records,clubs=dict(clubs),total=total,source=url)

ordered=sorted(events,key=lambda e:(0 if e["ref"] in ANCHORS else 1 if high(e) else 2,e["year"],e["ref"]))
rnum=int(os.getenv("ATLAS_ROSTERS","135"))
with ThreadPoolExecutor(max_workers=6) as ex:
 rosters=[f.result() for f in as_completed([ex.submit(roster,e) for e in ordered[:rnum]])]
players=[p for r in rosters for p in r["players"]]
delegations=[dict(ref=r["ref"],club=c,club_key=norm(c),count=n,source=r["source"]) for r in rosters for c,n in r["clubs"].items()]
write("adult_public_participations.csv",players,["ref","name","key","category","club","club_key","league","elo","source"])
write("club_delegations.csv",delegations,["ref","club","club_key","count","source"])
print("ROSTERS",len(rosters),"PARTICIPATIONS",len(players),"DELEGATIONS",len(delegations),flush=True)

G=nx.Graph();presence=collections.defaultdict(set)
for e in events:
 eid="EVENT:"+str(e["ref"]);G.add_node(eid,type="event",label=e["title"],year=e["year"])
 for kind,col in [("organizer","organizer"),("arbiter","arbiter")]:
  if e[col]:
   k=kind.upper()+":"+norm(e[col]);G.add_node(k,type=kind,label=e[col]);G.add_edge(eid,k,relation=kind,source=e["url"]);presence[k].add(e["ref"])
for p in players:
 eid="EVENT:"+str(p["ref"]);k="PERSON:"+p["key"]
 G.add_node(k,type="adult_player",label=p["name"]);G.add_edge(eid,k,relation="participant",source=p["source"]);presence[k].add(p["ref"])
for d in delegations:
 eid="EVENT:"+str(d["ref"]);k="CLUB:"+d["club_key"]
 G.add_node(k,type="club",label=d["club"]);G.add_edge(eid,k,relation="club_delegation",source=d["source"]);presence[k].add(d["ref"])
at_event=collections.defaultdict(set)
for actor,refs in presence.items():
 for ref in refs:at_event[ref].add(actor)
pairs=collections.defaultdict(set)
for ref,members in at_event.items():
 adults=sorted(x for x in members if x.startswith("PERSON:"))
 roles=sorted(x for x in members if x.startswith("ARBITER:") or x.startswith("ORGANIZER:"))
 clubs=sorted(x for x in members if x.startswith("CLUB:"))
 for j,a in enumerate(adults):
  for b in adults[j+1:j+24]+roles[:5]+clubs[:8]:pairs[tuple(sorted((a,b)))].add(ref)
 for i,a in enumerate(roles):
  for b in roles[i+1:]+clubs[:10]:pairs[tuple(sorted((a,b)))].add(ref)
repeat=[]
for (a,b),refs in pairs.items():
 if len(refs)<2:continue
 yrs=sorted(set(event_by_id[r]["year"] for r in refs if r in event_by_id))
 repeat.append(dict(a=a,b=b,n=len(refs),years=yrs,refs=sorted(refs)))
repeat.sort(key=lambda x:-x["n"])
write("coappearances_repeated.csv",[dict(a=x["a"],b=x["b"],n=x["n"],years=",".join(map(str,x["years"])),refs=",".join(map(str,x["refs"]))) for x in repeat],["a","b","n","years","refs"])
P=nx.Graph()
for r in repeat:P.add_edge(r["a"],r["b"],weight=r["n"])
clusters=[]
if P.number_of_edges():
 for i,community in enumerate(nx.community.louvain_communities(P,seed=42,weight="weight")):
  if len(community)<3:continue
  sub=P.subgraph(community)
  members=sorted([dict(id=u,label=G.nodes[u].get("label",u),type=G.nodes[u].get("type",""),links=sub.degree(u)) for u in community],key=lambda x:-x["links"])
  clusters.append(dict(id=i,size=len(community),edges=sub.number_of_edges(),members=members[:80]))
clusters.sort(key=lambda x:-x["size"])
funding=[]
f=Path("research/echecs_2026/state_results/chess_beneficiaries_2023.csv")
if f.exists():
 with f.open(encoding="utf-8-sig",newline="") as fh:
  for x in csv.DictReader(fh):
   name=x.get("Dénomination","")
   if not re.search(r"\b(?:ECHECS|ECHIQUIER|CHESS)\b",norm(name)) or re.search(r"CHESS BOXING|ECHEC SCOLAIRE",norm(name)):continue
   try:amt=float(x["Montant"])
   except:continue
   funding.append(dict(siren=x.get("SIREN"),name=name,program=x.get("Programme"),amount=amt,year=2023))
summary=dict(generated=datetime.now(timezone.utc).isoformat(),departments=len(DEPTS),index_tournaments=len(known),metadata_events=len(events),roster_pages=len(rosters),rosters_with_players=sum(r["total"]>0 for r in rosters),roster_total_participants_aggregated=sum(r["total"] for r in rosters),named_adult_participations=len(players),distinct_adult_names=len(set(p["key"] for p in players)),club_delegations=len(delegations),repeated_pairs=len(repeat),clusters=len(clusters),graph_nodes=G.number_of_nodes(),graph_edges=G.number_of_edges(),funding_records=len(funding),important_limitation="Tournament department indexes: first page only, NOT full archive. Roster coverage is a targeted subset. No evidence of private relationship from coattendance.",errors=errors)
for name,obj in [("summary.json",summary),("events.json",events),("players.json",players),("delegations.json",delegations),("coappearances.json",repeat[:3500]),("communities.json",clusters),("funding.json",funding),("source_manifest.json",sources)]:
 (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
nx.write_graphml(G,OUT/"typed_evidence_graph.graphml")
print("SUMMARY",json.dumps(summary,ensure_ascii=False),flush=True)
