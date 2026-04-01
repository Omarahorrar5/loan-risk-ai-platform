import numpy as np
import torch
import torch.nn as nn
import joblib, os

SAVE_DIR  = os.path.join(os.path.dirname(__file__), "..", "saved_models")
THRESHOLD = 0.4

class MLP(nn.Module):
    def __init__(self, in_features, hidden_sizes):
        super().__init__()
        layers = []
        prev = in_features
        for h in hidden_sizes:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(0.3)]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(1)

FEATURE_ORDER = [
    "person_age", "person_income", "person_home_ownership",
    "person_emp_length", "loan_intent", "loan_grade", "loan_amnt",
    "loan_int_rate", "loan_percent_income", "cb_person_default_on_file",
    "cb_person_cred_hist_length"
]

CATEGORICAL_COLS = [
    "person_home_ownership", "loan_intent",
    "loan_grade", "cb_person_default_on_file"
]

# ── Load once at startup ──────────────────────────────────────────────────────
scaler   = joblib.load(os.path.join(SAVE_DIR, "scaler.pkl"))
encoders = joblib.load(os.path.join(SAVE_DIR, "encoders.pkl"))

_model = MLP(in_features=11, hidden_sizes=[256, 128, 64, 32])
_model.load_state_dict(torch.load(os.path.join(SAVE_DIR, "mlp_model.pth"),
                                   map_location="cpu"))
_model.eval()


def predict(data: dict) -> dict:
    data = data.copy()

    # Encode categoricals
    for col in CATEGORICAL_COLS:
        le  = encoders[col]
        val = data[col].upper()
        if val not in le.classes_:
            raise ValueError(f"Unknown value '{val}' for '{col}'. "
                             f"Valid: {list(le.classes_)}")
        data[col] = int(le.transform([val])[0])

    # Build feature vector in correct order
    x = np.array([[data[f] for f in FEATURE_ORDER]], dtype=np.float32)

    # Scale
    x = scaler.transform(x).astype(np.float32)

    # Inference
    with torch.no_grad():
        logit = _model(torch.from_numpy(x))
        prob  = torch.sigmoid(logit).item()

    return {
        "risk_probability": round(prob, 4),
        "decision":         "RISKY" if prob >= THRESHOLD else "SAFE",
        "threshold":        THRESHOLD
    }