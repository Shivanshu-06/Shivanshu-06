#!/usr/bin/env python3
"""Generate self-hosted, light-theme GitHub profile statistics from public repositories."""
import json
import os
import urllib.request
import urllib.parse
import html
from pathlib import Path
from datetime import datetime, timezone

USER = os.environ.get("GH_USERNAME", "Shivanshu-06")
TOKEN = os.environ.get("GH_TOKEN", "")
OUT = Path(__file__).resolve().parents[1] / "assets" / "stats"
OUT.mkdir(parents=True, exist_ok=True)

def get(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "shiv-profile-stats", "X-GitHub-Api-Version": "2022-11-28"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
        return json.load(response)

def esc(value):
    return html.escape(str(value), quote=True)

def text(x, y, value, size=16, color="#534F4B", weight=400):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(value)}</text>'

def svg(body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="230" viewBox="0 0 600 230" role="img"><rect x="1" y="1" width="598" height="228" rx="17" fill="#FFFCF6" stroke="#D8E3D4" stroke-width="2"/>{body}</svg>"""

def main():
    repos = []
    for page in range(1, 11):
        chunk = get(f"https://api.github.com/users/{urllib.parse.quote(USER)}/repos?per_page=100&page={page}&type=owner")
        repos.extend(chunk)
        if len(chunk) < 100:
            break
    repos = [repo for repo in repos if not repo.get("fork") and not repo.get("private")]
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    forks = sum(repo.get("forks_count", 0) for repo in repos)
    updated = datetime.now(timezone.utc).strftime("%d %b %Y UTC")

    body = text(28, 45, "GITHUB · PUBLIC REPOSITORIES", 16, "#466E5C", 700)
    body += '<rect x="28" y="60" width="544" height="1" fill="#E1E8DD"/>'
    for x, value, label in [(30, len(repos), "Repositories"), (218, stars, "Stars"), (406, forks, "Forks")]:
        body += f'<rect x="{x-8}" y="78" width="167" height="98" rx="11" fill="#F0F5ED"/>'
        body += text(x+10, 122, value, 34, "#476F5A", 700)
        body += text(x+10, 150, label, 13, "#746C61", 500)
    body += text(30, 198, "Public, non-fork repositories only", 12, "#746C61")
    body += text(30, 216, "Updated " + updated, 11, "#978C7D")
    (OUT / "overview.svg").write_text(svg(body), encoding="utf-8")

    counts = {}
    for repo in repos:
        language = repo.get("language")
        if language:
            counts[language] = counts.get(language, 0) + 1
    sorted_langs = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    total = sum(counts.values())
    body = text(28, 45, "PRIMARY REPOSITORY LANGUAGES", 16, "#466E5C", 700)
    body += '<rect x="28" y="60" width="544" height="1" fill="#E1E8DD"/>'
    palette = ["#4E8E77", "#78AD99", "#A5C9B4", "#B5A0C8", "#D3B68F", "#E4C8BE"]
    x = 28
    for index, (lang, count) in enumerate(sorted_langs[:6]):
        width = (544 * count / total) if total else 0
        body += f'<rect x="{x:.1f}" y="81" width="{max(width-2, 0):.1f}" height="16" rx="3" fill="{palette[index]}"/>'
        x += width
        col = index % 2
        row = index // 2
        lx = 28 + col * 276
        ly = 127 + row * 29
        body += f'<rect x="{lx}" y="{ly-12}" width="11" height="11" rx="2" fill="{palette[index]}"/>'
        body += text(lx+19, ly, f"{lang} · {count} repositories", 13)
    if not sorted_langs:
        body += text(28, 118, "No public repository language data", 14)
    body += text(28, 213, "Based on each repository's primary language", 11, "#978C7D")
    (OUT / "languages.svg").write_text(svg(body), encoding="utf-8")
    print(f"Generated public statistics: {len(repos)} repositories")

if __name__ == "__main__":
    main()
