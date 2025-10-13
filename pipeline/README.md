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
- **Notifies** your team via Slack when processing completes

## 📑 Table of Contents

- [arXiv AI Research Data Pipeline](#arxiv-ai-research-data-pipeline)
  - [🎯 What It Does](#-what-it-does)
  - [📑 Table of Contents](#-table-of-contents)
  - [🏗️ How It Works](#️-how-it-works)
  - [🧩 Pipeline Modules](#-pipeline-modules)
    - [1. Scraper Module (`scraper.py`)](#1-scraper-module-scraperpy)
    - [2. Introduction Extractor Module (`intro_extractor.py`)](#2-introduction-extractor-module-intro_extractorpy)
    - [3. Embedding Similarity Module (`embedding_similarity.py`)](#3-embedding-similarity-module-embedding_similaritypy)
      - [Research Topics Analyzed](#research-topics-analyzed)
      - [Topic Descriptions for Semantic Analysis](#topic-descriptions-for-semantic-analysis)
    - [4. LLM Validation Module (`llm_validation.py`)](#4-llm-validation-module-llm_validationpy)
      - [LLM Validation Prompt Details](#llm-validation-prompt-details)
    - [5. LLM Scoring Module (`llm_scoring.py`)](#5-llm-scoring-module-llm_scoringpy)
      - [LLM Scoring Prompt Details](#llm-scoring-prompt-details)
    - [6. H-Index Fetching Module (`h_index_fetching.py`)](#6-h-index-fetching-module-h_index_fetchingpy)
    - [7. Database Cleanup Module (`database_cleanup.py`)](#7-database-cleanup-module-database_cleanuppy)
    - [8. Slack Notification Module (`slack.py`)](#8-slack-notification-module-slackpy)
  - [📊 Database Schema](#-database-schema)
    - [Papers Table](#papers-table)
    - [Topic Embeddings Table](#topic-embeddings-table)
  - [🗂️ Output Files](#️-output-files)
  - [⚙️ Configuration](#️-configuration)
    - [Project Structure](#project-structure)
  - [🚀 Usage](#-usage)
    - [Prerequisites](#prerequisites)
    - [Running the Pipeline](#running-the-pipeline)
    - [Test File Example](#test-file-example)
  - [📈 Performance](#-performance)
  - [📝 Logging](#-logging)

## 🏗️ How It Works

The pipeline processes papers through 8 sequential stages:

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
│ 7. Database     │ ── Cleans up database data for efficiency
│   Cleanup       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 8. Slack        │ ── Sends pipeline completion notification to Slack
│   Notification  │
└─────────────────┘
         │
         ▼
     database.sqlite
    (final output)
```

Each stage is fault-tolerant with comprehensive error handling and state persistence.

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

**What it does:** Computes semantic similarity scores between papers and 5 research topics using OpenAI embeddings.

#### Research Topics Analyzed

The pipeline analyzes papers across these 5 cutting-edge AI research areas:

1. **Agentic Artificial Intelligence** - Autonomous AI agents with goal-directed behavior, task decomposition, tool use, and workflow orchestration
2. **Proximal Policy Optimization (PPO)** - Policy gradient RL algorithm using clipped surrogate objectives for stable policy updates
3. **Reinforcement Learning** - Sequential decision-making through agent-environment interaction and reward maximization
4. **Reasoning Models** - AI systems performing complex multi-step logical deduction, mathematical problem-solving, and structured thinking
5. **Inference Time Scaling** - Techniques allocating additional computational resources during model inference to improve accuracy

#### Topic Descriptions for Semantic Analysis

Each research topic is defined through comprehensive descriptions used for semantic similarity matching. These descriptions include:

- **Summary**: High-level overview of the research area and typical paper characteristics
- **Definition**: Precise technical definition of what constitutes research in this area
- **Positive Signals**: Specific indicators that a paper belongs to this topic (keywords, methodologies, evaluation metrics)
- **Exclusions**: Clear boundaries defining what does NOT qualify as this topic
- **Keywords**: Extensive vocabulary associated with the research area

These detailed topic descriptions (ranging from 500-1000 words each) are embedded using OpenAI's `text-embedding-3-large` model and used to calculate semantic similarity scores between papers and topics. The full topic descriptions are defined in [embedding_similarity.py](src/modules/embedding_similarity.py) (lines 42-102).

**How it works:**
- Combines paper title, abstract, and introduction into content string
- Generates embeddings using OpenAI's text-embedding-3-large model
- Loads cached topic embeddings or computes them from detailed topic descriptions
- Calculates cosine similarity between paper and topic embeddings
- Applies **0.4 similarity threshold** to filter relevant papers
- Caches embeddings in SQLite database for efficiency
- Identifies highest-scoring topic for each paper

Papers that don't achieve the minimum similarity score of 0.4 for any of the 5 research topics are considered not relevant and **skip LLM analysis entirely**, ensuring computational resources are focused on the most promising papers.

### 4. LLM Validation Module (`llm_validation.py`)

**What it does:** Uses advanced language models to validate topic relevance and provide detailed justifications for papers above the similarity threshold.

**How it works:**
- Processes only papers with similarity scores ≥ 0.4
- Sends paper content to Grok-4-Fast via OpenRouter API
- Uses structured XML prompts with detailed topic descriptions
- Evaluates relevance on 4-point scale: Highly/Moderately/Tangentially/Not Relevant
- Generates detailed justifications explaining relevance assessments
- Handles concurrent API calls with rate limiting and retry logic
- Parses structured XML responses for reliable data extraction

#### LLM Validation Prompt Details

**Purpose**: Determine which of the 5 research topics are relevant to each paper.

**Model**: Grok-4-Fast via OpenRouter API

**Prompt Structure**:
The validation prompt provides the paper's title, abstract, and introduction (if available), along with concise topic definitions. For each topic scoring above the 0.4 similarity threshold, the LLM evaluates relevance on a 4-point scale:

- **Highly Relevant**: Paper's main contribution directly addresses the topic
- **Moderately Relevant**: Paper makes significant contributions related to the topic
- **Tangentially Relevant**: Paper touches on the topic but isn't primarily focused on it
- **Not Relevant**: Paper does not address the topic meaningfully

**Topic Definitions Used** (concise versions for LLM context):

1. **Agentic AI**: Autonomous systems where AI agents can perceive goals, decompose tasks, use external tools, and orchestrate workflows with minimal human intervention. Must include task decomposition, tool use, and planning—not just chatbots or single-prompt responses.

2. **Proximal Policy Optimization**: Specific RL algorithm using clipped surrogate objectives to prevent large policy updates. Must explicitly mention PPO or describe its clipped probability ratio mechanism.

3. **Reinforcement Learning**: Agent learning sequential decisions through environment interaction to maximize cumulative reward, formalized as MDPs. Must involve reward-based learning through interaction, not just supervised learning.

4. **Reasoning Models**: AI systems performing multi-step logical deduction, mathematical problem-solving, and structured thinking using techniques like chain-of-thought, self-verification, and explicit reasoning traces. Must be evaluated on reasoning benchmarks, not just pattern matching.

5. **Inference Time Scaling**: Techniques allocating additional compute during inference (after training) to improve accuracy, including verifier-based selection, iterative refinement, extended reasoning, or adaptive compute allocation.

**Output Format**: Structured XML with topic-specific relevance assessments and detailed justifications wrapped in CDATA tags.

**Configuration**:
- Temperature 0.1 for consistent, deterministic responses
- Maximum 4000 tokens per response for detailed justifications
- Parallel processing with 10 concurrent workers
- Retry logic with exponential backoff for resilience

The complete validation prompt template is defined in [llm_validation.py](src/modules/llm_validation.py) (lines 345-366).

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

#### LLM Scoring Prompt Details

**Purpose**: Evaluate paper quality across three dimensions for papers with at least one relevant topic.

**Model**: Grok-4-Fast via OpenRouter API

**Evaluation Rubric**:

The scoring prompt positions the LLM as an expert AI Research Analyst and provides detailed rubrics for three dimensions:

**1. Novelty** (Nature of the contribution):
- **Groundbreaking**: Introduces fundamentally new problems, paradigms, or breakthrough techniques that redefine the field
- **Significant**: Presents novel architectures, methods, or formulations that meaningfully advance current approaches
- **Incremental**: Provides refinements, extensions, or combinations of existing methods without fundamentally new concepts
- **Minimal**: Largely derivative work confirming known findings or making trivial modifications

**2. Potential Impact** (Likely influence):
- **Transformative**: Could reshape the field or enable entirely new research directions across multiple domains
- **Substantial**: Likely to influence broad work within the field and spawn follow-up research
- **Moderate**: Will be recognized within specific subfields or application areas
- **Negligible**: Unlikely to influence future research due to narrow scope or limited contributions

**3. Final Recommendation** (Action to take):
- **Must Read**: High-quality paper with significant contributions that advances the field meaningfully
- **Should Read**: Solid paper with valuable contributions worth attention when time permits
- **Can Skip**: Interesting but not essential; incremental, niche, or less impactful
- **Ignore**: Not recommended; lacks substance, relevance, or is poorly presented

**Output Format**: Structured XML containing:
- Single-paragraph summary synthesizing objectives, methodology, and key findings
- Score and 1-2 sentence justification for each of the three dimensions

**Configuration**:
- Temperature 0.1 for consistent, deterministic responses
- Maximum 4000 tokens per response for detailed justifications
- Parallel processing with 5 concurrent workers
- Retry logic with exponential backoff for resilience

The complete scoring prompt and rubric are defined in [llm_scoring.py](src/modules/llm_scoring.py) (lines 255-304).

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
- Removes cached embedding and topic data older than retention period (default: 14 days)
- Preserves recent data to avoid unnecessary recomputation
- Maintains database size and query performance
- Provides detailed cleanup statistics and logging

### 8. Slack Notification Module (`slack.py`)

**What it does:** Sends automated notifications to a Slack channel summarizing pipeline execution results.

**How it works:**
- Sends summary message after successful pipeline completion
- Displays total paper count and publication date
- Uses Slack Block Kit for rich, interactive formatting
- Includes "View Papers" button linking to the ResearchFeed website
- Configures bot appearance with custom username and emoji
- Handles missing configuration gracefully without blocking pipeline
- Operates independently—failures don't affect pipeline success

**Configuration:**
Requires two environment variables:
- `SLACK_BOT_TOKEN`: Slack bot OAuth token (starts with `xoxb-`)
- `SLACK_CHANNEL_ID`: Target Slack channel ID (e.g., `C1234567890`)

**Message Format:**
```
═══════════════════════════════════════
ResearchFeed Update | Run date: October 13, 2025
42 Papers Fetched | Published: October 12, 2025
[View Papers Button → https://researchfeed.pages.dev]
═══════════════════════════════════════
```

The notification module is fault-tolerant and logs warnings if Slack credentials are unavailable, allowing the pipeline to complete successfully regardless of notification status.

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

Values:
- Detailed text explanations for topics scoring above the similarity threshold
- `"below_threshold"` for topics scoring below the similarity threshold
- (Default `"no_justification"` is overwritten during LLM validation process)

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
├── /data/
│   ├── database.new.sqlite  # Main database with all paper data
│   └── cache.sqlite         # Cached embeddings and temporary data
└── logs/
    └── YYYYMMDD.log         # Daily processing logs
```

## ⚙️ Configuration

The pipeline can be configured by modifying `src/config.py`:

- **ARXIV**: API rate limits, target categories
- **LATEX_EXTRACTION**: Download timeouts, retry policies
- **EMBEDDING**: OpenAI model selection, batch sizes
- **LLM_VALIDATION**: API configuration, concurrency limits
- **LLM_SCORING**: Model selection, scoring criteria
- **H_INDEX_FETCHING**: Semantic Scholar API settings
- **DATABASE_CLEANUP**: Data retention periods

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
    ├── database_cleanup.py   # Data maintenance
    └── slack.py              # Slack notifications
```

## 🚀 Usage

### Prerequisites

1. **Python 3.8+** with required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Required API Keys** (set as environment variables):
   ```bash
   export OPENAI_API_KEY="your_openai_key"
   export OPENROUTER_API_KEY="your_openrouter_key"
   ```

3. **Slack Integration** (set as environment variables):
   ```bash
   export SLACK_BOT_TOKEN="xoxb-your-slack-bot-token"
   export SLACK_CHANNEL_ID="C1234567890"
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

### Test File Example

Create a text file with one arXiv ID per line:
```
2301.07041
2312.11805
2401.02412
```

## 📈 Performance

The pipeline is optimized for efficiency:

- **Parallel Processing**: Concurrent API calls and batch operations
- **Intelligent Caching**: Avoids reprocessing existing data
- **Rate Limiting**: Respects API limits with exponential backoff
- **Incremental Updates**: Only processes new or changed papers
- **Memory Efficient**: Streams large datasets without loading all in memory

## 📝 Logging

The pipeline generates comprehensive logs:

- **Daily Log Files**: `logs/YYYYMMDD.log`
- **Module-Specific Loggers**: Each component logs with its own identifier
- **Error Tracking**: Full stack traces for debugging
- **Progress Monitoring**: Detailed status updates and timing information
