from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.model import predict

app = FastAPI(title="Loan Risk API", version="1.0")

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

@app.get("/")
def root():
    return {"status": "ok", "message": "Loan Risk API is running"}

@app.post("/predict", response_model=PredictionOut)
def predict_risk(applicant: ApplicantIn):
    try:
        result = predict(applicant.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))