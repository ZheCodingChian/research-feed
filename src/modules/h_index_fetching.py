"""
H-Index Fetching Module

This module fetches H-index data for valuable papers (Must Read, Should Read) from Semantic Scholar.
It uses a cascading search strategy: full arXiv ID -> base arXiv ID -> title search.
Processing is sequential with rate limiting to respect Semantic Scholar's API limits.
"""

import logging
import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from paper import Paper, AuthorHIndex

logger = logging.getLogger('H_INDEX_FETCHING')


class HIndexFetching:
    """
    Handles fetching H-index data from Semantic Scholar for valuable papers.
    
    This class processes papers that have "Must Read" or "Should Read" recommendations
    and fetches author H-index data using Semantic Scholar's public API.
    """
    
    def __init__(self, config: dict):
        """Initialize with configuration settings."""
        self.config = config
        self.base_url = config['api_base_url']
        self.timeout = config['timeout']
        self.max_retries = config['max_retries']
        self.rate_limit_delay = config['rate_limit_delay']
        self.notable_threshold = config['notable_h_index_threshold']
        
        # API fields to request
        self.api_fields = "paperId,title,url,authors,authors.name,authors.authorId,authors.url,authors.hIndex"
    
    def run(self, papers: Dict[str, Paper]) -> Dict[str, Paper]:
        """
        Run H-index fetching for valuable papers.
        
        Args:
            papers: Dictionary of paper_id -> Paper objects
            
        Returns:
            The updated papers dictionary with H-index data
        """
        logger.info(f"Starting H-index fetching for {len(papers)} papers")
        
        # Step 1: Identify papers needing H-index fetching
        papers_to_process = self._identify_target_papers(papers)
        skipped_papers = len(papers) - len(papers_to_process)
        
        if not papers_to_process:
            logger.info("No papers require H-index fetching")
            return papers
        
        # Count skip reasons for detailed logging
        already_completed = sum(1 for p in papers.values() if p.can_skip_h_index_fetching())
        not_recommended = sum(1 for p in papers.values() if not p.is_valuable_paper() and not p.can_skip_h_index_fetching())
        
        logger.info(f"Fetching H-index for {len(papers_to_process)} papers, skipping {skipped_papers} papers "
                   f"({already_completed} already completed, {not_recommended} not recommended)")
        
        # Step 2: Process papers sequentially with rate limiting
        for i, paper in enumerate(papers_to_process, 1):
            try:
                self._fetch_h_index_for_paper(paper)
                
                # Log progress for each paper
                if paper.h_index_status == "completed":
                    method_name = paper.h_index_fetch_method.replace('_', ' ')
                    logger.info(f"{paper.id} - found via {method_name}, found {paper.authors_found}/{paper.total_authors} authors, "
                               f"highest H-index: {paper.highest_h_index}")
                else:
                    logger.warning(f"{paper.id} - failed to fetch H-index data")
                
                # Rate limiting: wait between requests (except for the last one)
                if i < len(papers_to_process):
                    time.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error processing paper {paper.id}: {e}")
                paper.update_h_index_status("failed")
                paper.add_error(f"H-index fetching failed: {str(e)}")
        
        # Step 3: Log summary statistics
        completed_count = sum(1 for p in papers.values() if p.h_index_status == "completed")
        failed_count = sum(1 for p in papers.values() if p.h_index_status == "failed")
        
        logger.info(f"H-index fetching complete: {completed_count}/{len(papers_to_process)} successful, {failed_count} failed")
        
        return papers
    
    def _identify_target_papers(self, papers: Dict[str, Paper]) -> List[Paper]:
        """
        Identify papers that need H-index fetching.
        
        Args:
            papers: Dictionary of papers
            
        Returns:
            List of papers that need H-index fetching
        """
        papers_to_process = []
        
        for paper in papers.values():
            # Skip if already processed
            if paper.can_skip_h_index_fetching():
                continue
            
            # Only process valuable papers
            if paper.is_valuable_paper():
                papers_to_process.append(paper)
                logger.debug(f"Paper {paper.id} needs H-index fetching")
        
        return papers_to_process
    
    def _fetch_h_index_for_paper(self, paper: Paper) -> None:
        """
        Fetch H-index data for a single paper using cascading search strategy.
        
        Args:
            paper: Paper object to fetch H-index data for
        """
        logger.debug(f"{paper.id} - Starting H-index fetching")
        
        # Extract arXiv ID (remove 'v' and version number for base ID)
        arxiv_id = paper.id
        base_arxiv_id = arxiv_id.split('v')[0] if 'v' in arxiv_id else arxiv_id
        
        # Strategy 1: Search by full arXiv ID
        ss_data = self._search_by_full_arxiv_id(arxiv_id)
        if ss_data:
            self._process_semantic_scholar_data(paper, ss_data, "full_id")
            return
        
        # Strategy 2: Search by base arXiv ID (if different from full ID)
        if base_arxiv_id != arxiv_id:
            ss_data = self._search_by_base_arxiv_id(base_arxiv_id)
            if ss_data:
                self._process_semantic_scholar_data(paper, ss_data, "base_id")
                return
        
        # Strategy 3: Search by title
        if paper.title:
            ss_data = self._search_by_title(paper.title)
            if ss_data:
                self._process_semantic_scholar_data(paper, ss_data, "title_search")
                return
        
        # All strategies failed
        paper.update_h_index_status("failed")
        paper.add_error("H-index fetching failed: not found in Semantic Scholar")
        logger.debug(f"{paper.id} - not found in Semantic Scholar")
    
    def _search_by_full_arxiv_id(self, arxiv_id: str) -> Optional[Dict]:
        """Search Semantic Scholar by full arXiv ID."""
        url = f"{self.base_url}/paper/arXiv:{arxiv_id}"
        params = {"fields": self.api_fields}
        return self._make_api_request(url, params)
    
    def _search_by_base_arxiv_id(self, base_arxiv_id: str) -> Optional[Dict]:
        """Search Semantic Scholar by base arXiv ID."""
        url = f"{self.base_url}/paper/arXiv:{base_arxiv_id}"
        params = {"fields": self.api_fields}
        return self._make_api_request(url, params)
    
    def _search_by_title(self, title: str) -> Optional[Dict]:
        """Search Semantic Scholar by paper title."""
        url = f"{self.base_url}/paper/search"
        params = {
            "query": title,
            "fields": self.api_fields,
            "limit": 1
        }
        response = self._make_api_request(url, params)
        
        # Extract first result from search response
        if response and 'data' in response and response['data']:
            return response['data'][0]
        return None
    
    def _make_api_request(self, url: str, params: dict = None) -> Optional[Dict]:
        """
        Make API request to Semantic Scholar with retry logic.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data or None if failed
        """
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # Not found - this is expected for some searches
                    return None
                elif response.status_code == 429:
                    # Rate limited - wait longer and retry
                    if attempt < self.max_retries:
                        wait_time = (2 ** attempt) * self.rate_limit_delay
                        logger.warning(f"Rate limited, waiting {wait_time:.1f}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limited after all retries")
                        return None
                else:
                    logger.warning(f"API request failed with status {response.status_code}")
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    logger.warning(f"Request timeout, attempt {attempt + 1}/{self.max_retries + 1}")
                    time.sleep(1)
                    continue
                else:
                    logger.error("Request timeout after all retries")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
        
        return None
    
    def _process_semantic_scholar_data(self, paper: Paper, ss_data: Dict, method: str) -> None:
        """
        Process Semantic Scholar data and update paper object.
        
        Args:
            paper: Paper object to update
            ss_data: Semantic Scholar API response data
            method: Search method used (full_id, base_id, title_search)
        """
        try:
            # Extract basic paper information
            paper.semantic_scholar_url = ss_data.get('url')
            paper.h_index_fetch_method = method
            
            # Process authors
            authors_data = ss_data.get('authors', [])
            paper.total_authors = len(authors_data)
            
            # Extract H-index data for each author
            author_h_indexes = []
            authors_with_data = 0
            h_indexes = []
            
            for author_data in authors_data:
                author = AuthorHIndex(
                    name=author_data.get('name', 'Unknown'),
                    profile_url=author_data.get('url'),
                    h_index=author_data.get('hIndex')
                )
                author_h_indexes.append(author)
                
                if author.h_index is not None:
                    authors_with_data += 1
                    h_indexes.append(author.h_index)
            
            paper.author_h_indexes = author_h_indexes
            paper.authors_found = authors_with_data
            
            # Calculate statistics
            if h_indexes:
                paper.highest_h_index = max(h_indexes)
                paper.average_h_index = sum(h_indexes) / len(h_indexes)
                paper.notable_authors_count = sum(1 for h in h_indexes if h > self.notable_threshold)
            else:
                paper.highest_h_index = None
                paper.average_h_index = None
                paper.notable_authors_count = 0
            
            paper.update_h_index_status("completed")
            logger.debug(f"{paper.id} - H-index data processed successfully")
            
        except Exception as e:
            paper.update_h_index_status("failed")
            paper.add_error(f"H-index data processing failed: {str(e)}")
            logger.error(f"{paper.id} - Failed to process Semantic Scholar data: {e}")


def run(papers: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Main entry point for H-index fetching module.
    
    Args:
        papers: Dictionary of paper_id -> Paper objects
        config: Configuration dictionary
        
    Returns:
        Updated papers dictionary with H-index data
    """
    fetcher = HIndexFetching(config)
    return fetcher.run(papers)
