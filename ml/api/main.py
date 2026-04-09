import logging
import time
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from api.model import predict, _model, scaler, encoders
from database import SessionLocal, Prediction, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Loan Risk API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Create tables on startup
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    init_db()
    logger.info("Database tables ready")
    yield

app = FastAPI(title="Loan Risk API", version="1.0", lifespan=lifespan)

#Schemas
class ApplicantIn(BaseModel):
    person_age:                  int
    person_income:               int
    person_home_ownership:       str
    person_emp_length:           float
    loan_intent:                 str
    loan_grade:                  str
    loan_amnt:                   int
    loan_int_rate:               float
    loan_percent_income:         float
    cb_person_default_on_file:   str
    cb_person_cred_hist_length:  int

class PredictionOut(BaseModel):
    risk_probability: float
    decision:         str
    threshold:        float

class BatchIn(BaseModel):
    applicants: list[ApplicantIn]

#Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response

#Routes
@app.get("/")
def root():
    return {"status": "ok", "message": "Loan Risk API is running"}


@app.get("/health")
def health():
    try:
        assert _model   is not None
        assert scaler   is not None
        assert encoders is not None
        return {"status": "healthy", "model": "loaded", "scaler": "loaded", "encoders": "loaded"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total = int(db.query(Prediction).count())
    risky = int(db.query(Prediction).filter(Prediction.decision == "RISKY").count())
    safe  = int(db.query(Prediction).filter(Prediction.decision == "SAFE").count())
    return {
        "total_predictions": total,
        "risky":             risky,
        "safe":              safe,
        "errors":            0,
        "risky_rate":        f"{round(risky / total * 100, 1)}%" if total > 0 else "N/A",
    }

@app.get("/history")
def history(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    return [
        {
            "id":               r.id,
            "decision":         r.decision,
            "risk_probability": r.risk_probability,
            "created_at":       r.created_at.isoformat(),
            "form": {
                "person_age":                 r.person_age,
                "person_income":              r.person_income,
                "person_home_ownership":      r.person_home_ownership,
                "person_emp_length":          r.person_emp_length,
                "loan_intent":                r.loan_intent,
                "loan_grade":                 r.loan_grade,
                "loan_amnt":                  r.loan_amnt,
                "loan_int_rate":              r.loan_int_rate,
                "loan_percent_income":        r.loan_percent_income,
                "cb_person_default_on_file":  r.cb_person_default_on_file,
                "cb_person_cred_hist_length": r.cb_person_cred_hist_length,
            }
        }
        for r in rows
    ]


@app.post("/predict", response_model=PredictionOut)
def predict_risk(applicant: ApplicantIn, db: Session = Depends(get_db)):
    try:
        result = predict(applicant.model_dump())

        row = Prediction(**applicant.model_dump(),
                         risk_probability=result["risk_probability"],
                         decision=result["decision"])
        db.add(row)
        db.commit()

        logger.info(f"Prediction → {result['decision']} (prob={result['risk_probability']})")
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal prediction error")


@app.post("/predict/batch")
def predict_batch(batch: BatchIn, db: Session = Depends(get_db)):
    results = []
    for i, applicant in enumerate(batch.applicants):
        try:
            result = predict(applicant.model_dump())
            row    = Prediction(**applicant.model_dump(),
                                risk_probability=result["risk_probability"],
                                decision=result["decision"])
            db.add(row)
            results.append({"index": i, "status": "ok", **result})
        except Exception as e:
            results.append({"index": i, "status": "error", "detail": str(e)})
    db.commit()
    logger.info(f"Batch → {len(batch.applicants)} processed")
    return {"count": len(batch.applicants), "results": results}