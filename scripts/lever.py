"""More Lever companies for data/own/lever.json (jobs.lever.co blocks Common Crawl's crawler, so harvest.py finds few).

Two public sources, every find checked against Lever's public postings API (200 = the board exists) before it is kept:
  1. the Internet Archive's URL index for jobs.lever.co (pages archived since 2024)
  2. company names already in our other lists (companies move between job systems), each name asked once; the names
     already asked are kept in data/own/lever_asked.json so later runs only ask about new ones.

  python scripts/lever.py [max_names=15000]
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWN = os.path.join(ROOT, "data", "own")
UA = {"User-Agent": "vettra-jobs (public job lists; github.com/mirzamalikbaig/vettra-jobs)"}
SLUG = re.compile(r"jobs\.lever\.co(?::\d+)?/([A-Za-z0-9_.-]+)")


def read(name, default):
    path = os.path.join(OWN, name)
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else default


def has_board(slug):
    try:
        with urllib.request.urlopen(urllib.request.Request("https://api.lever.co/v0/postings/%s?limit=1&mode=json" % slug, headers=UA),
                                    timeout=20) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(30)
        return False
    except (OSError, ValueError):  # ValueError: a name that cannot be a web address
        return False


def archive_slugs(pages=40):
    """Lever company names in the Internet Archive's index, page by page (resume keys); stops quietly on any failure."""
    found, key = set(), ""
    for _ in range(pages):
        url = ("https://web.archive.org/cdx/search/cdx?url=jobs.lever.co/&matchType=prefix&fl=original&collapse=urlkey"
               "&from=2024&limit=20000&showResumeKey=true" + ("&resumeKey=" + urllib.request.quote(key) if key else ""))
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                lines = r.read().decode("utf-8", "replace").splitlines()
        except OSError as e:
            print("  archive index stopped: %s" % str(e)[:80])
            break
        key = lines[-1].strip() if len(lines) > 1 and lines[-2] == "" else ""
        found |= {m.group(1).lower() for l in lines for m in [SLUG.search(l)] if m}
        print("  archive index: %d names so far" % len(found))
        if not key:
            break
        time.sleep(2)
    return found - {"robots.txt", "favicon.ico", "sitemap.xml", "api"}


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
    lever = {x.lower() for x in read("lever.json", [])}
    asked = set(read("lever_asked.json", []))
    names = {x.lower() for s in ("greenhouse", "ashby", "bamboohr") for x in read(s + ".json", [])}
    names |= {x.split("|")[0] for x in read("workday.json", [])}
    names |= {re.sub(r"[^a-z0-9]", "", r["name"].lower()) for r in read("paylocity.json", []) if not re.match(r"[0-9a-f]{8}-", r["name"])}  # skip ids standing in for names
    todo = sorted(archive_slugs() - lever) + sorted(n for n in names - lever - asked if re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,59}", n))[:limit]
    print("asking Lever about %d names" % len(todo))
    with ThreadPoolExecutor(max_workers=4) as pool:  # the collector's own Lever worker count
        for slug, ok in zip(todo, pool.map(has_board, todo)):
            asked.add(slug)
            if ok:
                lever.add(slug)
    for name, rows in (("lever.json", sorted(lever)), ("lever_asked.json", sorted(asked))):
        with open(os.path.join(OWN, name), "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=0)
    print("lever: %d companies" % len(lever))


if __name__ == "__main__":
    main()
