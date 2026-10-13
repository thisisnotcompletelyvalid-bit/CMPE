"""Public statistical ingest. Separate observations from planning coefficients."""
import argparse, hashlib, json, math, os, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from sqlalchemy import select
from .db import engine,initialize,sessionmaker_for, Observation

INDICATORS={
    "SP.POP.TOTL":"persons",
    "NY.GDP.MKTP.CD":"current USD (not a physical quantity)",
    "EG.ELC.ACCS.ZS":"percent of population",
    "EG.ELC.PROD.KH":"kWh",
    "EN.ATM.CO2E.KT":"kt CO2",
}
COUNTRIES={"USA","CHN","VNM","CUB","LAO","DEU","IND","BRA","ZAF","MEX"}

def fetch(country,indicator,opener=urlopen):
    if country not in COUNTRIES or indicator not in INDICATORS:raise ValueError("country or indicator not allowlisted")
    url=f"https://api.worldbank.org/v2/country/{quote(country)}/indicator/{quote(indicator)}?format=json&per_page=1000"
    request=Request(url,headers={"User-Agent":"CMPE-research-data-ingest/0.1"})
    with opener(request,timeout=30) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000:raise ValueError("public response too large")
    payload=json.loads(raw)
    if not isinstance(payload,list) or len(payload)!=2 or not isinstance(payload[1],list):raise ValueError(f"World Bank has no supported records for {country}/{indicator}: {str(payload)[:200]}")
    items=[]
    for entry in payload[1]:
        year=str(entry.get("date",""))
        val=entry.get("value")
        if len(year)!=4 or not year.isdigit() or type(val) not in (int,float) or not math.isfinite(val):continue
        items.append({"provider":"worldbank","location":country,"indicator":indicator,"period":year,"unit":INDICATORS[indicator],"value":float(val)})
    if not items:raise ValueError("no numeric observations; fail closed")
    return items,hashlib.sha256(raw).hexdigest()

def ingest(items,source_sha):
    eng=engine();initialize(eng)
    Session=sessionmaker_for(eng)
    with Session.begin() as db:
        for item in items:
            q=select(Observation).where(Observation.provider==item["provider"],Observation.location==item["location"],Observation.indicator==item["indicator"],Observation.period==item["period"])
            row=db.scalar(q)
            if row is None:db.add(Observation(**item,source_sha256=source_sha))
            else:row.value=item["value"];row.source_sha256=source_sha;row.unit=item["unit"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--country",choices=sorted(COUNTRIES),default="USA")
    p.add_argument("--out",default="data/snapshots/worldbank.json")
    p.add_argument("--import-db",action="store_true")
    a=p.parse_args()
    records=[]
    for code in INDICATORS:
        last=None
        for delay in (0,1,3):
            if delay:time.sleep(delay)
            try:
                items,sha=fetch(a.country,code)
                records.append({"indicator":code,"source_sha256":sha,"observations":items})
                if a.import_db:ingest(items,sha)
                last=None;break
            except Exception as ex:last=ex
        if last:raise RuntimeError("World Bank ingest failed for "+code) from last
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({"source":"World Bank Indicators API v2","country":a.country,"retrieved_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"indicators":records},indent=2))
    print(f"Validated {sum(len(r['observations']) for r in records)} annual observations for {a.country}; written {dest}")

if __name__=="__main__":main()
