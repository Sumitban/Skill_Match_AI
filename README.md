# Skill Match AI

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.104%2B-green)
![MongoDB](https://img.shields.io/badge/mongodb-4.6%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Automated resume screening and candidate ranking using NLP-driven machine learning. This system leverages semantic similarity, GitHub profile analysis, and machine learning to identify top candidates for job positions.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **🔍 Resume Parsing**: Automatic extraction of text, skills, and links from PDF resumes
- **🧠 Semantic Analysis**: Uses sentence transformers for semantic similarity matching
- **👤 GitHub Integration**: Analyzes GitHub profiles for technical skills and contributions
- **📊 Feature Engineering**: Extracts 9 key features including similarity scores and GitHub metrics
- **⚖️ Baseline Ranking**: Weighted scoring algorithm for candidate ranking
- **📈 ML Training**: XGBoost model training with HR feedback for continuous improvement
- **💾 MongoDB Storage**: Persistent storage of jobs, candidates, and rankings
- **🔐 Type Safe**: Full type hints for better code reliability
- **📝 Comprehensive Logging**: Structured logging for debugging and monitoring
- **✅ Error Handling**: Specific exception handling with meaningful error messages

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI REST API                      │
├─────────────────────────────────────────────────────────┤
│  /jobs  │  /candidates  │  /rank  │  /feedback          │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼───┐  ┌───▼──────┐  │
    │ Jobs  │  │Candidates├──┤
    │Service│  │ Service  │  │
    └───┬───┘  └──────────┘  │
        │         ┌──────────┘
        │         │
    ┌───▼─────────▼────────────────────────┐
    │    Feature Engineering Pipeline      │
    │  ┌───────────────────────────────┐   │
    │  │ Resume Ingestion/Parsing      │   │
    │  │ - PDF extraction              │   │
    │  │ - Link extraction             │   │
    │  │ - Section detection           │   │
    │  └───────────────────────────────┘   │
    │  ┌───────────────────────────────┐   │
    │  │ GitHub Analysis               │   │
    │  │ - Repository metrics          │   │
    │  │ - Language distribution       │   │
    │  │ - README aggregation          │   │
    │  └───────────────────────────────┘   │
    │  ┌───────────────────────────────┐   │
    │  │ Feature Builder               │   │
    │  │ - Similarity computation      │   │
    │  │ - Feature vectorization       │   │
    │  └───────────────────────────────┘   │
    └────────────┬─────────────────────────┘
                 │
        ┌────────▼────────┐
        │   Ranker        │
        │ - Baseline      │
        │ - ML-based      │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │    MongoDB      │
        │  - Jobs         │
        │  - Candidates   │
        │  - Rankings     │
        └─────────────────┘
```

## 📦 Prerequisites

- **Python 3.9+**
- **MongoDB 4.6+**
- **Git**
- **Virtual Environment** (recommended)

### External Services

- [GitHub API Token](https://docs.github.com/en/authentication/keeping-your-data-secure/creating-a-personal-access-token) (for GitHub profile analysis)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Skill_Match_AI.git
cd Skill_Match_AI
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv mlenv
mlenv\Scripts\activate

# Linux/macOS
python3 -m venv mlenv
source mlenv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r Backened/requirement.txt
```

### 4. Set Up MongoDB

```bash
# Using Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
# Visit: https://docs.mongodb.com/manual/installation/
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# Database Configuration
MONGO_URL=mongodb://localhost:27017/
DATABASE_NAME=skill_match_AI

# GitHub API Configuration
GITHUB_API_KEY=your_github_personal_access_token_here

# Embedding Model
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Model Configuration
MODEL_PATH=model.pkl

# Security (optional)
API_KEYS=your_api_key_1,your_api_key_2
```

### Configuration File

Key settings are managed in `Backened/app/config.py`:

- **Weights**: Resume (0.4), Skills (0.3), GitHub (0.2), Experience (0.1)
- **Thresholds**: Confidence threshold (0.6), min skill length (30 chars)
- **Model Parameters**: XGBoost estimators (100), max depth (4), learning rate (0.1)

## 🏃 Quick Start

### 1. Start the Server

```bash
cd Backened
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-04T10:00:00"
}
```

## 📚 API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health check |
| POST | `/jobs` | Create job posting |
| POST | `/candidates` | Process candidate resume |
| GET | `/candidates/{job_id}` | Get ranked candidates |
| POST | `/rank/{job_id}` | Rank candidates for job |
| POST | `/feedback` | Submit HR feedback |

### Detailed Endpoint Documentation

#### 1. Create Job

**Request:**
```bash
POST /jobs
Content-Type: application/json

{
  "job_id": "job_001",
  "title": "Senior Python Developer",
  "raw_text": "We are looking for a senior Python developer with 5+ years of experience..."
}
```

**Response (201 Created):**
```json
{
  "job_id": "job_001",
  "title": "Senior Python Developer",
  "message": "Job created successfully"
}
```

#### 2. Process Candidate

**Request:**
```bash
POST /candidates
Content-Type: application/json

{
  "job_id": "job_001",
  "resume_path": "/path/to/resume.pdf"
}
```

**Response (201 Created):**
```json
{
  "candidate_id": "507f1f77bcf86cd799439011",
  "job_id": "job_001",
  "message": "Candidate processed successfully"
}
```

#### 3. Get Ranked Candidates

**Request:**
```bash
GET /candidates/job_001
```

**Response (200 OK):**
```json
{
  "job_id": "job_001",
  "candidates": [
    {
      "id": "507f1f77bcf86cd799439011",
      "ranking": {
        "prediction_score": 0.85,
        "rank_position": 1,
        "hr_decision": null
      }
    },
    {
      "id": "507f1f77bcf86cd799439012",
      "ranking": {
        "prediction_score": 0.72,
        "rank_position": 2,
        "hr_decision": null
      }
    }
  ],
  "count": 2
}
```

#### 4. Rank Candidates

**Request:**
```bash
POST /rank/job_001
```

**Response (200 OK):**
```json
{
  "job_id": "job_001",
  "message": "Ranking complete",
  "count": 5
}
```

#### 5. Submit Feedback

**Request:**
```bash
POST /feedback
Content-Type: application/json

{
  "candidate_id": "507f1f77bcf86cd799439011",
  "decision": 1
}
```

**Response (200 OK):**
```json
{
  "candidate_id": "507f1f77bcf86cd799439011",
  "message": "Feedback recorded successfully"
}
```

## 💡 Usage Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a job
job_response = requests.post(
    f"{BASE_URL}/jobs",
    json={
        "job_id": "python_dev_001",
        "title": "Senior Python Developer",
        "raw_text": "Looking for experienced Python developer..."
    }
)
print(job_response.json())

# Process candidates
candidate_response = requests.post(
    f"{BASE_URL}/candidates",
    json={
        "job_id": "python_dev_001",
        "resume_path": "resumes/john_doe.pdf"
    }
)
candidate_id = candidate_response.json()["candidate_id"]

# Rank candidates
ranking_response = requests.post(
    f"{BASE_URL}/rank/python_dev_001"
)
print(ranking_response.json())

# Get ranked list
candidates_response = requests.get(
    f"{BASE_URL}/candidates/python_dev_001"
)
print(candidates_response.json())

# Submit feedback for training
requests.post(
    f"{BASE_URL}/feedback",
    json={
        "candidate_id": candidate_id,
        "decision": 1  # 1=Selected, 0=Rejected
    }
)
```

### Bash Example (cURL)

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Create job
curl -X POST "$BASE_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "dev_001",
    "title": "Developer",
    "raw_text": "Job description here..."
  }'

# Process candidates
curl -X POST "$BASE_URL/candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "dev_001",
    "resume_path": "/path/to/resume.pdf"
  }'

# Rank candidates
curl -X POST "$BASE_URL/rank/dev_001"

# Get rankings
curl "$BASE_URL/candidates/dev_001"
```

## 📁 Project Structure

```
Skill_Match_AI/
├── Backened/
│   ├── requirement.txt          # Python dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── api/
│   │   │   ├── main.py          # FastAPI application
│   │   │   └── schemas.py       # Request/response schemas
│   │   ├── embeddings/
│   │   │   ├── embedding_model.py
│   │   │   └── similarity.py
│   │   ├── exception/
│   │   │   └── resume_exception.py
│   │   ├── features/
│   │   │   └── feature_builder.py
│   │   ├── github/
│   │   │   ├── github_client.py
│   │   │   └── github_features.py
│   │   ├── ingestion/
│   │   │   ├── resume_ingestor.py
│   │   │   ├── section_detector.py
│   │   │   └── section_confidence.py
│   │   ├── jobs/
│   │   │   └── job_service.py
│   │   ├── ml/
│   │   │   ├── trainer.py
│   │   │   └── predictor.py
│   │   ├── ranking/
│   │   │   ├── baseline_ranker.py
│   │   │   └── feedback_service.py
│   │   ├── storage/
│   │   │   ├── mongodb.py
│   │   │   ├── candidate_repo.py
│   │   │   └── jobs.py
│   │   └── utils/
│   │       ├── logger.py
│   │       ├── pdf_utils.py
│   │       └── text_utils.py
│   └── logs/
│       └── app.log
├── tests/
│   ├── embeddings/
│   ├── features/
│   ├── github/
│   ├── ingestion/
│   ├── ranking/
│   └── pipeline/
├── data/
│   ├── sample_resumes/
│   └── mock_github_playloads/
├── docs/
│   ├── architecture.md
│   ├── role_definition.md
│   └── scoring_philosphy.md
├── .env.example
├── .gitignore
├── README.md
<br/> ├── LICENSE
└── pyproject.toml
```

## 🔧 Development

### Code Style

The project follows PEP 8 standards:

```bash
# Format code with Black
black Backened/

# Check style with Flake8
flake8 Backened/

# Type checking with Mypy
mypy Backened/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement changes with proper type hints and docstrings
3. Add logging statements for debugging
4. Write tests in `/tests` directory
5. Submit pull request

## ✅ Testing

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/embeddings/test_embedding_model.py

# Run with coverage
pytest --cov=Backened tests/

# Run with verbose output
pytest -v tests/
```

### Test Coverage

Current coverage targets:
- Unit tests: > 80%
- Integration tests: > 60%
- Critical paths: 100%

## 🐛 Troubleshooting

### MongoDB Connection Issues

**Error**: `Could not connect to MongoDB`

**Solution**:
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Or with Docker
docker ps | grep mongodb
docker start mongodb
```

### Empty Resume Field Error

**Error**: `No text is extracted and the output is empty`

**Solution**:
- Ensure PDF file is not corrupted
- Check file permissions
- Try converting PDF to text first

### GitHub API Rate Limiting

**Error**: `GitHub API rate limit exceeded`

**Solution**:
- Generate a new GitHub token
- Update `.env` file with token
- Use authenticated requests for higher limits

### Model Not Found

**Error**: `FileNotFoundError: model.pkl not found`

**Solution**:
```bash
# Train the model first
python -c "from Backened.app.ml.trainer import ModelTrainer; m = ModelTrainer(); m.train('job_id')"
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Built with ❤️ using FastAPI, MongoDB, and Machine Learning**
