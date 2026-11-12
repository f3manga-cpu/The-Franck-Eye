#!/usr/bin/env python3
"""Publish original, pre-written editorial stories to GTA GitHub Pages.

Explicitly no crypto issuance, trading, keys, audience simulation, or social API writes.
Use --publish to write due stories and --push for authenticated git publication.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from html import escape
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
QUEUE = HERE / "content_queue.json"
OUT = REPO / "docs" / "gta"
PUBLIC = "https://f3manga-cpu.github.io/The-Franck-Eye/gta/"
CET = ZoneInfo("Europe/Paris")

STYLE = """
:root{color-scheme:dark;--ink:#eaf4f8;--muted:#92aab5;--cyan:#75d9d2;--orange:#ff9c55;--edge:#315166}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 75% 0%,#174355 0%,#071521 48%,#040b12 100%);color:var(--ink);font:16px/1.65 system-ui,-apple-system,'Segoe UI',sans-serif}
a{color:var(--cyan);text-underline-offset:3px}
.wrap{width:min(100% - 38px,1040px);margin:auto}
nav{display:flex;align-items:center;justify-content:space-between;padding:24px 0;border-bottom:1px solid var(--edge);gap:16px;flex-wrap:wrap}
.brand{font-weight:900;letter-spacing:.11em;color:#f5ffff;text-decoration:none;font-size:1.05rem}
.navtag{font:700 .7rem/1.4 system-ui;letter-spacing:.12em;color:var(--orange);border:1px solid #a96642;padding:7px 10px}
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:26px;align-items:center;padding:75px 0 50px}
.eyebrow{font-size:.75rem;font-weight:700;letter-spacing:.19em;text-transform:uppercase;color:var(--cyan)}
h1{font-size:clamp(3rem,8vw,6.6rem);line-height:.97;letter-spacing:-.075em;text-transform:uppercase;margin:12px 0 30px;font-weight:950}
h2{font-size:clamp(1.7rem,4vw,2.75rem);line-height:1.2;letter-spacing:-.045em}
.dek{font-size:clamp(1rem,2vw,1.22rem);color:#c9d8e0;max-width:650px}
.logo{width:min(100%,440px);filter:drop-shadow(0 12px 55px #20bac24b);border-radius:50%}
.line{height:2px;background:linear-gradient(to right,transparent,var(--cyan),var(--orange),transparent)}
.card{padding:27px;border:1px solid var(--edge);background:#081f2bc9;border-radius:8px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding:15px 0 55px}
.card h3{font-size:1.55rem;line-height:1.22;margin:.3rem 0 .75rem}
.meta{font:700 .73rem/1.5 system-ui;letter-spacing:.1em;color:var(--orange);text-transform:uppercase}
p{margin:1rem 0} .card p{color:var(--muted)}
.btn{display:inline-block;background:var(--cyan);padding:10px 20px;color:#03252d;text-decoration:none;font-weight:850;border-radius:4px}
.article{width:min(100%,710px);margin:50px auto 95px}
.article h1{font-size:clamp(2.5rem,6vw,4.4rem);letter-spacing:-.05em}
.article p{font-size:1.12rem;margin:1.4em 0}
.callout{border-left:3px solid var(--orange);padding:10px 22px;color:#c3d5dc;background:#0b2632}
footer{border-top:1px solid var(--edge);padding:25px 0 45px;color:var(--muted);font-size:.83rem}
@media(max-width:700px){.hero{grid-template-columns:1fr;padding:48px 0 28px;text-align:left}.logo{width:min(100%,260px);margin:auto}.grid{grid-template-columns:1fr}}
"""

def x(s):
    return escape(str(s), quote=True)

def validate_story(story):
    assert set(("slug","when","category","title","dek","body","social")).issubset(story), "missing fields"
    assert story["slug"].startswith("signal-") and story["slug"].replace("signal-","").isdigit(), "invalid slug"
    dt = datetime.fromisoformat(story["when"])
    assert dt.tzinfo is not None
    assert len(story["body"]) >= 2
    return dt

def due_stories(now: datetime):
    entries = json.loads(QUEUE.read_text(encoding="utf8"))["stories"]
    if now.tzinfo is None: raise ValueError("now must be timezone-aware")
    for e in entries: validate_story(e)
    slugs=[e["slug"] for e in entries]
    assert len(slugs)==len(set(slugs)), "duplicate slugs"
    return sorted([e for e in entries if datetime.fromisoformat(e["when"]) <= now], key=lambda e:e["when"])

def shell(content: str):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071521"><title>{x(content[:78])}</title><meta name="description" content="Original fictional dispatches from Greatest Token Action. Independent of every game publisher."><style>{STYLE}</style></head><body><div class="wrap"><nav><a class="brand" href="{PUBLIC}">GTA // GREATEST TOKEN ACTION</a><span class="navtag">INDEPENDENT FICTION · NO LIVE TOKEN</span></nav>'

COMMUNITY = "https://github.com/f3manga-cpu/The-Franck-Eye/issues/9"

def footer():
    return '<footer>Greatest Token Action is an independent fictional editorial project. Not affiliated with Rockstar Games, Grand Theft Auto, or any game publisher. No live coin has been issued. No investment solicitation, financial advice or promised returns.</footer></div></body></html>'

def article_page(e):
    dt=datetime.fromisoformat(e["when"]).astimezone(CET)
    para="".join(f"<p>{x(p)}</p>" for p in e["body"])
    return shell(e["title"]+" — Greatest Token Action")+f'<main class="article"><div class="meta">{x(e["category"])} · {dt:%d %b %Y} · {x(e["slug"].upper())}</div><h1>{x(e["title"])}</h1><div class="dek">{x(e["dek"])}</div><div class="line" style="margin:33px 0"></div>{para}<div class="callout">Fictional characters ARCH and SABLE. Independent original story. The token has not been launched.</div><p><a href="{COMMUNITY}">Suggest an original scene (GitHub account required)</a></p><p><a href="{PUBLIC}">← All transmissions</a></p></main>'+footer()

def index_page(stories):
    entries=''.join('<article class="card"><div class="meta">'+x(e["category"])+' · '+x(e["when"][:10])+'</div><h3>'+x(e["title"])+'</h3><p>'+x(e["dek"])+'</p><a href="'+x(e["slug"])+'.html">Read transmission</a></article>' for e in reversed(stories))
    return shell("GTA — Greatest Token Action")+f'''<main><section class="hero"><div><div class="eyebrow">INDEPENDENT GAMING-CULTURE FICTION // SIGNAL ACTIVE</div><h1>GREATEST<br>TOKEN<br><span style="color:var(--orange)">ACTION.</span></h1><p class="dek">A faceless fictional news network. Original characters. One new city built in public, one transmission at a time.</p><p><a class="btn" href="#dispatches">READ THE DISPATCHES</a></p></div><img class="logo" src="../gta-staging/logo.png" width="440" height="440" alt="Greatest Token Action original emblem"></section><div class="line"></div><section id="dispatches"><div class="eyebrow" style="padding-top:38px">THE NEWSROOM</div><h2>Transmissions</h2><div class="grid">{entries}</div></section><section class="card" style="margin-bottom:55px"><div class="meta">TRANSPARENCY</div><h2>What is real?</h2><p>These are original fictional broadcasts by two recurring characters: ARCH (anchor) and SABLE (field reporter). The website and published stories are real. A public GTA token is not yet live. No partnerships, investments, user counts or future earnings are claimed.</p><p><a class="btn" href="{COMMUNITY}">SUGGEST A SCENE</a> <small>— GitHub sign-in required</small></p></section></main>'''+footer()

def write(stories):
    OUT.mkdir(parents=True,exist_ok=True)
    for e in stories: (OUT/(e["slug"]+".html")).write_text(article_page(e),encoding="utf8")
    (OUT/"index.html").write_text(index_page(stories),encoding="utf8")
    (OUT/"published.json").write_text(json.dumps({"project":"Greatest Token Action","source":"site publisher","coin_launched":False,"stories":[{"slug":e["slug"],"title":e["title"],"date":e["when"],"url":PUBLIC+e["slug"]+".html"} for e in stories]},indent=2)+"\n",encoding="utf8")

def run_git(command):
    return subprocess.run(["git",*command],cwd=REPO,text=True,capture_output=True,check=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--publish",action="store_true")
    parser.add_argument("--push",action="store_true")
    parser.add_argument("--at",help="Test date, offset-aware ISO8601")
    args=parser.parse_args()
    if args.push and not args.publish: parser.error("--push requires --publish")
    now=datetime.fromisoformat(args.at) if args.at else datetime.now(CET)
    stories=due_stories(now)
    print(json.dumps({"at":now.isoformat(),"due":[e["slug"] for e in stories],"action":"publish" if args.publish else "preview","coin_launched":False},indent=2))
    if not args.publish: return
    if not stories: return
    if args.push:
        run_git(["pull","--ff-only","origin","main"])
    write(stories)
    if args.push:
        # Commit only these vetted public story assets. Never touch unrelated private files.
        run_git(["add","docs/gta/"])
        status=run_git(["diff","--cached","--name-only"]).stdout
        if not status.strip():
            print("ALREADY_PUBLISHED_NO_CHANGES"); return
        expected={f"docs/gta/{e['slug']}.html" for e in stories}|{"docs/gta/index.html","docs/gta/published.json"}
        if not all(row in expected for row in status.strip().splitlines()):
            raise RuntimeError("Unexpected staged file: refusing to push")
        run_git(["commit","-m",f"gta-editorial: publish {len(stories)} due original dispatches"])
        pushed=run_git(["push","origin","HEAD:main"])
        print("GIT_PUSH_CONFIRMED",pushed.stderr.strip()[-400:])
    else: print("WRITTEN_LOCALLY_NOT_PUBLISHED_TO_GITHUB")

if __name__=="__main__": main()
