import requests,bs4,re,json
urls={
"committee":"https://www.echecs.asso.fr/ListeTournois.aspx?Action=TOURNOICOMITE&ComiteRef=03",
"event":"https://www.echecs.asso.fr/FicheTournoi.aspx?Ref=72269",
"players":"https://www.echecs.asso.fr/Resultats.aspx?Action=Ls&URL=Tournois%2FId%2F72269%2F72269",
"classification":"https://www.echecs.asso.fr/Resultats.aspx?Action=Cl&URL=Tournois%2FId%2F72269%2F72269"}
for k,u in urls.items():
 try:
  r=requests.get(u,timeout=35)
  print("URL",k,r.status_code,len(r.content),r.url)
  soup=bs4.BeautifulSoup(r.text,'html.parser')
  links=[(a.get_text(" ",strip=True)[:80],a.get('href')) for a in soup.select('a[href]') if re.search("FicheTournoi|Resultats|FicheJoueur",a.get('href') or '',re.I)]
  print("LINKS",links[:12])
  trs=soup.find_all('tr')
  print("TABLES",len(soup.find_all('table')),"TRS",len(trs))
  sample=[]
  for tr in trs:
   cells=tr.find_all(['td','th'],recursive=False)
   c=[x.get_text(' ',strip=True)[:85] for x in cells]
   if len(c)>2 and (("FRESSINET" in str(c)) or ("MAURIZZI" in str(c)) or ("VICHY" in str(c)) or ("BACROT" in str(c)) or ("National" in str(c)) or "Club" in str(c) or "Nom" in str(c)):
    sample.append({"cells":c,"html":str(tr)[:500]})
  print("TR_EXAMPLES",json.dumps(sample[:7],ensure_ascii=False))
  print("TEXT_PREVIEW",soup.get_text(' ',strip=True)[-1600:])
 except Exception as e:print("ERROR",type(e).__name__,str(e))
