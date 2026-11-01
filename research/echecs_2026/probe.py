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

print("PAGER START")
s=bs4.BeautifulSoup(requests.get(urls["committee"],timeout=25).text,"html.parser")
for a in s.find_all('a',href=True):
  href=a.get("href","")
  if "__doPostBack" in href or "Page" in href or "ListeTournois" in href:
    print("PAGER",repr(a.get_text(' ',strip=True)),repr(href[:200]))
for hidden in s.select('input[type="hidden"]'):
  print("HIDDEN",hidden.get("name"),len(str(hidden.get("value",""))))

print("PAGER_POST")
session=requests.Session();resp=session.get(urls["committee"],timeout=25)
soup=bs4.BeautifulSoup(resp.text,'html.parser')
data={x.get("name"):x.get("value","") for x in soup.select('input[name]') if x.get("name")}
data.update({"__EVENTTARGET":"ctl00$ContentPlaceHolderMain$PagerHeader","__EVENTARGUMENT":"2"})
try:
 rr=session.post(urls["committee"],data=data,timeout=35)
 ss=bs4.BeautifulSoup(rr.text,'html.parser')
 entries=[(tr.find_all('td',recursive=False)[0].get_text(' ',strip=True),tr.get_text(' ',strip=True)[:85]) for tr in ss.select('tr') if len(tr.find_all('td',recursive=False))>=5 and re.fullmatch(r"\d{5,6}",tr.find_all('td',recursive=False)[0].get_text(' ',strip=True))]
 print("PAGER_POST_STATUS",rr.status_code,len(rr.content),"FIRST",entries[:3],"LAST",entries[-3:],"TOTAL",len(entries))
except Exception as e:print("PAGER_POST_ERROR",repr(e))
