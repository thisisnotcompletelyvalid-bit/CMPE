"""Advisory CMPE API: persistent datasets, independent reviews, verifiable simulation."""
import os, json, hashlib, hmac
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError
from .db import engine, initialize, sessionmaker_for, Dataset, Approval, Plan, Observation, SignedReport, ReportReview
from .schema import Economy
from .optimizer import optimize
from .catalog import inventory, readiness as assess_readiness
from .reporting import SignedEnvelope, authenticate, flag_reconciliation

ENG=engine()
Session=sessionmaker_for(ENG)
def sha(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

@asynccontextmanager
async def lifespan(application):
    initialize(ENG)
    yield

app=FastAPI(title="CMPE Physical Planning API",version="3.0.0-alpha",lifespan=lifespan,docs_url=None,redoc_url=None)
MAX_BODY=512_000

@app.middleware("http")
async def security(request:Request,call_next):
    if request.method in ("POST","PUT","PATCH"):
        try: declared=int(request.headers.get("content-length","0"))
        except ValueError: declared=MAX_BODY+1
        if declared>MAX_BODY:
            return JSONResponse({"detail":"request too large"},status_code=413)
        b=bytearray()
        async for chunk in request.stream():
            b.extend(chunk)
            if len(b)>MAX_BODY: return JSONResponse({"detail":"request too large"},status_code=413)
        request._body=bytes(b)
    r=await call_next(request)
    r.headers["Cache-Control"]="no-store"
    r.headers["X-Content-Type-Options"]="nosniff"
    r.headers["X-Frame-Options"]="DENY"
    r.headers["Referrer-Policy"]="no-referrer"
    r.headers["Content-Security-Policy"]="default-src 'none'; style-src 'unsafe-inline'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"
    return r

def check_role(roles, key):
    key = key or ""
    for role in roles:
        expected=os.environ.get("CMPE_"+role+"_TOKEN","")
        if len(expected)>=32 and hmac.compare_digest(key,expected):
            return role
    raise HTTPException(401,"Authorized credentials required")

def credential(*roles):
    def verify(x_cmpe_key:str|None=Header(default=None)):
        return check_role(roles,x_cmpe_key)
    return verify

class Submitted(BaseModel):
    model_config=ConfigDict(extra="forbid")
    source: str=Field(min_length=3,max_length=120)
    economy: Economy

@app.get("/health/live")
def live(): return {"status":"alive","execution":"advisory-only"}

@app.get("/health/ready")
def ready():
    try:
        with ENG.connect() as c:c.execute(text("SELECT 1"))
    except Exception:raise HTTPException(503,"database unavailable")
    return {"status":"ready","database":"reachable"}

@app.get("/")
def index():
    return HTMLResponse(Path(__file__).with_name("public_ui.html" if os.environ.get("CMPE_PUBLIC_READ_ONLY")=="1" else "ui.html").read_text())

@app.get("/assets/readiness.js")
def public_script():
    return FileResponse(Path(__file__).with_name("readiness.js"),media_type="text/javascript")

@app.get("/assets/console.js")
def script():
    return FileResponse(Path(__file__).with_name("console.js"),media_type="text/javascript")

@app.get("/v1/status")
def status(_:str=Depends(credential("INGEST","REVIEWER_A","REVIEWER_B","PLANNER"))):
    with Session() as db:
        counts={x:db.scalar(select(func.count()).select_from(Dataset).where(Dataset.state==x)) for x in ("pending","active","superseded")}
        n=db.scalar(select(func.count()).select_from(Observation))
    return {"datasets":counts,"public_observations":n,"actuation_enabled":False}

@app.post("/v1/datasets",status_code=201)
def stage(body:Submitted,role:str=Depends(credential("INGEST"))):
    payload=body.economy.model_dump()
    digest=sha({"source":body.source,"economy":payload})
    with Session.begin() as db:
        existing=db.scalar(select(Dataset).where(Dataset.sha256==digest))
        if existing:return {"dataset_id":existing.id,"state":existing.state,"sha256":digest,"duplicate":True}
        row=Dataset(sha256=digest,source=body.source,submitted_by=role,state="pending",payload=payload)
        db.add(row); db.flush(); id=row.id
    return {"dataset_id":id,"state":"pending","sha256":digest}

@app.post("/v1/datasets/{dataset_id}/approve")
def approve(dataset_id:int,role:str=Depends(credential("REVIEWER_A","REVIEWER_B"))):
    with Session.begin() as db:
        row=db.scalar(select(Dataset).where(Dataset.id==dataset_id).with_for_update())
        if row is None:raise HTTPException(404,"unknown dataset")
        if row.state!="pending":raise HTTPException(409,"dataset not pending")
        if db.scalar(select(Approval).where(Approval.dataset_id==dataset_id,Approval.reviewer==role)):
            raise HTTPException(409,"reviewer already approved")
        db.add(Approval(dataset_id=dataset_id,reviewer=role)); db.flush()
        count=db.scalar(select(func.count()).select_from(Approval).where(Approval.dataset_id==dataset_id))
        if count>=2:
            for other in db.scalars(select(Dataset).where(Dataset.state=="active").with_for_update()):
                other.state="superseded"
            row.state="active"
        return {"dataset_id":dataset_id,"state":row.state,"approvals":count}

@app.get("/v1/datasets")
def datasets(_:str=Depends(credential("INGEST","REVIEWER_A","REVIEWER_B","PLANNER"))):
    with Session() as db:
        rows=db.scalars(select(Dataset).order_by(Dataset.id.desc()).limit(100))
        return [{"id":r.id,"source":r.source,"sha256":r.sha256,"state":r.state,"created_at":r.created_at.isoformat()} for r in rows]

@app.post("/v1/plans")
def plan(_:str=Depends(credential("PLANNER"))):
    with Session() as db:
        row=db.scalar(select(Dataset).where(Dataset.state=="active").order_by(Dataset.id.desc()))
        if row is None:raise HTTPException(409,"no independently approved dataset")
        # Copy data outside transaction; the result contains the exact input hash.
        did,hash_,data=row.id,row.sha256,row.payload
    try:result=optimize(Economy.model_validate(data))
    except (ValueError,RuntimeError) as e:raise HTTPException(422,str(e)) from e
    result["input_sha256"]=hash_
    with Session.begin() as db:
        run=Plan(dataset_id=did,input_sha256=hash_,result=result)
        db.add(run);db.flush();pid=run.id
    return {"plan_id":pid,"dataset_id":did,"result":result}

@app.get("/v1/plans/{plan_id}")
def get_plan(plan_id:int,_:str=Depends(credential("PLANNER"))):
    with Session() as db:
        p=db.get(Plan,plan_id)
        if p is None:raise HTTPException(404,"unknown simulation")
        return {"id":p.id,"dataset_id":p.dataset_id,"input_sha256":p.input_sha256,"result":p.result}

@app.get("/v1/observations")
def observations(limit:int=50,_:str=Depends(credential("INGEST","PLANNER"))):
    if limit<1 or limit>500:raise HTTPException(422,"limit must be between 1 and 500")
    with Session() as db:
        rows=db.scalars(select(Observation).order_by(Observation.id.desc()).limit(limit))
        return [{"provider":r.provider,"location":r.location,"indicator":r.indicator,"period":r.period,"value":r.value,"unit":r.unit,"source_sha256":r.source_sha256} for r in rows]


@app.get("/v1/catalog")
def information_catalog():
    return {"purpose":"National physical-data inventory; requirements not currently acquired",
            "requirements": inventory()}

@app.get("/v1/readiness")
def readiness():
    return assess_readiness()

@app.post("/v1/reports",status_code=201)
def accept_signed_report(body:SignedEnvelope, role:str=Depends(credential("INGEST"))):
    """Verify source signature, prevent replay, quarantine until independent review."""
    try:
        digest=authenticate(body)
    except ValueError as e:
        raise HTTPException(422,str(e)) from e
    flags=flag_reconciliation(body.report)
    with Session.begin() as db:
        # A full national deployment requires a transactionally locked
        # organization source registry to serialize concurrent submissions.
        most_recent=db.scalar(select(func.max(SignedReport.sequence)).where(
            SignedReport.organization==body.report.organization))
        if most_recent is not None and body.report.sequence<=most_recent:
            raise HTTPException(409,"stale or duplicate source sequence")
        report=SignedReport(
            organization=body.report.organization,sequence=body.report.sequence,
            sha256=digest,payload=body.report.model_dump(mode="json"),
            flags=flags,state="quarantined")
        db.add(report)
        try:db.flush()
        except IntegrityError as e:
            raise HTTPException(409,"duplicate report") from e
        identifier=report.id
    return {"report_id":identifier,"sha256":digest,"state":"quarantined","flags":flags,
            "model_input_authorized":False}

@app.get("/v1/reports")
def list_signed_reports(_:str=Depends(credential("INGEST","REVIEWER_A","REVIEWER_B","PLANNER"))):
    with Session() as db:
        rows=db.scalars(select(SignedReport).order_by(SignedReport.id.desc()).limit(100))
        return [{"id":r.id,"organization":r.organization,"sequence":r.sequence,
                 "sha256":r.sha256,"state":r.state,"flags":r.flags} for r in rows]

@app.post("/v1/reports/{report_id}/review")
def review_signed_report(report_id:int,role:str=Depends(credential("REVIEWER_A","REVIEWER_B"))):
    with Session.begin() as db:
        row=db.scalar(select(SignedReport).where(SignedReport.id==report_id).with_for_update())
        if row is None:raise HTTPException(404,"unknown report")
        if row.state!="quarantined":raise HTTPException(409,"report not awaiting review")
        previous=db.scalar(select(ReportReview).where(
            ReportReview.report_id==report_id,ReportReview.reviewer==role))
        if previous:raise HTTPException(409,"reviewer already recorded")
        db.add(ReportReview(report_id=report_id,reviewer=role));db.flush()
        count=db.scalar(select(func.count()).select_from(ReportReview).where(
            ReportReview.report_id==report_id))
        if count>=2 and not row.flags:
            row.state="reviewed"
        return {"report_id":report_id,"state":row.state,"reviews":count,
                "manual_reconciliation_required":bool(row.flags),
                "model_input_authorized":False}
