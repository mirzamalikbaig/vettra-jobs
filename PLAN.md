# vettra-jobs plan (reviewed 2026-11-20)

Goal: one public, compressed file of open job postings from tens of thousands of employers in every field, refreshed
daily for free, that each person's Vettra downloads and matches on their own laptop.

## Stages

| # | What | Done when |
|---|---|---|
| 1 | Collector: the MIT job-board-aggregator scraper (credited) + its company lists, run by a daily GitHub Actions workflow | a run finishes on GitHub |
| 2 | Publish: `jobs.jsonl.gz` (one job per line, so a laptop can read it without loading it whole) + `metadata.json` as release assets; Vettra downloads `releases/latest/download/jobs.jsonl.gz` | the link serves today's file |
| 3 | Vettra reads it: download once a day, keep jobs whose title fits the person's field pack and that are in the US, fetch descriptions for those only, then the usual verdict and matching | a teacher, a nurse and a chip designer get matches from it |
| 4 | Our own company list: harvest Common Crawl's URL index for ATS addresses (the same method the aggregator used), so Vettra does not depend on lists licensed for non-commercial use only | lists in this repo come from our own harvest |

## Review: risks and decisions

1. **Licenses.** Code is MIT: keep its LICENSE and credit. The company lists are CC BY-NC 4.0: fine for a free pilot,
   not for a paid product. Stage 4 replaces them.
2. **No personal data here.** This repository is public and holds only code and public job postings. Resumes, profiles
   and applications stay on each person's laptop; Vettra (private repository) only downloads from here.
3. **Run time.** The aggregator's daily run takes about 53 minutes for 67k companies (its Actions history, 2026-11-19
   and 20), well under GitHub's 6-hour job limit. Workflow timeout set to 5 hours.
4. **Politeness.** Keep the aggregator's per-system worker counts (tuned to each system's rate limits). Read only public
   job APIs and feeds; no logins, no proxies, nothing that hides an automated reader.
5. **Scheduled runs stop on inactive repositories** (GitHub disables schedules after 60 days without commits). Each run
   commits one line to `runs.jsonl` (date, companies, jobs, minutes) so the repository stays active and the numbers are
   on record.
6. **Simpler than the original.** No website, no chunked GitHub Pages copy, no salary or trend charts: one release file.
   Skipped: merging with yesterday's file (a closed job should disappear anyway; "first seen" can come later).
7. **Releases pile up.** Keep the newest 3, delete older ones in the same workflow.
8. **Download size for each person.** About 70-100 MB compressed. Vettra downloads at most once a day and keeps only
   the filtered jobs.
