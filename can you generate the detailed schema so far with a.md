
### **Architectural Schema: Modular Paper Processing Pipeline**

This document specifies the foundational architecture for an automated system designed to scrape, process, and analyze academic papers. The design prioritizes modularity, configurability, and resilience. For now, we will focus on the foundation and architecture of the program. we will just have the scraping arxiv done first 

### **1. Project Structure**

The project will be organized into the following directory and file structure:

* **`main.py`**: The central orchestrator. It controls the pipeline's execution flow, parses command-line arguments, and manages saving data to the cache.
* **`config.yaml`**: A configuration file containing all operational parameters, ensuring no hardcoded values in the codebase.
* **`modules/`**: A directory containing all individual, swappable processing modules.
    * `__init__.py`
    * `scraper.py`
    * `intro_extractor.py` *(Work in Progress)*
    * `embed_similarity.py` *(Work in Progress)*
    * `llm_validation.py` *(Work in Progress)*
    * `llm_scoring.py` *(Work in Progress)*
    * `generate_report.py` *(Work in Progress)*
    * `notification.py` *(Work in Progress)*
* **`cache.db`**: A SQLite database file for the persistent storage of processed paper data.
* **`logs/`**: A directory for storing log files. Log files will be named by date (e.g., `20250709.log`).


### **2. Configuration Schema (`config.yaml`)**

All configurable parameters will be managed in this file. The structure for the scraper's configuration is as follows:

```yaml
# ArXiv API Interaction Parameters
arxiv:
  # List of categories to target. Only papers belonging to at least one of these will be processed.
  target_categories:
    - 'cs.AI'
    - 'cs.LG'
    - 'cs.CL'
    - 'cs.DC'
    - 'cs.CV'
    - 'cs.NE'
    - 'stat.ML'
    - 'math.OC'
    - 'math.ST'
    - 'math.PR'
    - 'stat.TH'

  # The number of results to fetch in a single API call for pagination.
  batch_size: 100

  # A hard limit on the total number of papers to process.
  # The pipeline will raise an error and exit if this limit is exceeded.
  max_paper_limit: 1000

  # Rate Limiting and Retry Strategy
  rate_limiting:
    # Initial time to wait (in seconds) between API requests.
    wait_time: 3.0
    # Maximum number of times to retry a failed API call.
    max_retries: 5
    # The factor by which the wait time increases after each failed retry.
    backoff_factor: 2.0
    # A random variation factor added to wait times to prevent synchronized requests (jitter).
    jitter: 0.5
```


### **3. Core Data Structures**

* **`Paper` Object**: A structured data object (e.g., a Python `dataclass`) that represents a single paper.
    * **Evolving Fields**: Its fields will be defined and expanded as module requirements are detailed.
    * **State Tracking**: It will contain a `status` field (e.g., "scraped," "intro_extraction_failed") to track the paper's progress and state. This is crucial for debugging, conditional processing in later steps, and summarizing run results.
    * **Error Logging**: An `errors` list will store any error messages specific to that paper.
* **`runtime_paper_dict`**: The single source of truth during a pipeline run. This is a Python dictionary where keys are unique paper IDs and values are the corresponding `Paper` objects. It is initialized by the scraper and passed sequentially through each module.


### **4. System Execution and Caching Logic**

The pipeline follows a "load-once at the start, save-on-demand from main" caching strategy.

1. **Initiation**:
    * `main.py` starts and parses command-line arguments to determine the run mode:
        * `--test <filename.txt>`: Process a specific list of paper IDs from a file.
        * `--date <YYYY-MM-DD>`: Process all papers from a specific date.
    * The logging system is configured to output to a date-stamped file in the `logs/` directory.
2. **Step 1: Scraper Module Execution**:
    * `main.py` calls `modules.scraper.run()`, passing it the necessary configuration.
    * The scraper executes its logic (detailed in the next section) and returns the fully populated `runtime_paper_dict`.
3. **Save Point**:
    * Upon receiving the `runtime_paper_dict` from the scraper, `main.py` immediately calls an internal `save_to_cache()` function.
    * This function iterates through the dictionary and persists the current state of every paper to `cache.db` using an `INSERT OR UPDATE` operation.
4. **Subsequent Module Execution**:
    * `main.py` calls the next module in the sequence (e.g., `intro_extractor.py`), passing it the entire `runtime_paper_dict`.
    * The module performs its task, modifying the `Paper` objects within the dictionary in-place. It **does not interact with the cache**.
    * Once the module completes, it returns control to `main.py`. `main.py` then calls `save_to_cache()` again to persist the newly added data.
5. **Repeat**: This cycle of "execute module -> save state" repeats for every processing module in the pipeline (`embed_similarity`, `llm_validation`, etc.).
6. **Finalization**: After all processing steps are complete, `main.py` calls the final modules (`generate_report.py`, `notification.py`) to produce the desired output.

### **5. Module Specification: `modules/scraper.py`**

This module handles the initial data acquisition and is designed for abstraction and robustness.

* **Input**: `config` object and the run parameters (`--test` file or `--date`).
* **Output**: The populated `runtime_paper_dict`.


#### **Functional Logic**:

1. **Determine Target IDs**: Identifies the list of paper IDs to process based on the specified run mode.
2. **Enforce Paper Limit**: Before fetching data, it checks if the number of target IDs exceeds `config.arxiv.max_paper_limit`. If so, it raises an error to halt the pipeline.
3. **Fetch Metadata**: It iteratively fetches paper metadata from the arXiv API in batches, governed by `config.arxiv.batch_size`. The fetching process includes:
    * **Intelligent Pagination**: Tracks progress across multiple API calls to handle large result sets.
    * **Rate Limiting**: Respects the API by pausing between requests according to `wait_time` and `jitter` settings.
    * **Exponential Backoff**: If an API error occurs, it retries the request up to `max_retries` times, increasing the wait time with each attempt according to the `backoff_factor`.
4. **Filter Results**: For each paper returned from the API:
    * **Category Normalization**: It applies a regex (`[a-z-]+\.[A-Z]{2}`) to the paper's category list to retain only valid arXiv codes.
    * **Targeted Filtering**: It checks if the paper has at least one category matching the `config.arxiv.target_categories` list. Papers that do not match are discarded.
5. **Build Initial Collection**: Creates a `Paper` object for each valid paper and adds it to an internal dictionary.
6. **Pre-load from Cache**: After fetching and filtering, it iterates through its newly created collection of `Paper` objects. For each one, it queries `cache.db` and, if a record exists, updates the in-memory `Paper` object with the cached data.
7. **Return**: Returns the final, fully initialized `runtime_paper_dict` to `main.py`.