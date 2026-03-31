# Loan Risk AI Platform

A machine learning system that predicts whether a loan applicant is likely to default,
helping simulate how banks use AI to make credit decisions.

## The Idea

Given a person's financial profile, the system outputs a risk score and a loan decision
(APPROVE or REJECT). The model learns patterns from historical loan data — for example,
that high debt relative to income, a previous default, or a low loan grade are strong
signals of risk.

## The Dataset

Source: Kaggle — Credit Risk Dataset  
32,581 loan applications with the following information per applicant:

- Personal: age, income, home ownership, employment length
- Loan: amount requested, purpose, grade assigned by the bank, interest rate
- Credit history: previous default on file, length of credit history
- Target: `loan_status` — 0 means the loan was repaid, 1 means the person defaulted

Default rate in the dataset is 21.8%, meaning roughly 1 in 5 applicants defaulted.

## Preprocessing

The raw data required several cleaning and preparation steps before it could be fed
into a neural network:

1. **Outlier removal** — removed rows where age was above 100 or employment length
   above 60, as these are clearly data entry errors.

2. **Missing value imputation** — `person_emp_length` had 895 missing values, filled
   with the median. `loan_int_rate` had 3,116 missing values, filled with the mean.

3. **Categorical encoding** — text columns were converted to numbers using
   LabelEncoder: home ownership (RENT/OWN/MORTGAGE/OTHER), loan intent, loan grade
   (A through G), and whether the person had a previous default (Y/N).

4. **Train/test split** — 80% of the data used for training (25,343 rows), 20% for
   testing (6,336 rows). Class balance is consistent across both splits at roughly
   78% safe / 22% risky.

5. **Normalization** — all features scaled using StandardScaler (fit only on training
   data) so that every feature has mean ≈ 0 and standard deviation ≈ 1. This prevents
   large-scale features like income from dominating small-scale ones like age during
   training.