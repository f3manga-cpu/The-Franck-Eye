import requests, csv, io, json, unicodedata, re
from collections import defaultdict
from pathlib import Path
OUT=Path("research/echecs_2026/state_results"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf25-donnees-de-l-annexe-jaune-effort-financier-de-l-etat-en-faveur-des-associations/exports/csv?use_labels=true"
r=requests.get(URL,timeout=150);r.raise_for_status()
data=r.content.decode("utf-8-sig")
(OUT/"download_sha256.txt").write_text(__import__('hashlib').sha256(r.content).hexdigest())
try: dialect=csv.Sniffer().sniff(data[:10000],delimiters=";,\t")
except: dialect=csv.excel
rows=list(csv.DictReader(io.StringIO(data),dialect=dialect))
def normalize(s):
    s=unicodedata.normalize("NFKD",str(s or ''))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()
matches=[]
for row in rows:
    name=normalize(row.get('denomination') or row.get('Dénomination') or '')
    if re.search(r'\bechecs\b|\bechiquier\b|\bchess\b|\bechiqueen',name) and not re.search(r'chess\s*boxing|echec\s*scolaire',name):
        matches.append(row)
with (OUT/"chess_beneficiaries_2023.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore");w.writeheader();w.writerows(matches)
g=defaultdict(lambda:{"rows":0,"total_euros":0,"programmes":set(),"names":set()})
for row in matches:
    siren=row.get("siren") or row.get("SIREN") or ""
    name=row.get("denomination") or row.get("Dénomination") or ""
    key=siren if re.fullmatch(r"\d{9}",siren) else "NAME:"+normalize(name)
    a=float(str(row.get("montant") or row.get("Montant") or "0").replace(',','.'))
    g[key]["rows"]+=1;g[key]["total_euros"]+=a;g[key]["programmes"].add(str(row.get("programme") or row.get("Programme") or ""));g[key]["names"].add(name)
top=[{"siren_or_name":k,"name":" / ".join(sorted(v["names"])),"rows":v["rows"],"total_euros":round(v["total_euros"],2),"programmes":sorted(v["programmes"])} for k,v in g.items()]
top.sort(key=lambda x:-x["total_euros"])
program_totals=defaultdict(float)
for row in matches:
    program_totals[str(row.get("Programme") or row.get("programme") or "non_identifie")]+=float(str(row.get("Montant") or row.get("montant") or "0").replace(',','.'))
summary={"totals_by_state_budget_program":dict(sorted(program_totals.items(),key=lambda kv:-kv[1])),"raw_rows":len(rows),"chess_matched_rows":len(matches),"unique_chess_beneficiaries":len(top),"sum_matched_euros_2023":round(sum(v["total_euros"] for v in g.values()),2),"top":top[:100],"source_url":URL,"underlying_year_of_payments":2023,"publication":2024,"warning":"Text match on beneficiary denomination only. Not a complete FFE sector total; excludes multisport clubs with no chess term."}
(OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in summary.items() if k!="top"},ensure_ascii=False))
