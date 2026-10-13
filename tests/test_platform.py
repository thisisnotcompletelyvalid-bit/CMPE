import os,json
from pathlib import Path
os.environ["CMPE_DATABASE_URL"]="sqlite:///./cmpe-test.sqlite3"
os.environ["CMPE_INGEST_TOKEN"]="I"*40
os.environ["CMPE_REVIEWER_A_TOKEN"]="A"*40
os.environ["CMPE_REVIEWER_B_TOKEN"]="B"*40
os.environ["CMPE_PLANNER_TOKEN"]="P"*40
from fastapi.testclient import TestClient
from cmpe.api import app
from cmpe.optimizer import optimize
from cmpe.schema import Economy

DATA=json.loads(Path("data/examples/fictional_economy.json").read_text())

def hdr(role):return {"X-CMPE-Key":os.environ["CMPE_"+role+"_TOKEN"]}

def test_core_solver():
    out=optimize(Economy.model_validate(DATA["economy"]))
    assert out["coverage_fraction"]>0.99999
    assert out["max_balance_violation"]<1e-5
    assert out["labor_used_hours"]<=160
    assert out["emissions_used_kg"]<=100

def test_reject_bad_units():
    d=json.loads(json.dumps(DATA["economy"]))
    d["activities"][0]["inputs"]={"coal":1}
    import pytest
    with pytest.raises(ValueError):Economy.model_validate(d)

def test_reject_nan():
    d=json.loads(json.dumps(DATA["economy"]))
    d["activities"][0]["capacity"]=float("nan")
    import pytest
    with pytest.raises(ValueError):Economy.model_validate(d)

def test_authorization_and_dual_review():
    with TestClient(app) as c:
        assert c.get("/health/ready").status_code==200
        assert c.get("/v1/status").status_code==401
        assert c.post("/v1/plans",headers=hdr("PLANNER")).status_code==409
        r=c.post("/v1/datasets",json=DATA,headers=hdr("INGEST"))
        assert r.status_code==201,r.text
        id=r.json()["dataset_id"]
        assert c.post(f"/v1/datasets/{id}/approve",headers=hdr("INGEST")).status_code==401
        a=c.post(f"/v1/datasets/{id}/approve",headers=hdr("REVIEWER_A"))
        assert a.status_code==200 and a.json()["state"]=="pending"
        assert c.post(f"/v1/datasets/{id}/approve",headers=hdr("REVIEWER_A")).status_code==409
        b=c.post(f"/v1/datasets/{id}/approve",headers=hdr("REVIEWER_B"))
        assert b.status_code==200 and b.json()["state"]=="active"
        p=c.post("/v1/plans",headers=hdr("PLANNER"))
        assert p.status_code==200,p.text
        pid=p.json()["plan_id"]
        assert c.get(f"/v1/plans/{pid}",headers=hdr("PLANNER")).status_code==200
        assert c.get("/v1/status",headers=hdr("PLANNER")).json()["datasets"]["active"]==1

def test_large_payload_rejected():
    with TestClient(app) as c:
        resp=c.post("/v1/datasets",content=b"x"*513000,headers={**hdr("INGEST"),"Content-Type":"application/json"})
        assert resp.status_code==413
