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
- The company lists in `data/` come from the same project and are licensed CC BY-NC 4.0 (non-commercial use, credit
  required). Vettra uses them for a free pilot; they are to be replaced by lists harvested by this project (PLAN.md,
  stage 4) before any commercial use.
