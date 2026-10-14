"""Signed, replay-resistant institutional aggregate reporting contract.

Every report is quarantined and must be independently reviewed. No report feeds
the optimizer automatically. This protects the optimizer's trusted-input boundary.
"""
import base64
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field, ConfigDict, model_validator
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .catalog import METRICS

CODE=re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{1,63}$")

class PhysicalRecord(BaseModel):
    model_config=ConfigDict(extra="forbid")
    metric: str
    unit: str
    region: str=Field(min_length=2,max_length=64)
    quantity: float=Field(ge=0)
    uncertainty_fraction: float=Field(ge=0,le=1)
    measurement: str
    period_start: datetime
    period_end: datetime

    @model_validator(mode="after")
    def check(self):
        if self.metric not in METRICS or self.unit!=METRICS[self.metric][0]:
            raise ValueError("unknown physical metric or incorrect unit")
        if not CODE.fullmatch(self.region):
            raise ValueError("invalid aggregate region label")
        if self.measurement not in {"meter","survey","lab","weighbridge","estimated","manual"}:
            raise ValueError("measurement method not recognized")
        if not math.isfinite(self.quantity) or not math.isfinite(self.uncertainty_fraction):
            raise ValueError("nonfinite observation")
        if self.period_start.tzinfo is None or self.period_end.tzinfo is None:
            raise ValueError("timestamps must have explicit timezone")
        if not self.period_start < self.period_end or self.period_end-self.period_start>timedelta(days=370):
            raise ValueError("invalid observation duration")
        if self.period_end>datetime.now(timezone.utc)+timedelta(days=1):
            raise ValueError("future observations are prohibited")
        return self

class PhysicalReport(BaseModel):
    model_config=ConfigDict(extra="forbid")
    schema_version: int=Field(ge=1,le=1)
    organization: str=Field(min_length=2,max_length=64)
    sequence: int=Field(ge=1)
    declared_at: datetime
    records: list[PhysicalRecord]=Field(min_length=1,max_length=300)

    @model_validator(mode="after")
    def validate_report(self):
        if not CODE.fullmatch(self.organization):
            raise ValueError("invalid registered organization identifier")
        if self.declared_at.tzinfo is None:
            raise ValueError("declaration must have timezone")
        if abs((datetime.now(timezone.utc)-self.declared_at).total_seconds())>86400:
            raise ValueError("signed declaration is stale or future-dated")
        keys=[(r.metric,r.region,r.period_start,r.period_end) for r in self.records]
        if len(set(keys))!=len(keys):raise ValueError("duplicate physical observation")
        return self

class SignedEnvelope(BaseModel):
    model_config=ConfigDict(extra="forbid")
    report: PhysicalReport
    signature: str=Field(min_length=80,max_length=120)

def canonical(report: PhysicalReport)->bytes:
    return json.dumps(report.model_dump(mode="json"),sort_keys=True,
                      ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf-8")

def authenticate(envelope:SignedEnvelope)->str:
    try:
        registry=json.loads(os.environ.get("CMPE_REPORTING_PUBLIC_KEYS","{}"))
        rawkey=registry[envelope.report.organization]
        if not isinstance(rawkey,str):raise ValueError("invalid registered key")
        key=base64.b64decode(rawkey,validate=True)
        sig=base64.b64decode(envelope.signature,validate=True)
        if len(key)!=32 or len(sig)!=64:raise ValueError("wrong key or signature length")
        Ed25519PublicKey.from_public_bytes(key).verify(sig,canonical(envelope.report))
    except (KeyError,ValueError,TypeError,InvalidSignature,json.JSONDecodeError) as e:
        raise ValueError("invalid or unregistered report signature") from e
    return hashlib.sha256(canonical(envelope.report)).hexdigest()

def flag_reconciliation(report: PhysicalReport)->list[str]:
    flags=[]
    grouped={}
    for r in report.records:
        if r.uncertainty_fraction>0.2:
            flags.append(f"uncertainty_high:{r.metric}:{r.region}")
        if r.measurement in ("manual","estimated"):
            flags.append(f"manual_verification_required:{r.metric}:{r.region}")
        key=(r.region,r.period_start,r.period_end)
        grouped.setdefault(key,{})[r.metric]=r.quantity
    for (region,_,_),v in grouped.items():
        if {"electricity_generated","electricity_consumed","electricity_grid_losses"}.issubset(v):
            g=v["electricity_generated"]
            discrepancy=abs(g-v["electricity_consumed"]-v["electricity_grid_losses"])
            if discrepancy>max(g,1.0)*0.05:
                flags.append(f"physical_balance_discrepancy:electricity:{region}")
    return sorted(set(flags))
