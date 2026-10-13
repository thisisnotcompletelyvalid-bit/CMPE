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

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer,primary_key=True)
    dataset_id = Column(Integer,ForeignKey("datasets.id"),nullable=False)
    input_sha256 = Column(String(64),nullable=False)
    result = Column(JSON,nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

def engine():
    url=os.environ.get("CMPE_DATABASE_URL","sqlite:///./cmpe-dev.sqlite3")
    kw={"pool_pre_ping":True}
    if url.startswith("sqlite:"):kw["connect_args"]={"check_same_thread":False}
    return create_engine(url,**kw)

def sessionmaker_for(eng):
    return sessionmaker(bind=eng,autoflush=False,expire_on_commit=False)

def initialize(eng):
    # Bootstrap only. National installations require versioned migrations and change approvals.
    Base.metadata.create_all(eng)
