import numpy as np
import joblib
import os

SAVE_DIR = os.path.join(os.path.dirname(__file__), "saved_models")

# ── Load everything preprocess.py saved ──────────────────────────────────────
X_train = np.load(os.path.join(SAVE_DIR, "X_train.npy"))
X_test  = np.load(os.path.join(SAVE_DIR, "X_test.npy"))
y_train = np.load(os.path.join(SAVE_DIR, "y_train.npy"))
y_test  = np.load(os.path.join(SAVE_DIR, "y_test.npy"))
scaler  = joblib.load(os.path.join(SAVE_DIR, "scaler.pkl"))
encoders = joblib.load(os.path.join(SAVE_DIR, "encoders.pkl"))

FEATURE_NAMES = [
    "person_age", "person_income", "person_home_ownership",
    "person_emp_length", "loan_intent", "loan_grade", "loan_amnt",
    "loan_int_rate", "loan_percent_income", "cb_person_default_on_file",
    "cb_person_cred_hist_length"
]

# ── 1. Shapes ─────────────────────────────────────────────────────────────────
print("=== SHAPES ===")
print(f"X_train : {X_train.shape}   ← (samples, features)")
print(f"X_test  : {X_test.shape}")
print(f"y_train : {y_train.shape}")
print(f"y_test  : {y_test.shape}")

# ── 2. Class balance ─────────────────────────────────────────────────────────
print("\n=== CLASS BALANCE ===")
for split_name, y in [("Train", y_train), ("Test", y_test)]:
    total   = len(y)
    n_safe  = (y == 0).sum()
    n_risk  = (y == 1).sum()
    print(f"  {split_name}: {n_safe} safe ({n_safe/total*100:.1f}%)  |  "
          f"{n_risk} risky ({n_risk/total*100:.1f}%)")

# ── 3. First 5 rows of X_train (normalized) ──────────────────────────────────
print("\n=== FIRST 5 ROWS — X_train (after normalization) ===")
print(f"{'Feature':<30} {'Row0':>8} {'Row1':>8} {'Row2':>8} {'Row3':>8} {'Row4':>8}")
print("-" * 74)
for i, name in enumerate(FEATURE_NAMES):
    vals = " ".join(f"{X_train[r, i]:>8.3f}" for r in range(5))
    print(f"{name:<30} {vals}")

# ── 4. What normalization actually did ───────────────────────────────────────
print("\n=== SCALER INFO (what each feature was normalized with) ===")
print(f"{'Feature':<30} {'Mean':>10} {'Std':>10}")
print("-" * 52)
for name, mean, std in zip(FEATURE_NAMES, scaler.mean_, scaler.scale_):
    print(f"{name:<30} {mean:>10.3f} {std:>10.3f}")

# ── 5. Encoder mappings ───────────────────────────────────────────────────────
print("\n=== ENCODER MAPPINGS (original label → number) ===")
for col, le in encoders.items():
    mapping = {label: idx for idx, label in enumerate(le.classes_)}
    print(f"  {col}: {mapping}")

# ── 6. Value range check (should be roughly -3 to +3 after normalization) ────
print("\n=== VALUE RANGES after normalization (X_train) ===")
print(f"  Min : {X_train.min():.3f}")
print(f"  Max : {X_train.max():.3f}")
print(f"  Mean: {X_train.mean():.4f}  ← should be ~0.0")
print(f"  Std : {X_train.std():.4f}   ← should be ~1.0")