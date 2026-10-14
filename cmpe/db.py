"""Persistent metadata and approvals. PostgreSQL in deployment; SQLite only for tests."""
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, JSON, Text, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase): pass

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True)
    sha256 = Column(String(64), nullable=False, unique=True)
    source = Column(String(120),nullable=False)
    submitted_by = Column(String(40),nullable=False)
    state = Column(String(20),nullable=False, default="pending",index=True)
    payload = Column(JSON,nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer,primary_key=True)
    dataset_id = Column(Integer,ForeignKey("datasets.id"),nullable=False)
    reviewer = Column(String(40),nullable=False)
    __table_args__ = (UniqueConstraint("dataset_id","reviewer"),)

class Observation(Base):
    __tablename__ = "observations"
    id = Column(Integer,primary_key=True)
    provider = Column(String(50),nullable=False)
    location = Column(String(30),nullable=False)
    indicator = Column(String(90),nullable=False)
    period = Column(String(20),nullable=False)
    unit = Column(String(80),nullable=False)
    value = Column(Float,nullable=False)
    source_sha256 = Column(String(64),nullable=False)
    __table_args__=(UniqueConstraint("provider","location","indicator","period",name="uq_observation"),)

class SignedReport(Base):
    __tablename__ = "signed_reports"
    id = Column(Integer, primary_key=True)
    organization = Column(String(64), nullable=False)
    sequence = Column(Integer, nullable=False)
    sha256 = Column(String(64), unique=True, nullable=False)
    payload = Column(JSON, nullable=False)
    flags = Column(JSON, nullable=False)
    state = Column(String(30), default="quarantined", nullable=False)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    __table_args__ = (UniqueConstraint("organization","sequence",name="uq_reporting_sequence"),)

class ReportReview(Base):
    __tablename__ = "report_reviews"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("signed_reports.id"), nullable=False)
    reviewer = Column(String(40), nullable=False)
    __table_args__ = (UniqueConstraint("report_id","reviewer",name="uq_report_reviewer"),)

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer,primary_key=True)
    dataset_id = Column(Integer,ForeignKey("datasets.id"),nullable=False)
    input_sha256 = Column(String(64),nullable=False)
    result = Column(JSON,nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

def database_url():
    url=os.environ.get("CMPE_DATABASE_URL","sqlite:///./cmpe-dev.sqlite3")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://"+url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://"+url[len("postgresql://"):]
    return url

def engine():
    url=database_url()
    kw={"pool_pre_ping":True}
    if url.startswith("sqlite:"):kw["connect_args"]={"check_same_thread":False}
    return create_engine(url,**kw)

def sessionmaker_for(eng):
    return sessionmaker(bind=eng,autoflush=False,expire_on_commit=False)

def initialize(eng):
    # Bootstrap only. National installations require versioned migrations and change approvals.
    if os.environ.get("CMPE_REQUIRE_MIGRATIONS") == "1":
        from sqlalchemy import inspect, text
        if "alembic_version" not in inspect(eng).get_table_names():
            raise RuntimeError("Run the reviewed Alembic migrations before starting the service")
        with eng.connect() as c:
            if c.execute(text("SELECT version_num FROM alembic_version")).scalar() != "0002_signed_reports":
                raise RuntimeError("Incompatible database schema migration")
    else:
        Base.metadata.create_all(eng)
