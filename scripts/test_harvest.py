"""python scripts/test_harvest.py   offline checks of how harvest.py reads company names out of job-system URLs."""
from harvest import company

cases = [
    ("greenhouse", "https://boards.greenhouse.io/Anthropic/jobs/123", "anthropic"),
    ("greenhouse", "https://boards.greenhouse.io/embed/job_board?for=stripe", "stripe"),
    ("greenhouse", "https://job-boards.greenhouse.io/etched/jobs/9", "etched"),
    ("greenhouse", "https://boards.greenhouse.io/robots.txt", None),
    ("lever", "https://jobs.lever.co/1password/abc", "1password"),
    ("ashby", "https://jobs.ashbyhq.com/openai/xyz", "openai"),
    ("bamboohr", "https://acme.bamboohr.com/careers/12", "acme"),
    ("icims", "https://careers-harrowcouncil.icims.com/jobs/1/x/job", "harrowcouncil"),
    ("workday", "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/x", "nvidia|wd5|NVIDIAExternalCareerSite"),
    ("workday", "https://intel.wd1.myworkdayjobs.com/External", "intel|wd1|External"),
    ("workday", "https://intel.wd1.myworkdayjobs.com/robots.txt", None),
    ("paylocity", "https://recruiting.paylocity.com/Recruiting/Jobs/All/73b6525a-3273-48b3-b9d8-d6479233c61c/10-Design",
     ("73b6525a-3273-48b3-b9d8-d6479233c61c", "10 Design")),
]
bad = [(s, u, company(s, u), want) for s, u, want in cases if company(s, u) != want]
for b in bad:
    print("FAIL", b)
print("%d checks, %d failed" % (len(cases), len(bad)))
raise SystemExit(1 if bad else 0)
