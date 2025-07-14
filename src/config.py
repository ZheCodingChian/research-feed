# ArXiv API Interaction Parameters
ARXIV = {
    # List of categories to target. Only papers belonging to at least one of these will be processed.
    'target_categories': [
        'cs.AI',
        'cs.CV'
    ],
    
    # The number of results to fetch in a single API call for pagination.
    'batch_size': 100,
    
    # A hard limit on the total number of papers to process.
    # The pipeline will raise an error and exit if this limit is exceeded.
    'max_paper_limit': 1000,
    
    # Rate Limiting and Retry Strategy
    'rate_limiting': {
        # Initial time to wait (in seconds) between API requests.
        'wait_time': 3.0,
        # Maximum number of times to retry a failed API call.
        'max_retries': 3,
        # The factor by which the wait time increases after each failed retry.
        'backoff_factor': 2.0,
        # A random variation factor added to wait times to prevent synchronized requests (jitter).
        'jitter': 0.5
    }
}

# LaTeX Introduction Extraction Parameters
LATEX_EXTRACTION = {
    # Rate limiting for arXiv downloads (sequential processing)
    'rate_limit_delay': 1.0,  # Seconds to wait between each download request
    
    # Retry settings
    'max_retries': 3,
    'retry_delays': [1, 5, 10],  # Retry backoff delays in seconds: 1s, 5s, 10s
    'timeout': 90,
    
    # Content limits
    'max_introduction_length': 15000
}

# Embedding Similarity Parameters
EMBEDDING = {
    # Model configuration
    'model': 'text-embedding-3-large',
    
    # Batch processing
    'batch_size': 100,
    
    # Retry settings
    'max_retries': 3,
    'timeout': 60
}

# LLM Validation Parameters
LLM_VALIDATION = {
    # OpenRouter API configuration
    'api_base_url': 'https://openrouter.ai/api/v1',
    'model': 'x-ai/grok-3-mini',
    'api_key_env': 'OPENROUTER_API_KEY',
    
    # Similarity threshold for validation
    'similarity_threshold': 0.4,
    
    # Parallel processing settings
    'max_workers': 10,  # Number of concurrent API calls
    'batch_size': 10,   # Papers to process in parallel batches
    'max_retries': 3,
    'timeout': 120,
    
    # Rate limiting (reduced since we're using parallel processing)
    'rate_limit_delay': 0.5,  # Reduced delay between batches
    'jitter': 0.2
}

# LLM Scoring Parameters
LLM_SCORING = {
    # OpenRouter API configuration
    'api_base_url': 'https://openrouter.ai/api/v1',
    'model': 'x-ai/grok-3-mini',
    'api_key_env': 'OPENROUTER_API_KEY',
    
    # Parallel processing settings (no batching for this module)
    'max_workers': 5,   # Number of concurrent API calls
    'timeout': 120
}

# H-Index Fetching Parameters
H_INDEX_FETCHING = {
    # Semantic Scholar API configuration
    'api_base_url': 'https://api.semanticscholar.org/graph/v1',
    
    # Sequential processing settings
    'timeout': 30,
    'max_retries': 3,
    
    # Rate limiting (conservative to respect Semantic Scholar's public API limits)
    'rate_limit_delay': 1.0,  # 1 second delay between requests
    
    # Processing thresholds
    'notable_h_index_threshold': 5  # H-index threshold for "notable" authors
}