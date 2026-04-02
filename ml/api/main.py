import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.model import predict, _model, scaler, encoders

#Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

#App
app = FastAPI(title="Loan Risk API", version="1.0")

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

#Stats counter
stats = {"total": 0, "risky": 0, "safe": 0, "errors": 0}

#Schemas
class ApplicantIn(BaseModel):
    person_age:                  int
    person_income:               int
    person_home_ownership:       str   # MORTGAGE | OWN | RENT | OTHER
    person_emp_length:           float
    loan_intent:                 str   # EDUCATION | MEDICAL | VENTURE | PERSONAL | HOMEIMPROVEMENT | DEBTCONSOLIDATION
    loan_grade:                  str   # A | B | C | D | E | F | G
    loan_amnt:                   int
    loan_int_rate:               float
    loan_percent_income:         float
    cb_person_default_on_file:   str   # Y | N
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
    start = time.time()
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
        assert _model is not None, "Model not loaded"
        assert scaler is not None, "Scaler not loaded"
        assert encoders is not None, "Encoders not loaded"
        return {
            "status":   "healthy",
            "model":    "loaded",
            "scaler":   "loaded",
            "encoders": "loaded"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/metrics")
def metrics():
    total = stats["total"]
    return {
        "total_predictions": total,
        "risky":             stats["risky"],
        "safe":              stats["safe"],
        "errors":            stats["errors"],
        "risky_rate":        f"{round(stats['risky'] / total * 100, 1)}%" if total > 0 else "N/A",
    }


@app.post("/predict", response_model=PredictionOut)
def predict_risk(applicant: ApplicantIn):
    try:
        result = predict(applicant.model_dump())
        stats["total"] += 1
        stats[result["decision"].lower()] += 1
        logger.info(
            f"Prediction → {result['decision']} "
            f"(prob={result['risk_probability']}) "
            f"age={applicant.person_age} income={applicant.person_income} "
            f"grade={applicant.loan_grade}"
        )
        return result
    except ValueError as e:
        stats["errors"] += 1
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal prediction error")


@app.post("/predict/batch")
def predict_batch(batch: BatchIn):
    results = []
    for i, applicant in enumerate(batch.applicants):
        try:
            result = predict(applicant.model_dump())
            stats["total"] += 1
            stats[result["decision"].lower()] += 1
            results.append({"index": i, "status": "ok", **result})
        except ValueError as e:
            stats["errors"] += 1
            results.append({"index": i, "status": "error", "detail": str(e)})
        except Exception as e:
            stats["errors"] += 1
            results.append({"index": i, "status": "error", "detail": "Prediction failed"})
    logger.info(f"Batch prediction → {len(batch.applicants)} applicants processed")
    return {"count": len(batch.applicants), "results": results}