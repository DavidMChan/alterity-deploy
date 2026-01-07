import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, BigInteger, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func

# Database URL from env
# Format: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Models ---

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(Text)
    # ... other fields ignored for worker scope for now

class DemographicConfig(Base):
    __tablename__ = "demographic_configs"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    name = Column(Text)
    constraints = Column(JSONB, default={})

class Survey(Base):
    __tablename__ = "surveys"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    name = Column(Text)
    status = Column(Text)

class Probe(Base):
    __tablename__ = "probes"
    id = Column(BigInteger, primary_key=True, index=True)
    survey_id = Column(BigInteger, ForeignKey("surveys.id"))
    content = Column(Text)
    type = Column(Text)
    options = Column(JSONB)

class Backstory(Base):
    __tablename__ = "backstories"
    id = Column(BigInteger, primary_key=True, index=True)
    content = Column(Text)
    model_signature = Column(Text)
    demographics = Column(JSONB, default={})
    custom_tags = Column(JSONB, default={})
    # embedding = Column(Vector(1536)) # PGVector needs special handling or ignore in vanilla sqlalchemy

class SurveyRun(Base):
    __tablename__ = "survey_runs"
    id = Column(BigInteger, primary_key=True, index=True)
    survey_id = Column(BigInteger, ForeignKey("surveys.id"))
    config_id = Column(BigInteger, ForeignKey("demographic_configs.id"), nullable=True)
    methodology = Column(Text)
    status = Column(Text)
    run_config = Column(JSONB, default={})
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Result(Base):
    __tablename__ = "results"
    id = Column(BigInteger, primary_key=True, index=True)
    run_id = Column(BigInteger, ForeignKey("survey_runs.id"))
    probe_id = Column(BigInteger, ForeignKey("probes.id"))
    backstory_id = Column(BigInteger, ForeignKey("backstories.id"), nullable=True)
    response = Column(JSONB)
    usage_cost = Column(Float, default=0.0)

class Configuration(Base):
    __tablename__ = "configurations"
    key = Column(Text, primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    name = Column(Text, primary_key=True)
    is_enabled = Column(Boolean, default=False)
    properties = Column(JSONB, default={})
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
