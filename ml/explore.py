import pandas as pd
import numpy as np

df = pd.read_csv("dataset/credit_risk_dataset.csv")

print("=== SHAPE ===")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

print("\n=== COLUMNS & TYPES ===")
print(df.dtypes)

print("\n=== FIRST 5 ROWS ===")
print(df.head())

print("\n=== TARGET: loan_status ===")
print(df["loan_status"].value_counts())
print(f"Default rate: {df['loan_status'].mean()*100:.1f}%")

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== NUMERIC STATS ===")
print(df.describe())