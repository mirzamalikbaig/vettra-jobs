"""Our own company lists, harvested from Common Crawl's public URL index (stage 4 in PLAN.md).

Common Crawl's CDX index is sorted by SURT key ("com,myworkdayjobs,nvidia.wd5)/..."), so every company page of one job
system sits in a few neighbouring blocks. cluster.idx (about 100 MB per crawl) says where each block of ~3,000 rows
starts; we fetch only the blocks for our job systems with HTTP Range requests from data.commoncrawl.org (not the busy
CDX server, which answers bulk queries with 504s). A crawl takes a few hundred small requests.

  python scripts/harvest.py [crawls=3]     writes data/own/<system>.json, merged with what earlier harvests found
"""
import bisect
import gzip
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "own")
BASE = "https://data.commoncrawl.org/"
UA = {"User-Agent": "vettra-jobs harvest (public job lists; github.com/mirzamalikbaig/vettra-jobs)"}

# system -> (SURT prefix, URL pattern whose first group is the company as the scraper wants it)
SYSTEMS = {
    "greenhouse": [("io,greenhouse,boards)/", r"//boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-z0-9_-]+)(?=[/?#&]|$)"),
                   ("io,greenhouse,job-boards)/", r"//job-boards\.greenhouse\.io/([a-z0-9_-]+)(?=[/?#&]|$)")],
    "lever": [("co,lever,jobs)/", r"//jobs\.lever\.co/([a-z0-9_.-]+)")],
    "ashby": [("com,ashbyhq,jobs)/", r"//jobs\.ashbyhq\.com/([a-z0-9_.%-]+)")],
    "bamboohr": [("com,bamboohr,", r"//([a-z0-9-]+)\.bamboohr\.com/(?:careers|jobs)")],
    "icims": [("com,icims,", r"//careers-([a-z0-9-]+)\.icims\.com/")],
    "workday": [("com,myworkdayjobs,", r"//([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([A-Za-z0-9_-]+)(?=[/?#&]|$)")],
    "paylocity": [("com,paylocity,recruiting)/recruiting/jobs/all/",
                   r"/Jobs/All/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:/([^/?#]+))?")],
}
# Path words that are pages of the job system, not companies.
NOT_COMPANY = {"embed", "api", "v1", "jobs", "job", "careers", "static", "assets", "favicon.ico", "robots.txt", "sitemap.xml",
               "login", "wday", "en-us", "privacy", "terms", "search", "apply", "job_app", "includes", "_next", "public"}


def get(path, rng=None, tries=4):
    for i in range(tries):
        try:
            h = dict(UA, Range="bytes=%d-%d" % rng) if rng else UA
            with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=h), timeout=120) as r:
                return r.read()
        except OSError as e:
            if i == tries - 1:
                raise
            print("  retry %s (%s)" % (path[-40:], str(e)[:60]))
            time.sleep(5 * (i + 1))


def crawls(n):
    with urllib.request.urlopen(urllib.request.Request("https://index.commoncrawl.org/collinfo.json", headers=UA), timeout=60) as r:
        return [c["id"] for c in json.load(r)[:n]]


def blocks(crawl, prefixes):
    """The cluster.idx blocks that can hold rows starting with any prefix: the one before the first match, and all matches."""
    idx = get("cc-index/collections/%s/indexes/cluster.idx" % crawl).decode("utf-8").splitlines()
    keys = [l.split(" ", 1)[0] for l in idx]
    want = set()
    for p in prefixes:
        i = max(bisect.bisect_left(keys, p) - 1, 0)
        while i < len(keys) and (keys[i] < p or keys[i].startswith(p)):
            want.add(i)
            i += 1
    return [idx[i].split("\t")[1:4] for i in sorted(want)]


def company(system, url):
    for prefix, pat in SYSTEMS[system]:
        m = re.search(pat, url, re.I)
        if not m:
            continue
        if system == "workday":
            tenant, wd, site = m.group(1).lower(), m.group(2).lower(), m.group(3)
            return None if site.lower() in NOT_COMPANY else "%s|%s|%s" % (tenant, wd, site)
        if system == "paylocity":
            return (m.group(1).lower(), urllib.parse.unquote(m.group(2) or "").replace("-", " ").strip())
        slug = urllib.parse.unquote(m.group(1)).lower().strip(".-")
        return None if not slug or slug in NOT_COMPANY or len(slug) > 80 else slug
    return None


def harvest(crawl):
    prefixes = {p: s for s, pats in SYSTEMS.items() for p, _ in pats}
    found = {s: {} for s in SYSTEMS}
    todo = blocks(crawl, prefixes)
    print("%s: %d index blocks" % (crawl, len(todo)))
    for shard, off, length in todo:
        raw = gzip.decompress(get("cc-index/collections/%s/indexes/%s" % (crawl, shard), (int(off), int(off) + int(length) - 1)))
        for line in raw.decode("utf-8", "replace").splitlines():
            key = line.split(" ", 1)[0]
            system = next((s for p, s in prefixes.items() if key.startswith(p)), None)
            if not system:
                continue
            try:
                url = json.loads(line.split(" ", 2)[2])["url"]
            except (IndexError, ValueError, KeyError):
                continue
            c = company(system, url)
            if c is None:
                continue
            if system == "paylocity":
                guid, name = c
                if name or guid not in found[system]:
                    found[system][guid] = name
            else:
                found[system][c] = True
    return found


def main():
    os.makedirs(OUT, exist_ok=True)
    total = {s: {} for s in SYSTEMS}
    for crawl in crawls(int(sys.argv[1]) if len(sys.argv) > 1 else 3):
        for s, got in harvest(crawl).items():
            for k, v in got.items():
                if v or k not in total[s]:
                    total[s][k] = v
    for s, got in total.items():
        path = os.path.join(OUT, s + ".json")
        old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
        if s == "paylocity":
            names = {r["guid"]: r.get("name", "") for r in old}
            names.update({g: n for g, n in got.items() if n or g not in names})
            rows = [{"guid": g, "name": n or g} for g, n in sorted(names.items())]
        else:
            rows = sorted(set(old) | set(got))
            if s == "workday":  # the same board seen as /NVIDIAExternalCareerSite and /nvidiaexternalcareersite
                rows = list({r.lower(): r for r in reversed(rows)}.values())[::-1]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=0, ensure_ascii=False)
        print("  %-10s %6d companies (%d new this harvest)" % (s, len(rows), len(rows) - len(old)))


if __name__ == "__main__":
    main()
