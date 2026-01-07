# AI Agent Automation Pipeline

### Authors: Jennifer Hunter and Claude Code (Anthropic)

An end-to-end automated data pipeline orchestrating multiple AI agents to generate, evaluate, and optimize photography prompts for image generation. This repository showcases one complete agent workflow from a larger multi-agent system, demonstrating production-ready data engineering practices including ETL processes, database management, API integration, and workflow automation.

> **Note:** This project represents a single agent pipeline extracted from a larger multi-agent orchestration system. It demonstrates the architecture, data flow, and coordination patterns applicable to complex multi-agent workflows.

---

## 📊 Full Pipeline Documentation

**For a comprehensive view of the complete pipeline architecture, including detailed Mermaid flowcharts for all stages, decision logic, database schemas, and data flows, see:**

### **[PIPELINE_FLOWCHART_DOCUMENTATION.md](./PIPELINE_FLOWCHART_DOCUMENTATION.md)**

This document contains visual flowcharts covering:
- Complete pipeline orchestration and stage transitions
- Photo and video quality evaluation workflows
- Caption generation and hashtag strategy flows
- Queue management and publishing workflows
- Database schema relationships
- Error handling and retry logic
- Slack notification integration

---

## Data Science Skills Demonstrated

### Data Engineering & Pipeline Architecture
- Multi-stage ETL pipeline with 4 automated stages (Generate → Evaluate → Transform → Output)
- Relational database design with SQLite (5-table schema with foreign key constraints)
- Automated data validation and quality control workflows
- Session-based state management and pipeline execution tracking
- Error handling, retry logic, and graceful degradation strategies

### API Integration & External Data Sources
- OpenAI API integration (GPT-4o) with rate limiting and exponential backoff
- Replicate API integration for image generation with async task monitoring
- RESTful API consumption with request/response validation
- Concurrent API calls using Python async/await patterns

### Data Processing & Transformation
- Text processing with regex-based parsing, cleaning, and optimization
- Data format conversion (detailed prompts → generator-optimized prompts)
- Metadata extraction and enrichment throughout pipeline stages
- Compression ratio analysis and character count optimization

### Database Management & SQL
- Schema design for workflow tracking (sessions, prompts, evaluations, reformats, images)
- CRUD operations with parameterized queries and SQL injection prevention
- Complex JOINs for cross-table analytics and reporting
- Database indexing and query optimization for performance
- Session filtering and timestamp-based data retrieval

### Python Programming & Software Engineering
- Object-oriented design with separation of concerns
- Asynchronous programming for concurrent API operations
- Configuration management using YAML with dynamic theme loading
- Security best practices: input validation, path sanitization, API key management
- Type hints, comprehensive docstrings, and PEP 8 compliance

### Automation & Orchestration
- Batch processing with configurable parameters
- Interactive CLI with input validation and user-friendly menus
- Command-line argument parsing for scriptable workflows
- Real-time progress tracking and execution summaries
- Automated logging and monitoring of pipeline execution

## Technical Architecture

```
Stage 1: Prompt Generation (text_generation/create_prompts.py)
   ↓ GPT-4o generates creative prompts from YAML theme configs
   ↓ Stores raw prompts in database with metadata

Stage 2: Quality Evaluation (evaluation/prompt_judge.py)
   ↓ AI-powered iterative refinement and approval workflow
   ↓ Tracks evaluation scores, feedback, and iteration history

Stage 3: Format Optimization (evaluation/reformatter.py)
   ↓ Converts detailed prompts to generator-optimized format
   ↓ Calculates compression ratios and tracks transformations

Stage 4: Image Generation (image_generation/image_generator.py)
   ↓ Generates images via Replicate API (Flux model)
   ↓ Downloads, validates, and stores images with metadata
```

## Database Schema

**pipeline_sessions** - Session-level tracking with execution statistics
**generated_prompts** - Raw prompts with theme, approach, and variation metadata  
**prompt_evaluations** - Iterative refinement history with scores and feedback
**reformatted_prompts** - Optimized prompts with compression metrics
**generated_images** - Final images with generation metadata and file paths

Foreign key relationships ensure referential integrity across all pipeline stages.

## Theme Selection Rationale

The four included YAML themes (wildlife, landscape, aerial, architecture) were chosen as test cases for their data science validation properties:

**Wildlife Photography:**
- **High variability testing** - Animal subjects with diverse features (fur, feathers, scales) test model's ability to handle complex texture generation
- **Behavioral authenticity** - Natural poses and habitat context validate compositional understanding
- **Edge case detection** - Species-specific characteristics test prompt specificity and detail handling

**Landscape Photography:**
- **Multi-element composition** - Tests foreground/midground/background depth handling
- **Environmental complexity** - Weather conditions, seasonal variations, and lighting scenarios validate atmospheric understanding
- **Scale diversity** - From macro nature details to panoramic vistas tests dynamic range capabilities

**Aerial Photography:**
- **Perspective validation** - Bird's-eye views test spatial reasoning and geometric pattern recognition
- **Scale comprehension** - Geographic features at varying altitudes validate size and proportion understanding
- **Pattern detection** - Natural formations and topographic textures test structural composition

**Architecture Photography:**
- **Geometric precision** - Structural lines and symmetry validate mathematical accuracy
- **Material rendering** - Diverse surfaces (glass, concrete, metal) test texture and reflection handling
- **Technical specifications** - Professional photography requirements (lens choice, aperture) validate equipment understanding

These themes provide comprehensive coverage of photographic domains, enabling rigorous testing of prompt quality, model performance, and pipeline robustness across diverse visual scenarios.

## Technologies & Libraries

- **Python 3.7+** - Core programming language
- **SQLite** - Relational database for pipeline tracking (portable to PostgreSQL/MySQL)
- **OpenAI API** - GPT-4o for prompt generation and evaluation
- **Replicate API** - Flux-Krea-Dev model for image generation  
- **YAML** - Configuration management for theme definitions
- **asyncio** - Asynchronous API operations and concurrent processing
- **argparse** - CLI argument parsing for automation
- **pathlib** - Cross-platform file path handling
- **requests** - HTTP client for API integration
- **Pillow** - Image validation and processing

## Setup & Usage

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
```bash
# Copy template and add API keys
cp config/.env.example config/.env
# Edit config/.env with your:
#   OPENAI_API_KEY
#   REPLICATE_API_TOKEN
```

### Running the Pipeline

**Interactive Mode:**
```bash
python main.py
```

**Command-Line Mode:**
```bash
python main.py --session-id wildlife_session --theme wildlife
```

**Run Specific Stages:**
```bash
python main.py --session-id test --stages judge,reformat
```

## Project Structure

```
ai_agent_automation/
├── main.py                    # Pipeline orchestrator with CLI
├── database/
│   ├── database_utils.py      # Database manager (CRUD operations)
│   └── security_utils.py      # Input validation and sanitization
├── text_generation/
│   └── create_prompts.py      # Stage 1: Prompt generation with GPT-4o
├── evaluation/
│   ├── prompt_judge.py        # Stage 2: Quality evaluation workflow
│   ├── reformatter.py         # Stage 3: Format optimization
│   └── themes/                # YAML-based theme configuration system
│       ├── theme_loader.py    # Dynamic theme loading and caching
│       ├── base_theme.py      # Theme class definitions
│       └── definitions/       # YAML theme files
│           ├── wildlife.yaml
│           ├── landscape.yaml
│           ├── aerial.yaml
│           └── architecture.yaml
├── image_generation/
│   └── image_generator.py     # Stage 4: Image generation via Replicate API
├── config/
│   └── .env.example           # Environment variable template
└── requirements.txt           # Pinned Python dependencies
```

## Data Pipeline Features

- **Session Management** - Unique session IDs for tracking and reproducibility
- **Error Recovery** - Graceful handling of API failures with exponential backoff
- **Progress Tracking** - Real-time status updates and execution summaries  
- **Data Persistence** - All intermediate results stored in relational database
- **Audit Trail** - Complete history of prompts, evaluations, and transformations
- **Reproducibility** - Session-based replay and analysis capabilities
- **Scalability** - Batch processing with configurable parallelization

## Portfolio Highlights

This project demonstrates data engineering and data science skills applicable to:

- **ETL Development** - Multi-stage data transformation pipelines with validation
- **API Integration** - Production-ready integration with external AI services
- **Database Design** - Relational schema for complex workflow tracking
- **Workflow Automation** - Orchestrated multi-agent systems with error handling
- **Quality Assurance** - Automated validation and iterative refinement processes
- **Software Engineering** - Clean code architecture with security best practices

## Analytics Capabilities

The database schema supports analytical queries including:
- Success rates by theme and evaluation iteration
- Prompt length optimization analysis (compression ratios)
- Image generation success/failure rates
- Session duration and throughput metrics
- Comparative analysis across themes and approaches

## Notes

- Written as a portfolio project demonstrating data engineering and AI orchestration skills
- Uses SQLite for portability; schema design supports migration to PostgreSQL/MySQL
- Security-focused with input validation, path sanitization, and API key management
- Follows Python best practices: type hints, docstrings, PEP 8 style guide
- Designed for scalability: easily extensible to additional pipeline stages or themes

## Important Disclaimer

**AI-Assisted Development:** This codebase was developed with the assistance of AI coding tools (Claude Code by Anthropic). While the code demonstrates professional software engineering practices and has been reviewed for functionality and security, **detailed code review and testing would be necessary before any commercial implementation or production deployment**.

Key considerations for production use:
- Comprehensive unit and integration testing
- Security audit of API key management and data handling
- Load testing for concurrent API operations
- Error handling validation under various failure scenarios
- Compliance review for data privacy and API terms of service
- Performance optimization for production-scale workloads

This project is intended for educational and portfolio demonstration purposes.