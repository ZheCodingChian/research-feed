import time
import random
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

import config
from paper import Paper
from database import PaperDatabase

logger = logging.getLogger('SCRAPER_TEST')


class ArxivTestScraper:
    """
    Test scraper for ID-based paper fetching from arXiv API.
    
    This implementation reads paper IDs from a text file, loads cached papers,
    and fetches metadata only for missing or failed papers.
    """
    
    def __init__(self):
        self.config = config.ARXIV
        self.db = PaperDatabase()
        self.session_stats = {
            'successfully_scraped': 0,
            'scraping_failed': 0,
            'api_calls': 0,
            'retries': 0
        }

    def run(self, run_mode: str, run_value: str) -> Dict[str, Paper]:
        """
        Main entry point for the test scraper.
        
        Args:
            run_mode: Must be 'test'
            run_value: Path to text file containing paper IDs
            
        Returns:
            Dictionary of paper_id -> Paper objects
            
        Raises:
            ValueError: If run_mode is not 'test'
            FileNotFoundError: If test file doesn't exist
        """
        if run_mode != 'test':
            raise ValueError(f"Test scraper only supports 'test' mode, got '{run_mode}'")
        
        logger.info(f"Starting test scraping from file {run_value}")
        
        # Step 1: Read paper IDs from file
        paper_ids = self._read_paper_ids_from_file(run_value)
        logger.info(f"Loaded {len(paper_ids)} paper IDs from test file")
        self._check_paper_limit(len(paper_ids))
        
        # Step 2: Load cached papers and build runtime dict
        runtime_dict = self._load_cached_papers(paper_ids)
        
        # Step 3: Fetch metadata for missing papers
        complete_dict = self._fetch_missing_papers_metadata(runtime_dict)
        
        # Step 4: Clean up categories to keep only arXiv format
        complete_dict = self._clean_arxiv_categories(complete_dict)
        
        # Log final statistics
        self._log_session_summary()
        
        return complete_dict

    def _read_paper_ids_from_file(self, file_path: str) -> List[str]:
        """
        Read paper IDs from text file.
        
        Args:
            file_path: Path to text file containing one paper ID per line
            
        Returns:
            List of paper IDs
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(file_path, 'r') as f:
                paper_ids = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Read {len(paper_ids)} paper IDs from {file_path}")
            return paper_ids
            
        except FileNotFoundError:
            logger.error(f"Test file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading test file {file_path}: {e}")
            raise

    def _check_paper_limit(self, paper_count: int) -> None:
        """
        Check if paper count exceeds configured limit.
        
        Args:
            paper_count: Number of papers found
            
        Raises:
            RuntimeError: If count exceeds limit
        """
        max_limit = self.config['max_paper_limit']
        if paper_count > max_limit:
            error_msg = f"Paper count ({paper_count}) exceeds maximum limit ({max_limit})"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _load_cached_papers(self, paper_ids: List[str]) -> Dict[str, Optional[Paper]]:
        """
        Load cached papers and build initial runtime dictionary.
        
        Args:
            paper_ids: List of paper IDs to check
            
        Returns:
            Dictionary with Paper objects for successfully scraped papers,
            None for papers that need processing
        """
        logger.info(f"Loading cached papers for {len(paper_ids)} IDs")
        
        # Query database for existing papers
        cached_papers = self.db.load_papers(paper_ids)
        logger.info(f"Found {len(cached_papers)} papers in cache")
        
        runtime_dict = {}
        cache_hits = 0
        cache_misses = 0
        
        for paper_id in paper_ids:
            if paper_id in cached_papers and cached_papers[paper_id].is_successfully_scraped():
                # Keep successfully scraped paper - skip metadata extraction
                runtime_dict[paper_id] = cached_papers[paper_id]
                cache_hits += 1
            else:
                # Either not in cache or failed status - mark for processing
                runtime_dict[paper_id] = None
                cache_misses += 1
        
        logger.info(f"Cache analysis: {cache_hits} hits, {cache_misses} misses")
        return runtime_dict

    def _fetch_missing_papers_metadata(self, runtime_dict: Dict[str, Optional[Paper]]) -> Dict[str, Paper]:
        """
        Fetch metadata for papers that need processing.
        
        Args:
            runtime_dict: Dictionary with None values for papers to process
            
        Returns:
            Complete dictionary with all Paper objects
        """
        papers_to_process = [paper_id for paper_id, paper in runtime_dict.items() if paper is None]
        logger.info(f"Fetching metadata for {len(papers_to_process)} papers")
        
        if not papers_to_process:
            logger.info("No papers need metadata fetching")
            return runtime_dict
        
        # Build arXiv API query for missing papers
        xml_response = self._fetch_papers_by_ids(papers_to_process)
        
        # Extract metadata from response
        return self._extract_metadata_from_response(xml_response, runtime_dict, papers_to_process)

    def _fetch_papers_by_ids(self, paper_ids: List[str]) -> str:
        """
        Fetch papers by their IDs from arXiv API.
        
        Args:
            paper_ids: List of paper IDs to fetch
            
        Returns:
            Raw XML response from arXiv API
            
        Raises:
            Exception: If all retry attempts fail
        """
        # Build search query with OR conditions
        id_conditions = [f"id:{paper_id}" for paper_id in paper_ids]
        search_query = "+OR+".join(id_conditions)
        url = f"http://export.arxiv.org/api/query?search_query={search_query}&max_results={len(paper_ids)}"
        
        logger.info(f"Fetching metadata for {len(paper_ids)} papers")
        return self._make_api_request(url)

    def _make_api_request(self, url: str) -> str:
        """
        Make API request with exponential backoff retry logic.
        
        Args:
            url: Complete URL to request
            
        Returns:
            Response content as string
            
        Raises:
            Exception: If all retry attempts fail
        """
        max_retries = self.config['rate_limiting']['max_retries']
        base_wait = self.config['rate_limiting']['wait_time']
        backoff_factor = self.config['rate_limiting']['backoff_factor']
        jitter = self.config['rate_limiting']['jitter']
        
        for attempt in range(max_retries + 1):
            try:
                self.session_stats['api_calls'] += 1
                logger.debug(f"API request attempt {attempt + 1}/{max_retries + 1}: {url}")
                
                with urllib.request.urlopen(url, timeout=30) as response:
                    return response.read().decode('utf-8')
                    
            except Exception as e:
                if attempt < max_retries:
                    self.session_stats['retries'] += 1
                    wait_time = base_wait * (backoff_factor ** attempt)
                    actual_wait = wait_time + random.uniform(-jitter, jitter)
                    actual_wait = max(0, actual_wait)
                    
                    logger.warning(f"API request failed (attempt {attempt + 1}), retrying in {actual_wait:.1f}s: {e}")
                    time.sleep(actual_wait)
                else:
                    logger.error(f"API request failed after {max_retries + 1} attempts: {e}")
                    raise

    def _extract_metadata_from_response(self, xml_response: str, runtime_dict: Dict[str, Optional[Paper]], papers_to_process: List[str]) -> Dict[str, Paper]:
        """
        Extract metadata from XML response for papers that need processing.
        
        Args:
            xml_response: Raw XML from arXiv API
            runtime_dict: Dictionary with None values for papers to process
            papers_to_process: List of paper IDs we're trying to process
            
        Returns:
            Complete dictionary with all Paper objects
        """
        logger.info(f"Extracting metadata from XML response")
        
        try:
            root = ET.fromstring(xml_response)
            processed_count = 0
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                try:
                    paper = self._parse_single_paper(entry)
                    if paper and paper.id in papers_to_process:
                        runtime_dict[paper.id] = paper
                        processed_count += 1
                        self.session_stats['successfully_scraped'] += 1
                        
                except Exception as e:
                    # Try to extract paper ID for error logging
                    paper_id = "unknown"
                    try:
                        id_element = entry.find('{http://www.w3.org/2005/Atom}id')
                        if id_element is not None:
                            paper_id = id_element.text.split('/')[-1].split('v')[0]
                    except:
                        pass
                    
                    logger.error(f"Failed to parse paper {paper_id}: {e}")
                    
                    # Create failed paper object if we can identify the ID
                    if paper_id != "unknown" and paper_id in papers_to_process:
                        failed_paper = Paper(
                            id=paper_id,
                            title="",
                            authors=[],
                            categories=[],
                            abstract="",
                            published_date=datetime.now(),
                            arxiv_url=None,
                            pdf_url=None
                        )
                        failed_paper.update_status("scraping_failed")
                        failed_paper.add_error(f"Metadata extraction failed: {str(e)}")
                        runtime_dict[paper_id] = failed_paper
                        self.session_stats['scraping_failed'] += 1
            
            # Handle any papers that weren't found in the XML
            for paper_id, paper in runtime_dict.items():
                if paper is None:
                    logger.warning(f"Paper {paper_id} not found in arXiv API response")
                    failed_paper = Paper(
                        id=paper_id,
                        title="",
                        authors=[],
                        categories=[],
                        abstract="",
                        published_date=datetime.now(),
                        arxiv_url=None,
                        pdf_url=None
                    )
                    failed_paper.update_status("scraping_failed")
                    failed_paper.add_error("Paper not found in arXiv API response")
                    runtime_dict[paper_id] = failed_paper
                    self.session_stats['scraping_failed'] += 1
            
            logger.info(f"Successfully processed {processed_count} papers")
            return runtime_dict
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML response for metadata extraction: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during metadata extraction: {e}")
            raise

    def _parse_single_paper(self, entry) -> Optional[Paper]:
        """
        Parse a single paper entry from XML.
        
        Args:
            entry: XML entry element
            
        Returns:
            Paper object or None if parsing fails
        """
        try:
            # Extract paper ID
            id_element = entry.find('{http://www.w3.org/2005/Atom}id')
            if id_element is None:
                return None
            
            arxiv_id = id_element.text.split('/')[-1]
            if 'v' in arxiv_id:
                arxiv_id = arxiv_id.split('v')[0]
            
            # Extract title
            title_element = entry.find('{http://www.w3.org/2005/Atom}title')
            title = title_element.text.strip() if title_element is not None else ""
            
            # Extract authors
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name_element = author.find('{http://www.w3.org/2005/Atom}name')
                if name_element is not None:
                    authors.append(name_element.text.strip())
            
            # Extract categories
            categories = []
            for category in entry.findall('{http://www.w3.org/2005/Atom}category'):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # Extract abstract
            summary_element = entry.find('{http://www.w3.org/2005/Atom}summary')
            abstract = summary_element.text.strip() if summary_element is not None else ""
            
            # Extract published date
            published_element = entry.find('{http://www.w3.org/2005/Atom}published')
            if published_element is not None:
                published_date = datetime.fromisoformat(published_element.text.replace('Z', '+00:00'))
            else:
                published_date = datetime.now()
            
            # Extract URLs from link elements
            arxiv_url = None
            pdf_url = None
            
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                rel = link.get('rel')
                href = link.get('href')
                type_attr = link.get('type')
                
                if rel == 'alternate' and type_attr == 'text/html':
                    arxiv_url = href
                elif rel == 'related' and type_attr == 'application/pdf':
                    pdf_url = href
            
            # Log missing URLs for debugging
            missing_urls = []
            if arxiv_url is None:
                missing_urls.append('arxiv_url')
            if pdf_url is None:
                missing_urls.append('pdf_url')
            
            if missing_urls:
                logger.warning(f"Paper {arxiv_id} missing URLs: {', '.join(missing_urls)}")
            
            # Create paper object
            paper = Paper(
                id=arxiv_id,
                title=title,
                authors=authors,
                categories=categories,
                abstract=abstract,
                published_date=published_date,
                arxiv_url=arxiv_url,
                pdf_url=pdf_url
            )
            paper.update_status("successfully_scraped")
            
            return paper
            
        except Exception as e:
            logger.error(f"Error parsing individual paper: {e}")
            return None

    def _clean_arxiv_categories(self, runtime_dict: Dict[str, Paper]) -> Dict[str, Paper]:
        """
        Clean up categories to keep only properly formatted arXiv categories.
        
        Keeps categories matching pattern: [a-z]{2,}\\.[A-Z]{2}
        Examples: cs.AI, stat.ML, math.OC, physics.HE
        Discards: ACM classifications, MSC codes, etc.
        
        Args:
            runtime_dict: Dictionary of paper_id -> Paper objects
            
        Returns:
            Dictionary with cleaned Paper objects
        """
        import re
        arxiv_pattern = re.compile(r'^[a-z]{2,}\.[A-Z]{2}$')
        
        cleaned_count = 0
        for paper_id, paper in runtime_dict.items():
            if paper and paper.categories:
                original_categories = paper.categories.copy()
                # Filter to keep only arXiv-formatted categories
                cleaned_categories = [cat for cat in paper.categories if arxiv_pattern.match(cat)]
                
                if len(cleaned_categories) < len(original_categories):
                    removed_categories = [cat for cat in original_categories if cat not in cleaned_categories]
                    paper.categories = cleaned_categories
                    cleaned_count += 1
                    
                    logger.info(f"Cleaned categories for paper {paper_id}: "
                               f"kept {cleaned_categories}, removed {removed_categories}")
        
        if cleaned_count > 0:
            logger.info(f"Category cleaning completed: {cleaned_count} papers had categories cleaned")
        else:
            logger.info("Category cleaning completed: no papers needed cleaning")
        
        return runtime_dict

    def _log_session_summary(self) -> None:
        """Log summary of scraping session."""
        logger.info(f"Test scraping session completed:")
        logger.info(f"  Successfully scraped: {self.session_stats['successfully_scraped']}")
        logger.info(f"  Scraping failed: {self.session_stats['scraping_failed']}")
        logger.info(f"  API calls made: {self.session_stats['api_calls']}")
        logger.info(f"  Retries: {self.session_stats['retries']}")


def run(run_mode: str, run_value: str) -> Dict[str, Paper]:
    """
    Main entry point for the test scraper module.
    
    Args:
        run_mode: Must be 'test'
        run_value: Path to text file containing paper IDs
        
    Returns:
        Dictionary of paper_id -> Paper objects
    """
    scraper = ArxivTestScraper()
    return scraper.run(run_mode, run_value)
