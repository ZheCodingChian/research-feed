# arXiv AI Research Data Pipeline

A comprehensive automated pipeline for discovering, analyzing, and curating high-quality AI research papers from arXiv. This system combines web scraping, natural language processing, machine learning, and intelligent scoring to generate a structured database of the most relevant and impactful research papers in artificial intelligence.

## 🎯 What It Does

The arXiv AI Research Data Pipeline automatically:

- **Discovers** new AI research papers from arXiv's cs.AI and cs.CV categories
- **Extracts** paper introductions from LaTeX source files when available
- **Calculates** semantic similarity scores for 5 key AI research topics
- **Validates** topic relevance using advanced LLM analysis
- **Scores** papers on novelty, impact, and recommendation quality
- **Enriches** data with author H-index information from Semantic Scholar
- **Stores** everything in a structured SQLite database for analysis

## 🔬 Research Topics Analyzed

The pipeline analyzes papers across these 5 cutting-edge AI research areas:

1. **Reinforcement Learning** - Agents learning through environment interaction and reward feedback
2. **Proximal Policy Optimization (PPO)** - Specific RL algorithm with clipped surrogate objectives
3. **Reasoning Models** - AI systems performing multi-step logical deduction and structured thinking
4. **Agentic AI** - Autonomous AI agents with tool use, planning, and workflow orchestration
5. **Inference Time Scaling** - Techniques allocating additional compute during model inference

## 🏗️ How It Works

The pipeline processes papers through 7 sequential stages:

```
┌─────────────────┐
│   1. Scraper    │ ── Fetches papers from arXiv API by date or test file
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 2. Introduction │ ── Downloads and extracts introductions from LaTeX source
│   Extractor     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  3. Embedding   │ ── Computes semantic similarity scores using OpenAI embeddings
│   Similarity    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 4. LLM          │ ── Validates topic relevance with detailed justifications
│   Validation    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 5. LLM Scoring  │ ── Scores novelty, impact, and generates recommendations
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 6. H-Index      │ ── Fetches author research impact data from Semantic Scholar
│   Fetching      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 7. Database        │ ── Cleans up database data for efficiency
│   Cleanup       │
└─────────────────┘
         │
         ▼
     database.sqlite
    (final output)
```

Each stage is fault-tolerant with comprehensive error handling and state persistence.

## 🚀 Usage

### Prerequisites

1. **Python 3.8+** with required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Keys** (set as environment variables):
   ```bash
   export OPENAI_API_KEY="your_openai_key"
   export OPENROUTER_API_KEY="your_openrouter_key"
   ```

### Running the Pipeline

**Process papers from a specific date:**
```bash
python src/main.py --date 2025-01-15
```


**Doing a test run:**
```bash
python src/main.py --test <testfile.txt>
```
### Test file example

Create a text file with one arXiv ID per line:
```
2301.07041
2312.11805
2401.02412
```

## 🔍 Relevance Filtering

The pipeline uses a **similarity threshold of 0.4** to filter papers based on topic relevance. Papers that don't achieve this minimum similarity score for any of the 5 research topics are considered not relevant to our field of interest and **skip LLM analysis entirely**. This ensures computational resources are focused on the most promising papers.

Papers above the threshold proceed through the full LLM validation and scoring pipeline for detailed analysis.

## 🧩 Pipeline Modules

### 1. Scraper Module (`scraper.py`)

**What it does:** Discovers and fetches paper metadata from arXiv based on date or test file input.

**How it works:**
- Queries arXiv API for papers in cs.AI and cs.CV categories for specified dates
- Parses XML responses to extract core metadata (title, authors, abstract, categories)
- **Category Enhancement**: Converts raw arXiv categories (e.g., "cs.AI") to descriptive format (e.g., "cs.AI (Artificial Intelligence)")
  - Only enhances categories once per paper using `category_enhancement` flag to prevent data loss on re-runs
  - Validates categories against arXiv format patterns and removes invalid entries
- Constructs URLs for arXiv page, PDF download, and LaTeX source
- Handles rate limiting and API errors with exponential backoff
- Creates Paper objects with initial "scraped" status

### 2. Introduction Extractor Module (`intro_extractor.py`)

**What it does:** Downloads LaTeX source files and extracts paper introductions for enhanced content analysis.

**How it works:**
- Downloads LaTeX source archives from arXiv when available
- Extracts and parses .tex files from compressed archives
- Uses pattern matching to identify introduction sections
- Cleans LaTeX markup while preserving meaningful content
- Handles various introduction formats (\\section{Introduction}, \\section{1}, etc.)
- Falls back gracefully when LaTeX source is unavailable

### 3. Embedding Similarity Module (`embedding_similarity.py`)

**What it does:** Computes semantic similarity scores between papers and the 5 research topics using OpenAI embeddings.

**How it works:**
- Combines paper title, abstract, and introduction into content string
- Generates embeddings using OpenAI's text-embedding-3-large model
- Loads cached topic embeddings or computes them from detailed topic descriptions
- Calculates cosine similarity between paper and topic embeddings
- Applies 0.4 similarity threshold to filter relevant papers
- Caches embeddings in SQLite database for efficiency
- Identifies highest-scoring topic for each paper

### 4. LLM Validation Module (`llm_validation.py`)

**What it does:** Uses advanced language models to validate topic relevance and provide detailed justifications for papers above the similarity threshold.

**How it works:**
- Processes only papers with similarity scores ≥ 0.4
- Sends paper content to Grok-3-Mini via OpenRouter API
- Uses structured XML prompts with detailed topic descriptions
- Evaluates relevance on 4-point scale: Highly/Moderately/Somewhat/Not Relevant
- Generates detailed justifications explaining relevance assessments
- Handles concurrent API calls with rate limiting and retry logic
- Parses structured XML responses for reliable data extraction

### 5. LLM Scoring Module (`llm_scoring.py`)

**What it does:** Evaluates paper quality across multiple dimensions using LLM analysis for validated papers.

**How it works:**
- Processes papers with "Highly Relevant", "Moderately Relevant", or "Tangentially Relevant" ratings
- Generates comprehensive paper summaries
- Scores papers on three dimensions:
  - **Novelty**: Groundbreaking/Significant/Incremental/Minimal with justification
  - **Impact**: Transformative/Substantial/Moderate/Negligible with justification  
  - **Recommendation**: Must Read/Should Read/Can Skip/Ignore with justification
- Uses structured prompts for consistent scoring criteria
- Provides detailed explanations for each score

### 6. H-Index Fetching Module (`h_index_fetching.py`)

**What it does:** Enriches paper data with author research impact metrics from Semantic Scholar.

**How it works:**
- Searches Semantic Scholar API using arXiv ID, then title if needed
- Fetches author profiles and H-index data for each paper author
- Calculates aggregate statistics: highest, average, and notable author counts
- Handles author name variations and disambiguation
- Tracks fetch methods and success rates for quality assessment
- Respects API rate limits with intelligent retry mechanisms

### 7. Database Cleanup Module (`database_cleanup.py`)

**What it does:** Maintains database efficiency by removing old cached data while preserving current processing results.

**How it works:**
- Updates timestamps for papers processed in current pipeline run
- Removes cached embedding and topic data older than retention period
- Preserves recent data to avoid unnecessary recomputation
- Maintains database size and query performance
- Provides detailed cleanup statistics and logging

## 📊 Database Schema

The pipeline outputs to `database.sqlite` with two main tables:

### Papers Table

**Core Metadata:**
- `id` (TEXT) - arXiv ID (e.g., "2301.07041")
- `title` (TEXT) - Paper title
- `authors` (TEXT) - JSON array of author names
- `categories` (TEXT) - JSON array of enhanced arXiv categories (e.g., ["cs.AI (Artificial Intelligence)", "cs.LG (Machine Learning)"])
- `abstract` (TEXT) - Paper abstract
- `published_date` (TEXT) - ISO format publication date
- `category_enhancement` (TEXT) - Enhancement status: "not_enhanced" or "enhanced"
- `arxiv_url` (TEXT) - arXiv abstract page URL
- `pdf_url` (TEXT) - Direct PDF download URL
- `latex_url` (TEXT) - LaTeX source files URL

**Processing Status Fields:**

- `scraper_status` (TEXT)
  - Values: `"initial"`, `"successfully_scraped"`, `"scraping_failed"`

- `intro_status` (TEXT)
  - Values: `"not_extracted"`, `"intro_successful"`, `"no_intro_found"`, `"extraction_failed"`

- `embedding_status` (TEXT)
  - Values: `"not_embedded"`, `"completed"`, `"failed"`

- `llm_validation_status` (TEXT)
  - Values: `"not_validated"`, `"completed"`, `"failed"`

- `llm_score_status` (TEXT)
  - Values: `"not_scored"`, `"completed"`, `"failed"`, `"not_relevant_enough"`

- `h_index_status` (TEXT)
  - Values: `"not_fetched"`, `"completed"`, `"failed"`

**Introduction Extraction:**
- `introduction_text` (TEXT) - Extracted introduction content
- `intro_extraction_method` (TEXT) - Method used for extraction
- `tex_file_name` (TEXT) - Source LaTeX file name

**Topic Similarity Scores (REAL, 0.0-1.0):**
- `agentic_ai_score`
- `proximal_policy_optimization_score`
- `reinforcement_learning_score`
- `reasoning_models_score`
- `inference_time_scaling_score`

**LLM Validation Results:**

Relevance assessments for each topic:
- `agentic_ai_relevance`
- `proximal_policy_optimization_relevance`
- `reinforcement_learning_relevance`
- `reasoning_models_relevance`
- `inference_time_scaling_relevance`

Values: `"not_validated"`, `"Highly Relevant"`, `"Moderately Relevant"`, `"Tangentially Relevant"`, `"Not Relevant"`

Justifications for each topic:
- `agentic_ai_justification`
- `proximal_policy_optimization_justification`
- `reinforcement_learning_justification`
- `reasoning_models_justification`
- `inference_time_scaling_justification`

Values: `"no_justification"` (default) or detailed text explanations when validation is completed

**LLM Quality Scoring:**
- `summary` (TEXT) - LLM-generated paper summary
- `novelty_score` (TEXT) - Values: `"Groundbreaking"`, `"Significant"`, `"Incremental"`, `"Minimal"`
- `novelty_justification` (TEXT) - Explanation for novelty score
- `impact_score` (TEXT) - Values: `"Transformative"`, `"Substantial"`, `"Moderate"`, `"Negligible"`
- `impact_justification` (TEXT) - Explanation for impact score
- `recommendation_score` (TEXT) - Values: `"Must Read"`, `"Should Read"`, `"Can Skip"`, `"Ignore"`
- `recommendation_justification` (TEXT) - Explanation for recommendation

**Author Impact Data:**
- `semantic_scholar_url` (TEXT) - Semantic Scholar paper URL
- `h_index_fetch_method` (TEXT) - Values: `"full_id"`, `"base_id"`, `"title_search"`
- `total_authors` (INTEGER) - Total number of authors
- `authors_found` (INTEGER) - Authors found with H-index data
- `highest_h_index` (INTEGER) - Highest H-index among authors
- `average_h_index` (REAL) - Average H-index of authors with data
- `notable_authors_count` (INTEGER) - Authors with H-index > 5
- `author_h_indexes` (TEXT) - JSON array of detailed author H-index objects

**Metadata:**
- `errors` (TEXT) - JSON array of error messages
- `created_at` (TEXT) - ISO format creation timestamp
- `updated_at` (TEXT) - ISO format last update timestamp
- `last_generated` (TEXT) - YYYY-MM-DD format for cache cleanup

### Topic Embeddings Table

- `topic_name` (TEXT) - Research topic name
- `description` (TEXT) - Detailed topic description
- `embedding_vector` (TEXT) - JSON array of embedding floats
- `model` (TEXT) - Embedding model used (e.g., "text-embedding-3-large")
- `created_at` (TEXT) - ISO format creation timestamp

## 🗂️ Output Files

After running the pipeline, you'll find:

```
pipeline/
├── database.sqlite       # Main database with all paper data
├── cache.sqlite         # Cached embeddings and temporary data
└── logs/
    └── YYYYMMDD.log     # Daily processing logs
```

## ⚙️ Configuration

The pipeline can be configured by modifying `src/config.py`:

- **ARXIV**: API rate limits, target categories
- **LATEX_EXTRACTION**: Download timeouts, retry policies
- **EMBEDDING**: OpenAI model selection, batch sizes
- **LLM_VALIDATION**: API configuration, concurrency limits
- **LLM_SCORING**: Model selection, scoring criteria
- **H_INDEX_FETCHING**: Semantic Scholar API settings
- **CACHE_CLEANUP**: Data retention periods

## 📈 Performance

The pipeline is optimized for efficiency:

- **Parallel Processing**: Concurrent API calls and batch operations
- **Intelligent Caching**: Avoids reprocessing existing data
- **Rate Limiting**: Respects API limits with exponential backoff
- **Incremental Updates**: Only processes new or changed papers
- **Memory Efficient**: Streams large datasets without loading all in memory

## 🔧 Development

### Project Structure

```
src/
├── main.py                    # Pipeline orchestrator
├── paper.py                   # Core data model
├── database.py               # SQLite database operations
├── config.py                 # Configuration settings
└── modules/
    ├── scraper.py            # arXiv paper discovery
    ├── intro_extractor.py    # LaTeX introduction extraction
    ├── embedding_similarity.py # Semantic similarity calculation
    ├── llm_validation.py     # Topic relevance validation
    ├── llm_scoring.py        # Quality scoring
    ├── h_index_fetching.py   # Author impact data
    └── cache_cleanup.py      # Data maintenance
```

### Adding New Topics

To add new research topics:

1. Update topic descriptions in `embedding_similarity.py`
2. Add corresponding fields to `paper.py` and `database.py`
3. Update LLM validation descriptions in `llm_validation.py`

## 📝 Logging

The pipeline generates comprehensive logs:

- **Daily Log Files**: `logs/YYYYMMDD.log`
- **Module-Specific Loggers**: Each component logs with its own identifier
- **Error Tracking**: Full stack traces for debugging
- **Progress Monitoring**: Detailed status updates and timing information
