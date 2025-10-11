import logging
from typing import Dict, List
from .scraper import ArxivScraper
from paper import Paper

logger = logging.getLogger('SCRAPER')


class TestScraper(ArxivScraper):
    """
    Test scraper for fetching specific arXiv papers by ID.
    
    Inherits from ArxivScraper to reuse all metadata extraction,
    category enhancement, and database operations. Only differs
    in the initial paper discovery method.
    """
    
    def run(self, run_mode: str, run_value: str) -> Dict[str, Paper]:
        """
        Main entry point for the test scraper.
        
        Args:
            run_mode: Must be 'test'
            run_value: Path to text file containing arXiv IDs
            
        Returns:
            Dictionary of paper_id -> Paper objects
            
        Raises:
            ValueError: If run_mode is not 'test'
            FileNotFoundError: If test file doesn't exist
        """
        if run_mode != 'test':
            raise ValueError(f"Test scraper only supports 'test' mode, got '{run_mode}'")
        
        logger.info(f"Starting test-based scraping from file {run_value}")
        
        # Step 1: Fetch papers by IDs from test file
        xml_response = self._fetch_papers_from_file(run_value)
        
        # Step 2: Extract IDs and check limits
        paper_ids = self._extract_paper_ids(xml_response)
        logger.info(f"Found {len(paper_ids)} papers from test file")
        self._check_paper_limit(len(paper_ids))
        
        # Step 3: Load cached papers and build runtime dict
        runtime_dict = self._load_cached_papers(paper_ids)
        
        # Step 4: Extract metadata for missing papers
        complete_dict = self._extract_metadata_for_missing_papers(xml_response, runtime_dict)
        
        # Step 5: Clean up categories to keep only arXiv format
        complete_dict = self._clean_arxiv_categories(complete_dict)
        
        return complete_dict
    
    def _fetch_papers_from_file(self, file_path: str) -> str:
        """
        Fetch papers by IDs from a test file.
        
        Args:
            file_path: Path to file containing arXiv IDs (one per line)
            
        Returns:
            Raw XML response from arXiv API
            
        Raises:
            FileNotFoundError: If test file doesn't exist
            Exception: If all retry attempts fail
        """
        # Read paper IDs from file
        with open(file_path, 'r') as f:
            paper_ids = [line.strip() for line in f if line.strip()]
        
        if not paper_ids:
            raise ValueError(f"No paper IDs found in test file: {file_path}")
        
        # Build query for specific paper IDs
        id_queries = [f"id:{paper_id}" for paper_id in paper_ids]
        search_query = f"({'+OR+'.join(id_queries)})"
        url = f"http://export.arxiv.org/api/query?search_query={search_query}&max_results={len(paper_ids) + 10}"
        
        logger.info(f"Fetching {len(paper_ids)} papers from test file")
        return self._make_api_request(url)


def run(run_mode: str, run_value: str) -> Dict[str, Paper]:
    """
    Main entry point for the test scraper module.
    
    Args:
        run_mode: Must be 'test'
        run_value: Path to text file containing arXiv IDs
        
    Returns:
        Dictionary of paper_id -> Paper objects
    """
    scraper = TestScraper()
    return scraper.run(run_mode, run_value)