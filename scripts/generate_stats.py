#!/usr/bin/env python3
"""Generate Graphite SVG stats from publicly accessible GitHub repository data."""
import json, os, urllib.request, urllib.parse, html
from pathlib import Path
from datetime import datetime, timezone

USER = os.environ.get('GH_USERNAME', 'Shivanshu-06')
TOKEN = os.environ.get('GH_TOKEN', '')
OUT = Path(__file__).resolve().parents[1] / 'assets' / 'stats'
OUT.mkdir(parents=True, exist_ok=True)

def get(url):
    headers={'Accept':'application/vnd.github+json','User-Agent':'graphite-profile-stats','X-GitHub-Api-Version':'2022-11-28'}
    if TOKEN: headers['Authorization']='Bearer '+TOKEN
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)

def esc(s): return html.escape(str(s),quote=True)

def svg(width,height,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>GitHub public repository statistics</title><style>text{{font-family:Arial,Helvetica,sans-serif}}.muted{{fill:#999da5}}.white{{fill:#f0f0f1}}@media(prefers-reduced-motion:no-preference){{.pulse{{animation:pulse 2.5s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.3}}}}}}</style><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" fill="#202124" stroke="#3a3b3f"/>{body}</svg>'''

def txt(x,y,s,size=15,cls='white',weight='normal'):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" font-weight="{weight}">{esc(s)}</text>'

def main():
    repos=[]
    for page in range(1,11):
        chunk=get(f'https://api.github.com/users/{urllib.parse.quote(USER)}/repos?per_page=100&page={page}&type=owner')
        repos.extend(chunk)
        if len(chunk)<100: break
    repos=[r for r in repos if not r.get('fork') and not r.get('private')]
    stars=sum(r.get('stargazers_count',0) for r in repos)
    forks=sum(r.get('forks_count',0) for r in repos)
    counts={}
    # GitHub language field is the primary language of each public non-fork repository.
    for r in repos:
        language=r.get('language')
        if language: counts[language]=counts.get(language,0)+1
    counts=sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]))
    updated=datetime.now(timezone.utc).strftime('%d %b %Y UTC')
    b=txt(30,41,'PUBLIC REPOSITORY OVERVIEW',14,'white','bold')+'<circle class="pulse" cx="562" cy="35" r="5" fill="#dedee0"/>'
    for x,val,label in [(30,len(repos),'Repositories'),(220,stars,'Stars received'),(410,forks,'Forks received')]:
        b+=txt(x,111,val,38,'white','bold')+txt(x,138,label,13,'muted')
    b+=txt(30,182,'Public, non-fork repositories only',12,'muted')+txt(30,205,'Updated '+updated,11,'muted')
    (OUT/'overview.svg').write_text(svg(600,230,b),encoding='utf-8')
    palette=['#eeeeef','#c8c9cc','#a2a5aa','#7f8389','#60656d','#484b52']
    total=sum(v for _,v in counts)
    b=txt(30,41,'PRIMARY REPOSITORY LANGUAGES',14,'white','bold')
    if not counts:
        b+=txt(30,98,'No public repository language data',15,'muted')
    else:
        x=30
        for i,(name,n) in enumerate(counts[:6]):
            w=540*n/total if total else 0
            b+=f'<rect x="{x:.1f}" y="63" width="{max(0,w-2):.1f}" height="14" rx="2" fill="{palette[i]}"/>'
            x+=w
        for i,(name,n) in enumerate(counts[:5]):
            col=i%2; row=i//2
            xx=30+col*275; yy=110+row*28
            b+=f'<rect x="{xx}" y="{yy-10}" width="9" height="9" rx="2" fill="{palette[i]}"/>'
            b+=txt(xx+17,yy, f'{name} · {n} repo'+('s' if n!=1 else ''),13,'white')
    b+=txt(30,212,'Based on each repository’s primary language',11,'muted')
    (OUT/'languages.svg').write_text(svg(600,230,b),encoding='utf-8')
    print(f'Generated stats for {USER}: {len(repos)} public non-fork repositories')

if __name__=='__main__': main()
