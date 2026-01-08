# Data Science Portfolio

A collection of personal projects demonstrating data science, software engineering, and AI integration skills.

## Projects Overview

### 1. [AI Agent Image & Video Generation Pipeline](./AI_agent_sample)
An end-to-end automated data pipeline orchestrating multiple AI agents to generate, evaluate, and optimise photography prompts for image and video generation. This repository showcases one complete agent workflow from a larger multi-agent system, demonstrating production-ready data engineering practices including ETL processes, database management, API integration, and workflow automation.

**Key Features:**
- 4-stage ETL pipeline code sample (Generate → Evaluate → Reformat → Image Generation)
- Relational database design with SQLite
- OpenAI API integration (GPT-4o) with rate limiting and exponential backoff
- Replicate API integration for image generation with async task monitoring
- Photography theme system with YAML configurations (wildlife, landscape, aerial, architecture)
- AI-powered iterative quality evaluation and refinement workflow
- Interactive CLI and command-line modes for automation
- Comprehensive pipeline flowchart documentation

**Data Engineering Skills:**
- Multi-stage ETL pipeline with automated data validation
- Session-based state management and pipeline execution tracking
- Error handling, retry logic, and graceful degradation strategies
- Asynchronous programming for concurrent API operations

**Technologies:** Python, OpenAI API, Replicate API, SQLite, YAML, asyncio, Pipeline Architecture

**Co-Authors:** Jennifer Hunter and Claude Code

---

### 2. [Bike Shop Database](./MySQL_db_project)
A MySQL database schema with analytical queries for retail inventory and sales tracking.

**Key Features:**
- Complete relational database design
- Sample data generation
- Business intelligence queries (Q&A format)
- JOINs, aggregations, and analytical SQL

**Technologies:** MySQL, SQL, Database Design, Data Analysis

**Development Note:** Code authored by Jennifer Hunter without AI assistance. README created with AI assistance.

---

### 3. [Bike Shop Management API](./Building_flask_app)
A Flask REST API with command-line client for managing bike shop operations.

**Key Features:**
- RESTful API design with multiple endpoints
- CRUD operations for orders and employees
- MySQL database integration
- Command-line client with formatted output
- Database integrity handling (foreign key constraints)

**Technologies:** Flask, REST APIs, Python, MySQL, Requests library

**Development Note:** Code authored by Jennifer Hunter without AI assistance. README created with AI assistance.

---

### 4. [Monster Battle Game](./Transforming_API_data) (PokéAPI Data Transformation)
A text-based game that fetches and transforms JSON data from PokéAPI to simulate creature battles.

**Key Features:**
- Real-time API data retrieval and transformation
- Interactive command-line gameplay
- Data persistence with text-based logging
- Error handling for API edge cases

**Technologies:** Python, REST APIs, JSON data transformation

**Development Note:** Code authored by Jennifer Hunter without AI assistance. README created with AI assistance.

---

## Skills Demonstrated

**Note:** Skills marked with an asterisk (*) were developed with AI assistance and represent areas where I am building proficiency through AI-augmented learning. These skills reflect my ability to collaborate with AI tools to understand and implement advanced concepts, though independent mastery is still in development.

### Programming Languages
- Python (primary language across all projects)
- SQL (MySQL queries and database design)

### Web Development & APIs
- Flask framework for REST API development
- API endpoint design and implementation
- HTTP methods (GET, POST, DELETE, PUT)
- API consumption with `requests` library
- JSON data handling and transformation

### Database Technologies
- MySQL (relational database design and queries)
- SQLite (application data persistence)
- Database schema design
- Foreign key constraints and data integrity
- SQL aggregations and JOINs
- Query optimisation

### Data Processing & Transformation
- API data extraction and cleaning
- JSON parsing and manipulation
- String processing and data validation
- Data persistence strategies*
- Time series data reshaping and preparation (project coming soon)
- Multi-source data integration (project coming soon)

### Machine Learning & Statistical Analysis (project coming soon)
- Time series forecasting (XGBoost, ARIMA)
- Model selection and evaluation
- Cross-validation techniques (TimeSeriesSplit)
- Feature engineering for temporal data
- Regression analysis (Linear Regression)
- Performance metrics (MAE, RMSE)

### AI & Automation
- LLM/AI integration for content generation*
- Multi-stage pipeline orchestration*
- Subprocess management*
- YAML-based configuration*
- Quality evaluation automation*

### Software Engineering
- Object-oriented programming (classes, inheritance)*
- Modular code architecture
- Error handling and validation
- Command-line argument parsing (argparse)*
- Interactive CLI development
- File I/O operations*
- Security best practices (input validation, path sanitization, API key management)*

### Development Tools & Practices
- Git version control
- Virtual environments*
- Dependency management*
- Documentation (docstrings, README files)
- Code organisation and project structure*

### Problem Solving
- API rate limiting and error handling*
- Database constraint management
- User input validation*
- Edge case handling*
- Real-time data processing*

---

## Setup & Installation

Each project contains its own README with specific setup instructions. Generally, you'll need:

- Python 3.10+
- MySQL (for database projects)
- API keys for AI projects (OpenAI, Replicate)
- Project-specific dependencies (see individual READMEs)

Install core dependencies:
```bash
# Web/API projects
pip install flask requests tabulate mysql-connector-python

# AI Agent project
pip install openai replicate python-dotenv Pillow pyyaml openai-agents
```

---

## Repository Structure

```
Data_Science_Portfolio/
├── AI_agent_sample/             # 1. AI Image Generation Pipeline
├── MySQL_db_project/            # 2. Bike Shop Database
├── Building_flask_app/          # 3. Bike Shop Management API
└── Transforming_API_data/       # 4. Monster Battle Game
```

---
