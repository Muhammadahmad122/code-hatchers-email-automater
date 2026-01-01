from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Prospect(Base):
    __tablename__ = 'prospects'
    
    id = Column(Integer, primary_key=True)
    business_name = Column(String, nullable=False)
    industry = Column(String)
    url = Column(String)
    contact_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    
    # AI Analysis Fields
    pain_point = Column(Text)
    pain_point_evidence = Column(Text)
    pain_point_confidence = Column(Float)
    
    # Solution Fields
    solution_concept_title = Column(String)
    solution_concept_body = Column(Text)
    solution_technical_details = Column(Text) # Internal use only
    validation_status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    
    # Status
    status = Column(String, default="NEW") # NEW, CONTACTED, ENGAGED, CONVERTED, EXHAUSTED, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="prospect")

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'))
    type = Column(String, nullable=False) # EMAIL_SENT, EMAIL_OPENED, LINK_CLICKED, REPLY_RECEIVED
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    prospect = relationship("Prospect", back_populates="interactions")

def get_engine(db_path='sqlite:///prospects.db'):
    return create_engine(db_path)

def init_db(engine):
    Base.metadata.create_all(engine)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
