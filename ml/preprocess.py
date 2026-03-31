import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

#LOAD DATA
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "dataset", "credit_risk_dataset.csv")

df = pd.read_csv(DATA_PATH)

print("Data loaded")

#CLEAN DATA

# Remove unrealistic values
df = df[df["person_age"] < 100]
df = df[df["person_emp_length"] < 60]

# Fill missing values
df["person_emp_length"] = df["person_emp_length"].fillna(df["person_emp_length"].median())
df["loan_int_rate"] = df["loan_int_rate"].fillna(df["loan_int_rate"].mean())

print("Data cleaned")

#ENCODE CATEGORICAL FEATURES

categorical_cols = [
    "person_home_ownership",
    "loan_intent",
    "loan_grade",
    "cb_person_default_on_file"
]

encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

print("Categorical features encoded")

#SPLIT FEATURES / TARGET

X = df.drop("loan_status", axis=1)
y = df["loan_status"]

#TRAIN / TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Data split")

#NORMALIZATION

scaler = StandardScaler()

# Fit ONLY on train
X_train_scaled = scaler.fit_transform(X_train)

# Apply to test
X_test_scaled = scaler.transform(X_test)

print("Data normalized")

#SAVE OBJECTS

SAVE_DIR = os.path.join(BASE_DIR, "saved_models")
os.makedirs(SAVE_DIR, exist_ok=True)

# Save scaler
joblib.dump(scaler, os.path.join(SAVE_DIR, "scaler.pkl"))

# Save encoders
joblib.dump(encoders, os.path.join(SAVE_DIR, "encoders.pkl"))

print("Scaler and encoders saved")

# 8. SAVE PROCESSED DATA

np.save(os.path.join(SAVE_DIR, "X_train.npy"), X_train_scaled)
np.save(os.path.join(SAVE_DIR, "X_test.npy"), X_test_scaled)
np.save(os.path.join(SAVE_DIR, "y_train.npy"), y_train)
np.save(os.path.join(SAVE_DIR, "y_test.npy"), y_test)

print("Processed data saved")

print("Preprocessing completed!")