# Modular Paper Processing Pipeline

A sophisticated, modular system for scraping, processing, and analyzing academic papers from arXiv. The architecture prioritizes modularity, configurability, and resilience with intelligent caching and comprehensive logging.

## 🏗️ Architecture Overview

The pipeline follows a **modular design** where each processing step is a separate, swappable module. The system uses a **centralized caching strategy** with SQLite for persistence and a **unified logging system** for comprehensive monitoring.

### Core Components

- **`main.py`**: Central orchestrator managing pipeline execution and caching
- **`config.py`**: Configuration management with no hardcoded values
- **`src/paper.py`**: Core `Paper` dataclass representing academic papers
- **`src/database.py`**: SQLite-based caching system
- **`src/modules/scraper.py`**: arXiv API scraper with intelligent retry logic
- **`cache.db`**: SQLite database for persistent paper storage
- **`logs/`**: Date-stamped log files for monitoring and debugging

## 🚀 Current Implementation Status

✅ **Completed Modules:**
- **Scraper Module**: Full arXiv API integration with rate limiting, retry logic, and category filtering
- **Caching System**: SQLite-based persistence with intelligent cache loading
- **Logging System**: Centralized logging with consistent formatting
- **Core Infrastructure**: Paper dataclass, database operations, and main orchestrator

🔄 **Planned Modules:**
- Introduction Extractor
- Embedding Similarity
- LLM Validation
- LLM Scoring
- Report Generation
- Notification System

## 📋 Requirements

- Python 3.8+
- No external dependencies (uses only Python standard library)

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd new-program
```

2. The system uses only Python standard library modules, so no additional installation is required.

## 💻 Usage

### Process Papers by Date
```bash
python3 src/main.py --date 2025-01-08
```
Fetches all papers published on January 8, 2025 within the configured categories.

### Process Papers from Test File
```bash
python3 src/main.py --test test_papers.txt
```
Processes specific papers listed in the file (one arXiv ID per line).

### Example Test File Format
```
2501.01234
2501.01235
2501.01236
```

## ⚙️ Configuration

All parameters are configured in `config.py`:

```python
ARXIV = {
    'target_categories': [
        'cs.AI', 'cs.LG', 'cs.CL', 'cs.DC', 'cs.CV', 'cs.NE',
        'stat.ML', 'math.OC', 'math.ST', 'math.PR', 'stat.TH'
    ],
    'batch_size': 100,
    'max_paper_limit': 1000,
    'rate_limiting': {
        'wait_time': 3.0,
        'max_retries': 5,
        'backoff_factor': 2.0,
        'jitter': 0.5
    }
}
```

## 🗂️ Data Flow

1. **Initialization**: Main orchestrator parses arguments and sets up logging
2. **Target Determination**: System identifies which papers to process (date-based or test file)
3. **Cache Loading**: Loads existing paper data from SQLite cache
4. **Processing Analysis**: Determines which papers need processing vs. can be skipped
5. **Scraping**: Fetches new papers from arXiv API with rate limiting and retry logic
6. **Caching**: Saves all paper data to cache after each module
7. **Module Chain**: Future modules will follow the same pattern

## 📊 Intelligent Caching

The system implements a sophisticated caching strategy:

- **Cache-First Loading**: Always loads existing data from cache before processing
- **Selective Processing**: Skips papers that are already successfully processed
- **Incremental Updates**: Only processes new or failed papers
- **Crash Recovery**: Automatic recovery from interruptions using cached data

## 📝 Logging

Comprehensive logging with consistent formatting:

```
2025-01-09 14:30:15,123 [SCRAPER] [INFO] Starting scraper module with --date 2025-01-08
2025-01-09 14:30:15,456 [SCRAPER] [INFO] Found 450 target papers: 420 to process, 30 to skip
2025-01-09 14:30:15,457 [SCRAPER] [INFO] Skipping paper arxiv:2501.12345 (already successfully_scraped)
```

Logs are saved to `logs/YYYYMMDD.log` and also displayed in console.

## 🔍 Paper Processing States

- **`initial`**: Newly created paper object
- **`successfully_scraped`**: All metadata successfully fetched from arXiv
- **`scraping_failed`**: Failed to fetch metadata after retries

## 🛠️ Error Handling

- **Rate Limiting**: Respects arXiv API limits with configurable delays
- **Exponential Backoff**: Automatic retry with increasing delays
- **Individual Paper Errors**: Isolated failures don't stop the entire pipeline
- **Comprehensive Error Logging**: All errors are logged with context

## 📁 File Structure

```
new-program/
├── requirements.txt           # Dependencies (currently none)
├── test_papers.txt           # Sample test file
├── cache.db                  # SQLite cache (created automatically)
├── logs/                     # Log files (created automatically)
├── src/
│   ├── main.py               # Main orchestrator
│   ├── config.py             # Configuration management
│   ├── paper.py              # Paper dataclass
│   ├── database.py           # Database operations
│   └── modules/
│       ├── __init__.py
│       └── scraper.py        # arXiv scraper module
└── README.md
```

## 🔮 Future Enhancements

The modular architecture allows for easy extension:

1. **Introduction Extractor**: Extract paper introductions
2. **Embedding Similarity**: Generate and compare embeddings
3. **LLM Validation**: Validate paper quality using LLMs
4. **LLM Scoring**: Score papers based on criteria
5. **Report Generation**: Generate summary reports
6. **Notification System**: Send alerts and updates

## 🤝 Contributing

The system is designed for easy module addition. Each new module should:
1. Accept the `runtime_paper_dict` as input
2. Modify papers in-place
3. Return the updated dictionary
4. Use the centralized logging system
5. Handle errors gracefully

## 📄 License

[Add your license here]