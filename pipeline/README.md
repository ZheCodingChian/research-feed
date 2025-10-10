# arXiv AI Research Data Pipeline

A comprehensive automated pipeline for discovering, analyzing, and curating high-quality AI research papers from arXiv. This system combines web scraping, natural language processing, machine learning, and intelligent scoring to generate a structured database of the most relevant and impactful research papers in artificial intelligence.

## 🎯 Project Overview

The arXiv AI Research Data Pipeline is a sophisticated content curation system that:

- **Automatically discovers** new AI research papers from arXiv
- **Intelligently filters** papers based on research topic relevance
- **Evaluates paper quality** using advanced LLM-based scoring
- **Enriches content** with author H-index data and detailed analysis
- **Generates structured data** in SQLite database format
- **Runs continuously** via GitHub Actions automation

### Key Features

- 🔍 **Smart Content Discovery**: Targeted scraping of cs.AI and cs.CV categories
- 🧠 **AI-Powered Analysis**: LLM validation and scoring using state-of-the-art models
- 📊 **Quality Assessment**: Multi-dimensional scoring (novelty, impact, recommendation)
- 👥 **Author Impact Analysis**: H-index fetching for research credibility
- 💾 **Structured Data Output**: SQLite database with comprehensive paper metadata
- ⚡ **High Performance**: Parallel processing and intelligent caching
- 🔄 **Robust Automation**: GitHub Actions with error handling and recovery

### Processing Pipeline

The system follows a modular pipeline architecture with 7 distinct stages:

```
┌─────────────────┐
│   1. Scraper    │ ── Fetches papers from arXiv API
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 2. Introduction │ ── Extracts paper introductions
│   Extractor     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  3. Embedding   │ ── Calculates topic similarity scores
│   Similarity    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 4. LLM          │ ── Validates relevance to topics with justification
│   Validation    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 5. LLM Scoring  │ ── Scores paper quality based on recommendation, novelty and potential impact
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 6. H-Index      │ ── Fetches author research impact data
│   Fetching      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 7. Cache        │ ── Cleans old data for efficiency
│   Cleanup       │
└─────────────────┘
         │
         ▼
     database.sqlite
    (structured output)
```

Each stage is fully modular and fault-tolerant, with comprehensive error handling and state persistence.

## 🧩 Core Components

### 1. Paper Data Model (`paper.py`)

The `Paper` class serves as the central data structure that flows through the entire pipeline:

```python
@dataclass
class Paper:
    # Core metadata
    id: str                    # arXiv ID
    title: str                 # Paper title
    authors: List[str]         # Author list
    categories: List[str]      # arXiv categories
    abstract: str              # Paper abstract
    published_date: datetime   # Publication date

    # Processing status tracking
    scraper_status: str        # Scraping state
    intro_status: str          # Introduction extraction state
    embedding_status: str      # Embedding calculation state
    llm_validation_status: str # LLM validation state
    llm_score_status: str      # LLM scoring state
    h_index_status: str        # H-index fetching state

    # Analysis results
    summary: str               # LLM-generated summary
    novelty_score: str         # High/Moderate/Low/None
    impact_score: str          # High/Moderate/Low/Negligible
    recommendation_score: str  # Must Read/Should Read/Can Skip/Ignore
    highest_h_index: int       # Author with highest H-index
```

### 2. Database Layer (`database.py`)

SQLite-based persistence layer providing:
- **Efficient caching** of all processing results
- **Crash recovery** capabilities
- **Incremental processing** support
- **Data consistency** across pipeline restarts

### 3. Configuration Management (`config.py`)

Centralized configuration for all pipeline parameters:
- API endpoints and rate limits
- Processing thresholds and batch sizes
- Retry policies and timeout settings
- Database retention settings

## 📋 Pipeline Modules

### Module 1: arXiv Scraper (`scraper.py`)

**Purpose**: Discovers and fetches new research papers from arXiv API

**Key Features**:
- Intelligent date-based paper discovery
- Category filtering (cs.AI, cs.CV)
- Rate limiting and retry logic
- Comprehensive metadata extraction
- Duplicate detection and handling

**Processing Logic**:
1. Constructs targeted arXiv API queries
2. Fetches papers in configurable batches
3. Extracts metadata (title, authors, abstract, categories)
4. Generates direct access URLs
5. Validates against processing limits

### Module 2: Introduction Extractor (`intro_extractor.py`)

**Purpose**: Extracts introduction sections from LaTeX source files

**Key Features**:
- LaTeX source download and parsing
- Intelligent introduction section detection
- Content cleaning and formatting
- Fallback strategies for extraction failures
- Length limits for processing efficiency

**Processing Logic**:
1. Downloads LaTeX source archives
2. Identifies main document files
3. Parses LaTeX structure for introduction sections
4. Cleans and formats extracted text
5. Handles extraction errors gracefully

### Module 3: Embedding Similarity (`embedding_similarity.py`)

**Purpose**: Calculates semantic similarity between papers and research topics

**Research Topics Covered**:
- **Reinforcement Learning from Human Feedback (RLHF)**
- **Weak Supervision**
- **Diffusion Reasoning**
- **Distributed Training**
- **Datasets and Benchmarks**

**Key Features**:
- OpenAI text-embedding-3-large model
- Batch processing for efficiency
- Topic embedding caching
- Similarity threshold filtering
- Comprehensive error handling

**Processing Logic**:
1. Generates embeddings for paper content
2. Calculates cosine similarity against topic embeddings
3. Identifies highest-scoring topics
4. Filters papers meeting similarity thresholds
5. Caches embeddings for reuse

### Module 4: LLM Validation (`llm_validation.py`)

**Purpose**: Validates paper relevance using Large Language Models

**Key Features**:
- Grok 3 Mini via OpenRouter API
- Parallel processing with rate limiting
- XML-structured response parsing
- Detailed relevance justifications
- Comprehensive error recovery

**Processing Logic**:
1. Builds detailed prompts with paper content
2. Requests relevance assessment for each topic
3. Parses structured XML responses
4. Validates response format and content
5. Updates paper objects with results

### Module 5: LLM Scoring (`llm_scoring.py`)

**Purpose**: Provides multi-dimensional quality scoring for high-relevance papers

**Scoring Dimensions**:
- **Novelty**: How original and innovative the work is
- **Impact**: Potential influence on future research
- **Recommendation**: Action guidance for readers

**Key Features**:
- Only processes highly/moderately relevant papers
- Detailed justifications for all scores
- Structured XML response parsing
- Robust error handling and retry logic
- Parallel processing optimization

**Processing Logic**:
1. Identifies papers with high relevance scores
2. Builds comprehensive evaluation prompts
3. Requests multi-dimensional scoring
4. Parses and validates LLM responses
5. Updates papers with scoring results

### Module 6: H-Index Fetching (`h_index_fetching.py`)

**Purpose**: Enriches papers with author research impact data

**Key Features**:
- Semantic Scholar API integration
- Multiple search strategies (ID, title-based)
- Author profile matching
- H-index aggregation and statistics
- Conservative rate limiting

**Processing Logic**:
1. Searches for papers on Semantic Scholar
2. Retrieves author profile information
3. Extracts H-index data for each author
4. Calculates aggregate statistics
5. Identifies notable researchers

### Module 7: Cache Cleanup (`cache_cleanup.py`)

**Purpose**: Maintains database efficiency by removing old data

**Key Features**:
- Configurable retention periods
- Safe deletion with validation
- Performance optimization
- Storage management

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Git**
- **API Keys** for:
  - OpenAI (for embeddings)
  - OpenRouter (for LLM validation/scoring)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/ZheCodingChian/arXiv-Newsletter-Papers.git
cd arXiv-Newsletter-Papers
```

2. **Create a virtual environment**:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:

Create a `.env` file in the project root:
```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Environment Variables Setup

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Add to `.env` as `OPENAI_API_KEY`

#### OpenRouter API Key
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Go to API Keys section
4. Generate a new key
5. Add to `.env` as `OPENROUTER_API_KEY`

## 🎮 Usage

### Local Development

#### Process papers from a specific date:
```bash
python src/main.py --date 2025-01-15
```

#### Run in test mode with sample papers:
```bash
python src/main.py --test test_papers.txt
```

### Production Deployment

The system is designed to run automatically via GitHub Actions:

#### Automatic Daily Execution
- Runs daily at 7:00 AM SGT (23:00 UTC previous day)
- Processes papers from 20 days ago (allows for arXiv processing delays)
- Generates database with processed papers
- Commits database and logs to repository

#### Manual Execution
1. Go to **Actions** tab in GitHub repository
2. Select **"run data pipeline"** workflow
3. Click **"Run workflow"**
4. Choose options:
   - **Test run**: Use `test_papers.txt` for testing
   - **Paper date**: Specific date to process (YYYY-MM-DD)

### Output Structure

```
project/
├── database.sqlite        # SQLite database with all paper data
├── logs/                  # Processing logs
│   ├── 20250115.log      # Daily log files
│   └── ...
└── ...
```

## 📊 Database Schema

The `database.sqlite` file contains comprehensive paper data:

### Papers Table
- Core metadata (title, authors, abstract, dates, URLs)
- Processing status for each pipeline stage
- Embedding similarity scores for all topics
- LLM validation results and justifications
- Quality scores (novelty, impact, recommendation)
- Author H-index data and statistics
- Error tracking and timestamps

### Topic Embeddings Table
- Cached embeddings for research topics
- Model information and creation timestamps

## 🔧 Configuration

Key configuration options in `config.py`:

- **ARXIV**: API settings, rate limits, target categories
- **LATEX_EXTRACTION**: Download settings, retry policies
- **EMBEDDING**: Model selection, batch sizes
- **LLM_VALIDATION**: API configuration, parallel processing
- **LLM_SCORING**: Scoring model settings
- **H_INDEX_FETCHING**: Semantic Scholar API settings
- **CACHE_CLEANUP**: Data retention periods

## 📝 Logging

The pipeline generates detailed logs for monitoring and debugging:
- All operations are logged with timestamps
- Separate loggers for each module
- Error tracking with full stack traces
- Daily log rotation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- arXiv for providing open access to research papers
- OpenAI for embedding models
- OpenRouter for LLM API access
- Semantic Scholar for author impact data
