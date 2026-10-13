"""Integration check against real PostgreSQL, independent of SQLite FastAPI tests."""
import os, uuid
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from cmpe.db import engine,initialize,sessionmaker_for,Dataset

def test_postgres_durable_unique_dataset_hash():
    url=os.environ.get("CMPE_TEST_DATABASE_URL")
    if not url:pytest.skip("CI PostgreSQL URL not configured")
    previous=os.environ.get("CMPE_DATABASE_URL")
    try:
        os.environ["CMPE_DATABASE_URL"]=url
        dbengine=engine();initialize(dbengine)
        Session=sessionmaker_for(dbengine)
        sha=uuid.uuid4().hex
        with Session.begin() as db:
            db.add(Dataset(sha256=sha,source="ci-physical-test",submitted_by="CI",state="pending",payload={"goods":[]}))
        with Session() as db:
            assert db.scalar(select(Dataset).where(Dataset.sha256==sha)) is not None
        with pytest.raises(IntegrityError):
            with Session.begin() as db:
                db.add(Dataset(sha256=sha,source="duplicate",submitted_by="CI",state="pending",payload={}))
        dbengine.dispose()
    finally:
        if previous is None:os.environ.pop("CMPE_DATABASE_URL",None)
        else:os.environ["CMPE_DATABASE_URL"]=previous
