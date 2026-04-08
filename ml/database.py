import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://loanuser:loanpass@db:5432/loandb")

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base         = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id                         = Column(Integer, primary_key=True, index=True)
    person_age                 = Column(Integer)
    person_income              = Column(Integer)
    person_home_ownership      = Column(String)
    person_emp_length          = Column(Float)
    loan_intent                = Column(String)
    loan_grade                 = Column(String)
    loan_amnt                  = Column(Integer)
    loan_int_rate              = Column(Float)
    loan_percent_income        = Column(Float)
    cb_person_default_on_file  = Column(String)
    cb_person_cred_hist_length = Column(Integer)
    risk_probability           = Column(Float)
    decision                   = Column(String)
    created_at                 = Column(DateTime, server_default=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)