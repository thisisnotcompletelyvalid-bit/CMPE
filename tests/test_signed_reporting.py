import os, base64\nos.environ.setdefault("CMPE_DATABASE_URL","sqlite:///./cmpe-report-test.sqlite3")\nfor role in ("INGEST","REVIEWER_A","REVIEWER_B","PLANNER"):\n    os.environ.setdefault("CMPE_"+role+"_TOKEN",role[0]*40)
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from cmpe.api import app
from cmpe.reporting import PhysicalReport, SignedEnvelope, authenticate, canonical, flag_reconciliation
from cmpe.catalog import readiness, inventory
from cmpe.db import SignedReport,Session if False else SignedReport

def specimen():
    now=datetime.now(timezone.utc)
    return {
        "schema_version":1,"organization":"cooperative-factory-test",
        "sequence":1,"declared_at":now.isoformat(),
        "records":[
            {"metric":"electricity_generated","unit":"kWh","region":"test-region",
             "quantity":1000,"uncertainty_fraction":0.02,"measurement":"meter",
             "period_start":(now-timedelta(hours=2)).isoformat(),
             "period_end":(now-timedelta(hours=1)).isoformat()},
            {"metric":"electricity_consumed","unit":"kWh","region":"test-region",
             "quantity":950,"uncertainty_fraction":0.02,"measurement":"meter",
             "period_start":(now-timedelta(hours=2)).isoformat(),
             "period_end":(now-timedelta(hours=1)).isoformat()},
            {"metric":"electricity_grid_losses","unit":"kWh","region":"test-region",
             "quantity":50,"uncertainty_fraction":0.02,"measurement":"meter",
             "period_start":(now-timedelta(hours=2)).isoformat(),
             "period_end":(now-timedelta(hours=1)).isoformat()}
        ]
    }

def test_report_signatures_replay_review_and_isolation(monkeypatch):
    monkeypatch.delenv("CMPE_PUBLIC_READ_ONLY",raising=False)
    key=Ed25519PrivateKey.generate()
    pub=base64.b64encode(key.public_key().public_bytes(
        serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    monkeypatch.setenv("CMPE_REPORTING_PUBLIC_KEYS",
        '{"cooperative-factory-test":"'+pub+'"}')
    specimen_obj=PhysicalReport.model_validate(specimen())
    signed=base64.b64encode(key.sign(canonical(specimen_obj))).decode()
    body={"report":specimen_obj.model_dump(mode="json"),"signature":signed}
    headers={"X-CMPE-Key":os.environ["CMPE_INGEST_TOKEN"]}
    with TestClient(app) as client:
        assert client.get("/v1/readiness").json()["national_planning_ready"] is False
        assert client.get("/v1/catalog").json()["requirements"]
        denied=client.post("/v1/reports",json={"report":body["report"],"signature":"A"*88},headers=headers)
        assert denied.status_code==422
        accepted=client.post("/v1/reports",json=body,headers=headers)
        assert accepted.status_code==201,accepted.text
        rid=accepted.json()["report_id"]
        assert accepted.json()["flags"]==[]
        assert accepted.json()["model_input_authorized"] is False
        assert client.post("/v1/reports",json=body,headers=headers).status_code==409
        a=client.post(f"/v1/reports/{rid}/review",
            headers={"X-CMPE-Key":os.environ["CMPE_REVIEWER_A_TOKEN"]})
        assert a.status_code==200 and a.json()["state"]=="quarantined"
        b=client.post(f"/v1/reports/{rid}/review",
            headers={"X-CMPE-Key":os.environ["CMPE_REVIEWER_B_TOKEN"]})
        assert b.status_code==200 and b.json()["state"]=="reviewed"
        assert b.json()["model_input_authorized"] is False

def test_physical_balance_flags_and_privacy_schema():
    from pydantic import ValidationError
    p=specimen()
    p["records"][1]["quantity"]=300
    assert any("balance_discrepancy" in f for f in flag_reconciliation(PhysicalReport.model_validate(p)))
    p["records"][0]["household_name"]="private person"
    try:PhysicalReport.model_validate(p)
    except ValidationError:pass
    else:raise AssertionError("personal field should not be allowed")

def test_public_readonly_blocks_writes(monkeypatch):
    monkeypatch.setenv("CMPE_PUBLIC_READ_ONLY","1")
    with TestClient(app) as client:
        assert client.get("/v1/readiness").status_code==200
        assert client.post("/v1/reports",json={}).status_code==403
