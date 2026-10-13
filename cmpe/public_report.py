"""Generate a reproducible, public, read-only physical-statistics report.

No GitHub account, secrets, consumer identities, or industrial private data
are ever embedded in the published website.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .worldbank import fetch, INDICATORS

COUNTRIES={"USA":"United States","CHN":"China","DEU":"Germany","IND":"India"}
PHYSICAL="EG.ELC.PROD.KH"
ACCESS="EG.ELC.ACCS.ZS"

def validate_series(items, country, code):
    if code not in INDICATORS:raise ValueError("unregistered indicator")
    if not items: raise ValueError(f"empty {country}/{code} series")
    years=set()
    for o in items:
        if o["location"]!=country or o["indicator"]!=code or o["unit"]!=INDICATORS[code]:
            raise ValueError("mismatched measurement")
        year=o["period"]
        if not (len(year)==4 and year.isdigit() and 1960<=int(year)<=2100):
            raise ValueError("invalid year")
        if year in years:raise ValueError("duplicated year")
        years.add(year)
        if o["value"] < 0:raise ValueError("negative observation")
        if code==ACCESS and o["value"]>100:raise ValueError("percentage greater than 100")
    return sorted(items,key=lambda x:x["period"])

def compile_report(datasets, *, retrieved_at=None):
    """datasets: list[(country, indicator, rows, source_hash)]"""
    summaries=[]
    seen=set()
    for country, code, observations, digest in datasets:
        if country not in COUNTRIES or code not in INDICATORS:
            raise ValueError("not allowlisted")
        if (country,code) in seen:raise ValueError("duplicate dataset")
        seen.add((country,code))
        if len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid source SHA256")
        clean=validate_series(observations,country,code)
        # Only publish public, aggregated observations
        summaries.append({
            "country":country,"country_name":COUNTRIES[country],
            "indicator":code,"unit":INDICATORS[code],"source_sha256":digest,
            "latest":clean[-1],"history":[{"year":int(i["period"]),"value":i["value"]} for i in clean],
        })
    if not any(x["indicator"]==PHYSICAL for x in summaries):
        raise ValueError("at least one physical output measurement required")
    return {
        "title":"CMPE Physical-Economic Observations",
        "status":"Public historical aggregates only; not a live national production feed",
        "method":"Source-provided annual World Bank observations; not automatically planning coefficients",
        "updated_utc":retrieved_at or datetime.now(timezone.utc).isoformat(),
        "sources":[{"name":"World Bank Indicators API v2","url":"https://api.worldbank.org/v2/"}],
        "series":sorted(summaries,key=lambda x:(x["country"],x["indicator"])),
    }

def publish(report, destination):
    target=Path(destination);target.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    (target/"data.json").write_bytes(raw)
    (target/"data.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  data.json\n")
    template=Path(__file__).resolve().parent.parent/"site"/"index.html"
    (target/"index.html").write_bytes(template.read_bytes())
    return hashlib.sha256(raw).hexdigest()

def build_online(country_codes=None):
    records=[]
    for country in (country_codes or sorted(COUNTRIES)):
        for code in (PHYSICAL,ACCESS):
            items,source_sha=fetch(country,code)
            records.append((country,code,items,source_sha))
    return compile_report(records)

def build_demo():
    # Explicitly synthetic fixture, suitable only for CI and local screenshots.
    rows=[]
    for country in ("USA","CHN"):
        for code,unitbase in ((PHYSICAL, 1e12),(ACCESS,94)):
            obs=[{"location":country,"indicator":code,"unit":INDICATORS[code],"period":str(y),"value":unitbase*(1+(y-2018)*0.025) if code==PHYSICAL else min(100,unitbase+(y-2018))} for y in range(2018,2023)]
            rows.append((country,code,obs,"a"*64))
    report=compile_report(rows,retrieved_at="2000-01-01T00:00:00+00:00")
    report["status"]="FICTIONAL DEMONSTRATION: NO REAL OBSERVATIONS"
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="site-build")
    p.add_argument("--demo",action="store_true")
    p.add_argument("--archive",action="store_true",help="Content-address archive the exact report; requires durable storage in real deployments")
    p.add_argument("--countries",nargs="+",choices=sorted(COUNTRIES))
    args=p.parse_args()
    report=build_demo() if args.demo else build_online(args.countries)
    digest=publish(report,args.out)
    if args.archive:
        from .archive import archive_bytes
        archived=archive_bytes((Path(args.out)/"data.json").read_bytes(),namespace="public")
        if archived["sha256"]!=digest:raise RuntimeError("archive checksum mismatch")
    print(f"Validated {len(report['series'])} series; SHA256={digest}; published to {args.out}")

if __name__=="__main__":main()
