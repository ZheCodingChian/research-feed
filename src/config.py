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
    # Parallel processing settings
    'max_workers': 3,
    
    # Rate limiting for arXiv downloads
    'rate_limit_delay': 1.5,
    'jitter': 0.5,
    
    # Retry settings
    'max_retries': 3,
    'timeout': 90,
    
    # Content limits
    'max_introduction_length': 15000,
    'min_source_size': 1000  # bytes
} 