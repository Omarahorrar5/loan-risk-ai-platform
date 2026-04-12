```markdown
# Loan Risk AI Platform

![CI/CD](https://github.com/omarahorrar/loan-risk-ai-platform/actions/workflows/ci-cd.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-hub-blue?logo=docker)
![AWS](https://img.shields.io/badge/deployed-AWS%20EC2-orange?logo=amazonaws)
![Terraform](https://img.shields.io/badge/infra-terraform-purple?logo=terraform)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)
![PyTorch](https://img.shields.io/badge/model-pytorch-red?logo=pytorch)

End-to-end MLOps platform that predicts credit loan risk using a neural network, served via a REST API, containerized with Docker, deployed on AWS EC2, and delivered through a full CI/CD pipeline — built as a portfolio project to demonstrate DevOps and MLOps practices.

---

## Architecture

```
Developer → git push → GitHub Actions → Docker Hub → AWS EC2
                           │
                    pytest → build → push
                                         │
                                    EC2 (Terraform)
                                    ├── nginx + React  :80
                                    ├── FastAPI + MLP  :8000
                                    └── PostgreSQL     :5432
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | PyTorch MLP — trained on 32k credit risk records |
| Backend | FastAPI — REST API with input validation and logging |
| Frontend | React + Vite — served via nginx |
| Database | PostgreSQL — predictions persisted across sessions |
| Containers | Docker + docker-compose |
| CI/CD | GitHub Actions — test → build → push to Docker Hub |
| Infrastructure | Terraform — AWS EC2, VPC, subnets, security groups |
| Registry | Docker Hub |

---

## Features

- Credit risk prediction (SAFE / RISKY) with probability score
- Batch prediction endpoint — multiple applicants in one request
- Real-time dashboard with metrics, charts, and prediction history
- Data persisted in PostgreSQL — survives container restarts
- Automated CI/CD — every push triggers tests and rebuilds Docker images
- Infrastructure as Code — one command to provision and deploy on AWS
- nginx reverse proxy with React Router support

---

## Quick Start

### Prerequisites

- Docker and docker-compose installed
- AWS CLI configured (for deployment)
- Terraform installed (for deployment)

### Run locally

```bash
git clone https://github.com/omarahorrar/loan-risk-ai-platform
cd loan-risk-ai-platform
docker compose pull
docker compose up -d
```

Open **http://localhost**

### Deploy to AWS

```bash
cd infra
terraform init
terraform apply
```

Terraform provisions the EC2 instance, installs Docker, pulls the images from Docker Hub, and starts the full stack automatically. The public IP is printed in the outputs.

### Destroy infrastructure

```bash
cd infra
terraform destroy
```

---

## Project Structure

```
loan-risk-ai-platform/
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # GitHub Actions pipeline
├── frontend/
│   ├── src/
│   │   ├── api/              # axios client
│   │   ├── components/       # Header, StatCard, ProbBar, HistoryTable, ResultPanel
│   │   └── pages/            # Predict, Dashboard
│   ├── nginx.conf            # nginx config with React Router support
│   └── Dockerfile            # multi-stage build (node → nginx)
├── ml/
│   ├── api/
│   │   ├── main.py           # FastAPI routes and middleware
│   │   └── model.py          # model loading and inference
│   ├── tests/
│   │   └── test_api.py       # pytest test suite (7 tests)
│   ├── saved_models/         # mlp_model.pth, scaler.pkl, encoders.pkl
│   ├── database.py           # SQLAlchemy models and session
│   ├── train.py              # MLP training script
│   ├── preprocess.py         # data cleaning and feature engineering
│   ├── explore.py            # EDA script
│   └── Dockerfile            # Python 3.12 slim + CPU torch
├── terraform/
│   ├── main.tf               # provider, backend (S3 remote state)
│   ├── variables.tf          # all input variables
│   ├── network.tf            # VPC, subnet, IGW, route tables
│   ├── security.tf           # security groups (ports 22, 80, 8000)
│   ├── compute.tf            # EC2 instance + key pair
│   ├── outputs.tf            # IP, DNS, SSH command, URLs
│   └── scripts/
│       └── user_data.sh      # bootstrap: install Docker, pull images, start app
├── docker-compose.yml        # local and production orchestration
└── README.md
```

---

## ML Model

| Property | Value |
|---|---|
| Algorithm | Multi-Layer Perceptron (MLP) |
| Framework | PyTorch |
| Architecture | 11 → 256 → 128 → 64 → 32 → 1 |
| Dataset | 32,581 credit risk records |
| Train / Test split | 80 / 20 |
| ROC-AUC | 0.90 |
| Risky Recall | 79% |
| Decision threshold | 0.4 (optimized for recall over precision) |
| Imbalance handling | pos_weight (78% safe / 22% risky) |
| Epochs | 60 |

The threshold is set to 0.4 instead of 0.5 — in credit risk, missing a risky loan (false negative) is more costly than flagging a safe one (false positive).

---

## CI/CD Pipeline

Every push to `main` triggers the following pipeline in GitHub Actions:

```
1. Checkout code
2. Install Python dependencies
3. Run pytest (7 tests — routes, validation, prediction shape)
      ↓ fails here if tests don't pass — nothing gets deployed
4. Login to Docker Hub
5. Build backend image  → push as omarahorrar/loan-risk-backend:latest + :sha
6. Build frontend image → push as omarahorrar/loan-risk-frontend:latest + :sha
```

Pull requests run tests only — images are only pushed on merge to `main`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Server status |
| GET | `/health` | Model, scaler, encoder status |
| GET | `/metrics` | Total predictions, safe/risky counts, risky rate |
| GET | `/history?limit=50` | Full prediction log from database |
| POST | `/predict` | Single applicant prediction |
| POST | `/predict/batch` | Batch prediction — array of applicants |

### Example request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "person_age": 28,
    "person_income": 45000,
    "person_home_ownership": "RENT",
    "person_emp_length": 3.0,
    "loan_intent": "PERSONAL",
    "loan_grade": "C",
    "loan_amnt": 8000,
    "loan_int_rate": 13.5,
    "loan_percent_income": 0.18,
    "cb_person_default_on_file": "N",
    "cb_person_cred_hist_length": 4
  }'
```

### Example response

```json
{
  "risk_probability": 0.4293,
  "decision": "RISKY",
  "threshold": 0.4
}
```

---

## Infrastructure

Provisioned with Terraform on AWS:

- VPC with public subnet
- Internet Gateway and route tables
- Security group — ports 22 (SSH), 80 (frontend), 8000 (backend)
- EC2 t3.small — Ubuntu 24.04
- Remote Terraform state stored in S3 with versioning
- Bootstrap via `user_data.sh` — zero manual SSH required