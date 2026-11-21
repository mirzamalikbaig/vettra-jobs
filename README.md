# vettra-jobs
<!-- first run 2026-11-20: 50 min, 576,179 jobs, 32,563 companies, 25 MB -->

Open job postings from tens of thousands of employers, in every field, collected once a day from the employers' own
public job boards (Greenhouse, Lever, Ashby, Workday, iCIMS, Paylocity, BambooHR, Workable, Join) and published as one
compressed file for the Vettra app.

- Today's file: https://github.com/mirzamalikbaig/vettra-jobs/releases/latest/download/jobs.jsonl.gz
  (gzip, one JSON job per line: title, company, location, url, ats, dates) and `metadata.json` next to it.
- Runs on GitHub Actions every day (`.github/workflows/daily.yml`); each run adds a line to `runs.jsonl`.
- Only public job postings are here. No personal data: each person's resume, profile and applications stay on their
  own computer, where Vettra matches this file against them.
- Plan and review: `PLAN.md`.

## Credits and licenses

- The collector (`scripts/scraper.py`, `scripts/geolocation.py`) is from
  [job-board-aggregator](https://github.com/Riley-Dorrington/job-board-aggregator) by Riley Dorrington, MIT License
  (`LICENSE-job-board-aggregator`).
- The company lists in `data/` come from the same project and are licensed
  [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) by Riley Dorrington: non-commercial use only, credit
  required; commercial use needs the author's permission. **Changes made here:** each daily run updates
  `data/join_company_ids.json`, and the published `jobs.jsonl.gz` is built by reading the companies in these lists.
- **Open licensing issue.** Being free does not by itself make a use non-commercial. Until it is resolved, these lists
  are used only for the owner's own testing. Vettra is not distributed to anyone else, and is never run as a business,
  with jobs found through these lists, until either the author grants permission in writing or the lists are replaced
  by company lists this project builds itself (PLAN.md, stage 4).
