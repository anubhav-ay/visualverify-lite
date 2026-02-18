"""Simple SQLite database models"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class VerificationJob(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True)
    image_url = Column(Text)
    user_claim = Column(Text)
    status = Column(String(20), default="PROCESSING")  # PROCESSING, COMPLETED, FAILED
    verdict = Column(String(20))  # TRUE, FALSE, RECYCLED, MISLEADING, UNVERIFIED
    confidence = Column(Float)
    explanation = Column(Text)
    evidence = Column(JSON)
    real_context = Column(JSON)
    claim_context = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class ImageCache(Base):
    __tablename__ = "image_cache"
    
    id = Column(Integer, primary_key=True)
    image_hash = Column(String(32), unique=True, index=True)  # MD5
    phash = Column(String(16), index=True)  # perceptual hash
    first_seen = Column(DateTime, default=datetime.utcnow)
    verdict = Column(String(20))
    confidence = Column(Float)
    explanation = Column(Text)

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "verify.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
