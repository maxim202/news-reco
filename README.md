# News Recommendation Platform


A production-ready, ML-powered news article recommendation system built with modern data engineering best practices.


---

## 2 Table of Contents

- Project Overview

- Architecture

- Quick Start

- Project Structure

- Data Pipeline Stages

- Testing

- API Endpoints

- Docker Deployment

- Technology Stack

- Example Workflows

- Key Design Decisions

- Data Schema

- Running the Application

- Additional Documentation

- Contributing

- License



---

## Project Overview


This is a complete data engineering project demonstrating:


-  Data Ingestion Pipeline - Real-time news collection from APIs

-  Data Processing - Cleaning, transformation, and feature engineering

-  Data Warehouse - SQLite with Star Schema design

-  ML Recommendation System - Content-based recommendations using TF-IDF

-  REST API - FastAPI with analytics endpoints

-  Production Deployment - Docker containerization

-  Comprehensive Testing - 59 unit & integration tests



---

## Architecture

	┌─────────────────────────────────────────────────────────────┐
	│                    News API (External)                      │
	└──────────────────────────┬──────────────────────────────────┘
	                           │
	                           ▼
	┌──────────────────────────────────────────────────────────────┐
	│           Data Ingestion Pipeline (Python)                   │
	│  • News API Client with error handling                       │
	│  • Rate limiting and retries                                 │
	│  • JSON file storage in S3-compatible format                 │
	└──────────────────────────┬──────────────────────────────────┘
	                           │
	                           ▼
	┌──────────────────────────────────────────────────────────────┐
	│           Data Processing Pipeline                           │
	│  • Cleaning (nulls, duplicates)                              │
	│  • Text processing (normalization)                           │
	│  • Feature engineering (word count, images, etc.)            │
	│  • CSV export for warehouse loading                          │
	└──────────────────────────┬──────────────────────────────────┘
	                           │
	                           ▼
	┌──────────────────────────────────────────────────────────────┐
	│        Data Warehouse (SQLite + Star Schema)                 │
	│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐           │
	│  │ dim_source  │  │ dim_author   │  │ dim_time   │           │
	│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘           │
	│         │                 │               │                   │
	│         └─────────────────┼───────────────┘                   │
	│                           │                                   │
	│                      ┌────▼──────┐                            │
	│                      │  fact_    │                            │
	│                      │ articles  │                            │
	│                      └───────────┘                            │
	└──────────────────────┬──────────────────────────────────────┘
	                       │
	        ┌──────────────┴──────────────┐
	        ▼                             ▼
	┌─────────────────────────┐  ┌─────────────────────────┐
	│  ML Recommendation      │  │  Analytics Queries      │
	│  (TF-IDF + Cosine)      │  │  (SQL on Warehouse)     │
	│  • Content-based        │  │  • Articles by source   │
	│  • Similarity scoring   │  │  • Author statistics    │
	└──────────────┬──────────┘  │  • Content distribution │
	              │             └──────────┬──────────────┘
	              └──────────────┬─────────┘
	                             │
	                             ▼
	┌──────────────────────────────────────────────────────────────┐
	│              FastAPI REST Service                            │
	│  • /recommendations/{article_id}                             │
	│  • /recommendations/search                                   │
	│  • /analytics/* endpoints                                    │
	│  • Auto-generated Swagger docs                               │
	└──────────────────────────┬──────────────────────────────────┘
	                           │
	                           ▼
	┌──────────────────────────────────────────────────────────────┐
	│           Docker Container (Production)                      │
	│  • Multi-stage build                                         │
	│  • Health checks                                             │
	│  • Volume mounting for data persistence                      │
	└──────────────────────────────────────────────────────────────┘


---

## Quick Start

Prerequisites

- Python 3.9+

- Git

- Docker (optional, for containerization)

- News API Key (free at newsapi.org)

Installation


1. Clone & Setup


	# Clone repository
	git clone <your-repo-url>
	cd news-recommendation-platform
	
	# Create virtual environment
	python -m venv venv
	source venv/bin/activate  # Windows: venv\Scripts\activate
	
	# Install dependencies
	pip install -r requirements.txt

2. Configure Environment


	# Copy example env file
	cp .env.example .env
	
	# Edit .env and add your NEWS_API_KEY
	nano .env

3. Setup & Populate Warehouse


	# Setup warehouse schema
	python scripts/setup_warehouse.py
	
	# Fetch news data
	python scripts/fetch_news.py
	
	# Process data
	python scripts/process_news.py
	
	# Load into warehouse
	python scripts/load_warehouse.py
	
	# Verify warehouse
	python scripts/analyze_warehouse.py

4. Train ML Model


	python scripts/train_recommender.py

5. Start API


	python scripts/run_api.py

Visit: http://localhost:8000/docs for interactive API docs


---

## Project Structure

	news-recommendation-platform/
	├── src/
	│   ├── ingestion/              # Data collection
	│   │   ├── news_api.py         # News API client
	│   │   └── config.py           # API configuration
	│   ├── processing/             # Data processing
	│   │   ├── cleaner.py          # Data cleaning & features
	│   │   └── transformer.py      # Data transformations
	│   ├── warehouse/              # Data warehouse
	│   │   ├── connection.py       # SQLite connection manager
	│   │   ├── loader.py           # Data loading pipeline
	│   │   ├── queries.py          # Analytical SQL queries
	│   │   └── schema.sql          # Database schema
	│   ├── ml/                     # Machine Learning
	│   │   ├── recommender.py      # Content-based recommender
	│   │   └── trainer.py          # Model training & persistence
	│   └── api/                    # REST API
	│       └── main.py             # FastAPI application
	│
	├── scripts/
	│   ├── fetch_news.py           # News collection
	│   ├── process_news.py         # Data processing
	│   ├── setup_warehouse.py      # Warehouse initialization
	│   ├── load_warehouse.py       # Data loading
	│   ├── analyze_warehouse.py    # Analytics queries
	│   ├── train_recommender.py    # ML model training
	│   └── run_api.py              # API server
	│
	├── tests/
	│   ├── unit/                   # Unit tests
	│   │   ├── test_ingestion.py   # Ingestion tests (10 tests)
	│   │   ├── test_processing.py  # Processing tests (13 tests)
	│   │   ├── test_warehouse.py   # Warehouse tests (8 tests)
	│   │   ├── test_recommender.py # ML tests (13 tests)
	│   │   └── test_api.py         # API tests (11 tests)
	│   └── integration/
	│       └── test_pipeline.py    # Pipeline tests (5 tests)
	│
	├── data/
	│   ├── raw/                    # Raw JSON data from API
	│   ├── processed/              # Cleaned CSV data
	│   ├── models/                 # Trained ML models
	│   └── warehouse.db            # SQLite database
	│
	├── config/
	│   ├── config.yaml             # Application configuration
	│   └── logging_config.py       # Logging setup
	│
	├── docs/
	│   ├── architecture.md         # System architecture
	│   ├── setup.md                # Detailed setup guide
	│   └── api.md                  # API documentation
	│
	├── Dockerfile                  # Container image definition
	├── docker-compose.yml          # Docker Compose configuration
	├── requirements.txt            # Python dependencies
	├── .env.example                # Environment variables template
	├── .gitignore                  # Git ignore rules
	└── README.md                   # This file

Related sections:


- Data Pipeline Stages explains how components interact

- Testing covers the test structure

- Additional Documentation for detailed docs


---

## Data Pipeline Stages

Stage 1: Ingestion

- Fetch articles from News API (newsapi.org)

- Handle rate limiting and errors gracefully

- Store raw JSON in data/raw/

- Batch frequency: Manual (configurable to scheduled)

Stage 2: Processing

- Remove null values and duplicates

- Clean and normalize text

- Extract features:
	- Word count, content length

	- Has image, day of week, hour published


- Export cleaned data to CSV

- Output: data/processed/*.csv

Stage 3: Warehouse Loading

- Load dimensions first (sources, authors, dates)

- Load fact table (articles with foreign keys)

- Star Schema ensures analytical efficiency

- Database: SQLite with indexes

- Rows loaded: ~50-100 per run

Stage 4: ML Training

- Extract features using TF-IDF vectorizer

- Create embedding matrix from content

- Train content-based recommender

- Save model to disk for inference

- Vocabulary size: ~500 top terms

Stage 5: API Serving

- Load pre-trained model on startup

- Expose HTTP endpoints

- Connect to warehouse for analytics

- Auto-generated OpenAPI docs

---

## Testing


The project includes 59 comprehensive tests:


	# Run all tests
	pytest tests/ -v
	
	# Run specific test file
	pytest tests/unit/test_recommender.py -v
	
	# Run with coverage report
	pytest tests/ --cov=src --cov-report=html
	
	# View coverage
	open htmlcov/index.html

Test Coverage

Module	Tests	Type
Ingestion	10	Unit
Processing	13	Unit
Warehouse	8	Unit
ML Recommender	13	Unit
API	11	Unit
Pipeline	5	Integration
Total	59	
Related sections:


- Code Quality for testing approach

- Project Structure for test organization

- Example Workflows for running tests


---

## API Endpoints

Health & Root

	GET /health
	# Returns: {"status": "healthy", "service": "...", "version": "1.0.0"}
	
	GET /
	# Returns: API information and documentation links

Recommendations

	# Get recommendations for an article
	GET /recommendations/{article_id}?n=5
	
	# Search recommendations for custom query
	POST /recommendations/search
	{
	  "query": "machine learning artificial intelligence",
	  "n": 5
	}
	
	# Response:
	{
	  "query_article_id": 1,
	  "recommendations": [
	    {
	      "article_id": 42,
	      "title": "Deep Learning Advances",
	      "similarity_score": 0.87,
	      "source": "Tech News"
	    },
	    ...
	  ],
	  "count": 5
	}

Analytics

	# Warehouse statistics
	GET /analytics/warehouse-stats
	
	# Articles by source
	GET /analytics/articles-by-source
	
	# Top authors
	GET /analytics/articles-by-author?limit=10
	
	# Content distribution
	GET /analytics/content-distribution

Interactive Docs: http://localhost:8000/docs


---

## Docker Deployment

Using Docker

	# Build image
	docker build -t news-recommendation-api:1.0 .
	
	# Run container
	docker run -p 8000:8000 \
	  -e NEWS_API_KEY=your_api_key \
	  -v $(pwd)/data:/app/data \
	  news-recommendation-api:1.0

Using Docker Compose

	# Start services
	docker-compose up
	
	# Stop services
	docker-compose down
	
	# View logs
	docker-compose logs -f api

Features

- Multi-stage build for smaller images

- Health checks for reliability

- Volume mounting for data persistence

- Auto-restart on failure



---

## Technology Stack

Core Technologies

- Language: Python 3.12

- Data Processing: Pandas, NumPy

- Machine Learning: scikit-learn, scipy

- Database: SQLite, SQLAlchemy

- API: FastAPI, Uvicorn, Pydantic

- Testing: pytest, responses

DevOps & Deployment

- Containerization: Docker, Docker Compose

- Version Control: Git

- CI/CD Ready: GitHub Actions compatible

Development Tools

- Code Quality: pytest, black, flake8, mypy

- Documentation: Auto-generated from code

- Logging: Python logging, structured output




---

## Example Workflows

Complete Data Pipeline

	# 1. Fetch fresh data
	python scripts/fetch_news.py
	
	# 2. Process and clean
	python scripts/process_news.py
	
	# 3. Load into warehouse
	python scripts/load_warehouse.py
	
	# 4. Analyze results
	python scripts/analyze_warehouse.py
	
	# Output: Warehouse populated with articles

Model Training & Inference

	# 1. Train recommender
	python scripts/train_recommender.py
	
	# 2. Start API
	python scripts/run_api.py
	
	# 3. In another terminal:
	curl http://localhost:8000/recommendations/0?n=5

Running Tests

	# Full test suite
	pytest tests/ -v
	
	# Specific module
	pytest tests/unit/test_recommender.py -v --tb=short
	
	# With coverage
	pytest tests/ --cov=src --cov-report=term-missing

---

## Key Design Decisions

1. Star Schema for Data Warehouse


Why: Optimizes analytical queries, separates dimensions from facts


	Dimensions: source, author, time
	Fact Table: articles (with FK to dimensions)

2. Content-Based Recommendations


Why: No cold-start problem, interpretable, fast inference


	Algorithm: TF-IDF + Cosine Similarity
	Speed: <10ms per recommendation

3. SQLite for Data Warehouse


Why: Zero-setup, file-based, sufficient for analytical workloads


	Scales to millions of records
	ACID compliance
	Easy backup (single file)

4. FastAPI for REST API


Why: Fast, modern, auto-docs, type validation


	Async support
	Auto-generated OpenAPI/Swagger
	Built-in validation with Pydantic

5. Docker for Deployment


Why: Reproducible, portable, production-ready


	Multi-stage builds
	Health checks
	Volume persistence




---

## Data Schema

Star Schema Design

dim_source

	source_id INT PRIMARY KEY
	source_name TEXT UNIQUE
	created_at TIMESTAMP

dim_author

	author_id INT PRIMARY KEY
	author_name TEXT
	created_at TIMESTAMP

dim_time

	time_id INT PRIMARY KEY
	date TEXT UNIQUE
	year, month, day INT
	day_of_week TEXT
	quarter INT
	is_weekend BOOLEAN

fact_articles (Central fact table)

	article_id INT PRIMARY KEY
	title, description, content TEXT
	url TEXT UNIQUE
	source_id FK → dim_source
	author_id FK → dim_author
	published_time_id FK → dim_time
	content_length, word_count INT
	has_image BOOLEAN
	created_at, updated_at TIMESTAMP


## Code Quality

Testing Approach

- Unit Tests: Test individual components in isolation

- Integration Tests: Test workflows across components

- Mocking: Use mocks for external APIs

- Fixtures: Reusable test data

Code Standards

- Type Hints: Full type annotations

- Docstrings: Module and function documentation

- Error Handling: Graceful failures with logging

- Logging: Structured, searchable log output


## Running the Application

Step-by-Step

	# 1. Activate environment
	source venv/bin/activate
	
	# 2. Ensure setup is done
	python scripts/setup_warehouse.py
	
	# 3. Get data
	python scripts/fetch_news.py
	python scripts/process_news.py
	python scripts/load_warehouse.py
	
	# 4. Train model
	python scripts/train_recommender.py
	
	# 5. Run API
	python scripts/run_api.py
	
	# 6. In browser: http://localhost:8000/docs

Verify It Works

	# Health check
	curl http://localhost:8000/health
	
	# Get recommendations
	curl http://localhost:8000/recommendations/0?n=3
	
	# Search
	curl -X POST http://localhost:8000/recommendations/search \
	  -H "Content-Type: application/json" \
	  -d '{"query": "artificial intelligence and machine learning", "n": 5}'
	
	# Analytics
	curl http://localhost:8000/analytics/warehouse-stats


## Additional Documentation

- Architecture Details: See docs/architecture.md

- Setup Guide: See docs/setup.md

- API Reference: See docs/api.md or http://localhost:8000/docs





## Contributing


This is a portfolio project. For suggestions or improvements:


1. Fork the repository

2. Create a feature branch

3. Make your changes

4. Submit a pull request

---

## License


MIT License - See LICENSE file for details
