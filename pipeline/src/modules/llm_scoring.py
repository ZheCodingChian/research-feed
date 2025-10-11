"""
LLM Scoring Module

This module scores papers that have passed LLM validation with at least one Highly Relevant, 
Moderately Relevant, or Tangentially Relevant topic. It provides detailed scoring across three 
dimensions: novelty, impact, and recommendation using Grok 3 Mini via OpenRouter API.
"""

import logging
import json
import os
import time
import random
import requests
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from typing import Dict, List, Optional
from paper import Paper
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger('LLM_SCORING')

class LLMScoring:
    """
    Handles LLM-based scoring of paper quality across multiple dimensions.
    
    This class takes papers that have at least one Highly Relevant, Moderately Relevant, 
    or Tangentially Relevant topic from LLM validation and provides detailed scoring for 
    novelty, impact, and recommendation using an LLM.
    """
    
    def __init__(self, config: dict):
        """Initialize with configuration settings."""
        self.config = config
        
        # Get API key from environment
        api_key = os.getenv(config['api_key_env'])
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {config['api_key_env']}")
        
        self.api_key = api_key
        
        # Initialize semaphore for concurrency control
        self.semaphore = Semaphore(config['max_workers'])
    
    def run(self, papers: Dict[str, Paper]) -> Dict[str, Paper]:
        """
        Run LLM scoring on papers that have at least one Highly Relevant, Moderately Relevant, or Tangentially Relevant topic.
        
        Args:
            papers: Dictionary of paper_id -> Paper objects
            
        Returns:
            The updated papers dictionary with LLM scoring results
        """
        logger.info(f"Starting LLM scoring for {len(papers)} papers")
        
        # Step 1: Identify papers needing scoring
        papers_to_process = self._identify_papers_for_scoring(papers)
        skipped_papers = len(papers) - len(papers_to_process)
        
        if not papers_to_process:
            logger.info("No papers require LLM scoring")
            return papers
        
        logger.info(f"Processing {len(papers_to_process)} papers for LLM scoring using {self.config['max_workers']} workers")
        
        # Step 2: Process papers in parallel (no batching for this module)
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Submit all papers
            future_to_paper = {
                executor.submit(self._process_paper_with_retry_wrapper, paper, i + 1, len(papers_to_process)): paper
                for i, paper in enumerate(papers_to_process)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    future.result()  # This will raise any exception that occurred
                except Exception as e:
                    logger.error(f"Unexpected error processing paper {paper.id}: {e}")
        
        # Step 3: Log summary statistics
        completed_count = sum(1 for p in papers.values() if p.llm_score_status == "completed")
        failed_count = sum(1 for p in papers.values() if p.llm_score_status == "failed")
        not_relevant_count = sum(1 for p in papers.values() if p.llm_score_status == "not_relevant_enough")
        
        logger.info(f"LLM scoring complete: {completed_count}/{len(papers)} successful, {failed_count} failed, {not_relevant_count} not relevant enough, {skipped_papers} skipped")
        
        return papers
    
    def _identify_papers_for_scoring(self, papers: Dict[str, Paper]) -> List[Paper]:
        """
        Identify papers that need LLM scoring.
        
        Args:
            papers: Dictionary of papers
            
        Returns:
            List of papers that need scoring
        """
        papers_to_process = []
        
        # Counters for detailed logging
        no_llm_validation = 0
        already_scored = 0
        insufficient_relevance = 0
        
        for paper in papers.values():
            # Check if LLM validation is completed
            if not paper.is_llm_validation_completed():
                no_llm_validation += 1
                continue
            
            # Check if already scored
            if paper.can_skip_llm_scoring():
                already_scored += 1
                continue
            
            # Check if has at least one Highly/Moderately/Tangentially Relevant topic
            if paper.has_highly_relevant_topic():
                papers_to_process.append(paper)
                logger.debug(f"Paper {paper.id} needs scoring")
            else:
                # Mark as not relevant enough
                paper.update_llm_score_status("not_relevant_enough")
                insufficient_relevance += 1
                logger.debug(f"Paper {paper.id} has no Highly/Moderately/Tangentially Relevant topics, marked as not_relevant_enough")
        
        # Log detailed skip statistics
        total_skipped = no_llm_validation + already_scored + insufficient_relevance
        if total_skipped > 0:
            skip_details = []
            if no_llm_validation > 0:
                skip_details.append(f"{no_llm_validation} no LLM validation")
            if already_scored > 0:
                skip_details.append(f"{already_scored} already scored")
            if insufficient_relevance > 0:
                skip_details.append(f"{insufficient_relevance} insufficient relevance (below Tangentially Relevant)")
            
            logger.info(f"Skipping {total_skipped} papers: {', '.join(skip_details)}")
        
        return papers_to_process
    
    def _process_paper_with_retry_wrapper(self, paper: Paper, paper_index: int, total_papers: int) -> None:
        """
        Wrapper for parallel processing that handles semaphore acquisition.
        
        Args:
            paper: Paper object to process
            paper_index: Current paper index (1-based)
            total_papers: Total number of papers being processed
        """
        with self.semaphore:  # Acquire semaphore to limit concurrent API calls
            self._process_paper_with_retry(paper, paper_index, total_papers)
    
    def _process_paper_with_retry(self, paper: Paper, paper_index: int, total_papers: int) -> None:
        """
        Process a single paper with retry logic.
        
        Args:
            paper: Paper object to process
            paper_index: Current paper index (1-based)
            total_papers: Total number of papers being processed
        """
        max_retries = 3  # Fixed at 3 retries as requested
        
        for attempt in range(max_retries + 1):
            try:
                self._process_single_paper(paper)
                paper.update_llm_score_status("completed")
                logger.info(f"Paper {paper_index}/{total_papers}: {paper.id} - LLM scoring SUCCESS")
                return
                
            except Exception as e:
                error_msg = str(e)
                
                # Check for rate limiting (429 error) and add extra delay
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    extra_delay = random.uniform(1.0, 3.0)
                    logger.warning(f"Paper {paper_index}/{total_papers}: {paper.id} - rate limited, waiting {extra_delay:.1f}s")
                    time.sleep(extra_delay)
                
                # Check for token limit exceeded
                if "token" in error_msg.lower() and ("limit" in error_msg.lower() or "exceed" in error_msg.lower()):
                    logger.error(f"Paper {paper_index}/{total_papers}: {paper.id} - token limit exceeded, marking as failed")
                    paper.update_llm_score_status("failed")
                    paper.add_error(f"LLM scoring failed: token limit exceeded")
                    return
                
                if attempt == max_retries:
                    # Final attempt failed
                    paper.update_llm_score_status("failed")
                    paper.add_error(f"LLM scoring failed after {max_retries + 1} attempts: {error_msg}")
                    logger.error(f"Paper {paper_index}/{total_papers}: {paper.id} - LLM scoring FAILED after all retries: {error_msg}")
                else:
                    # Log retry attempt
                    logger.warning(f"Paper {paper_index}/{total_papers}: {paper.id} - attempt {attempt + 1}/{max_retries + 1} FAILED: {error_msg}")
                    # Wait before retry with exponential backoff
                    retry_delay = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(retry_delay)
    
    def _process_single_paper(self, paper: Paper) -> None:
        """
        Process a single paper through LLM scoring.
        
        Args:
            paper: Paper object to score
            
        Raises:
            Exception: If scoring fails for any reason
        """
        logger.debug(f"{paper.id} - Starting LLM scoring")
        
        # Step 1: Build prompt
        prompt = self._build_scoring_prompt(paper)
        
        # Step 2: Make API call
        response_content = self._make_api_call(prompt)
        
        # Step 3: Parse and validate response
        scoring_results = self._parse_xml_response(response_content)
        
        # Step 4: Update paper object
        self._update_paper_with_results(paper, scoring_results)
    
    def _build_scoring_prompt(self, paper: Paper) -> str:
        """
        Build the scoring prompt for the LLM.
        
        Args:
            paper: Paper object to score
            
        Returns:
            Formatted prompt string
        """
        # Build paper information section
        title = paper.title or "No title available"
        abstract = paper.abstract or "No abstract available"
        authors = ", ".join(paper.authors) if paper.authors else "No authors available"
        categories = ", ".join(paper.categories) if paper.categories else "No categories available"
        
        paper_info = f"Title: {title}\nAuthors: {authors}\nCategories: {categories}\nAbstract: {abstract}"
        
        # Add introduction if available
        if paper.introduction_text:
            paper_info += f"\nIntroduction: {paper.introduction_text}"
        
        # Build the complete prompt
        prompt = f"""You are an expert AI Research Analyst. Your mission is to assess academic research papers based on their title, abstract, and introduction (if any). Your evaluation must be objective and insightful.

Your Task:

1. Read the paper's text provided. Understand the paper.
2. Summarize the Paper: Write a single, concise paragraph that synthesizes the paper's core objectives, methodology, and key findings as presented in the text.
3. Evaluate the Paper: Score the paper according to the three dimensions detailed in the rubric below. For each dimension, you must select the single most fitting category and provide a concise one-sentence justification for your choice.

Evaluation Dimensions & Scoring Rubric

Novelty: The nature of the paper's contribution.
- Groundbreaking: Introduces a fundamentally new problem, paradigm, or breakthrough technique that redefines how we approach an area. Represents a major shift in thinking or methodology.
- Significant: Presents a novel architecture, method, or problem formulation that meaningfully advances current approaches. Offers fresh perspectives or solutions that move the field forward in important ways.
- Incremental: Provides refinements, extensions, or clever combinations of existing methods. The contribution is solid but builds directly on established work without introducing fundamentally new concepts.
- Minimal: Largely derivative work that confirms known findings or makes trivial modifications to existing approaches. Offers little to no new insight or methodology.

Potential Impact: The likely influence of the work.
- Transformative: Could reshape the field or enable entirely new research directions and applications across multiple domains. Has potential to become foundational work that others build upon for years.
- Substantial: Likely to influence a broad range of work within the field and spawn follow-up research. Will be widely cited and adopted by researchers working on related problems.
- Moderate: Will be recognized and built upon within its specific subfield or application area. Relevant to practitioners in focused domains but won't drive field-wide changes.
- Negligible: Unlikely to influence future research or applications. Addresses problems too narrow or presents work too limited to generate meaningful follow-up interest.

Final Recommendation: The action an informed reader should take.
- Must Read: A high-quality paper with significant contributions or novel insights. Work that advances the field meaningfully and you should prioritize reading.
- Should Read: A solid paper with valuable contributions. Represents good work worth your attention when you have time, but may be more incremental. Second to Must Read papers.
- Can Skip: An interesting paper, but not essential. The contribution is incremental, niche, or a less impactful version of another idea.
- Ignore: Not recommended for review; lacks substance, relevance, or is poorly presented.

Paper Information:
{paper_info}

Respond ONLY in this exact XML format:

<paper_evaluation>
    <summary><![CDATA[Your single paragraph summary here]]></summary>
    <novelty>
        <score>Groundbreaking|Significant|Incremental|Minimal</score>
        <justification><![CDATA[1-2 sentences explaining your choice]]></justification>
    </novelty>
    <impact>
        <score>Transformative|Substantial|Moderate|Negligible</score>
        <justification><![CDATA[1-2 sentences explaining your choice]]></justification>
    </impact>
    <recommendation>
        <score>Must Read|Should Read|Can Skip|Ignore</score>
        <justification><![CDATA[1-2 sentences explaining your choice]]></justification>
    </recommendation>
</paper_evaluation>

Important: Evaluate all three dimensions and use only the specified categories. Keep justifications concise but informative. Wrap all text content in CDATA tags."""
        
        return prompt
    
    def _make_api_call(self, prompt: str) -> str:
        """
        Make API call to OpenRouter.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Response content from the API
            
        Raises:
            Exception: If API call fails
        """
        url = f"{self.config['api_base_url']}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config['model'],
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent responses
            "max_tokens": 4000   # Enough for detailed justifications
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=self.config['timeout']
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'choices' not in response_data or not response_data['choices']:
                raise Exception("No choices in API response")
            
            content = response_data['choices'][0]['message']['content']
            if not content:
                raise Exception("Empty content in API response")
            
            return content
            
        except requests.exceptions.Timeout:
            raise Exception("API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON in API response")
        except KeyError as e:
            raise Exception(f"Missing key in API response: {str(e)}")
    
    def _parse_xml_response(self, response_content: str) -> Dict[str, str]:
        """
        Parse XML response from LLM.
        
        Args:
            response_content: Raw response content from LLM
            
        Returns:
            Dictionary containing scoring results
            
        Raises:
            Exception: If parsing fails or response is invalid
        """
        try:
            # Parse XML
            root = ET.fromstring(response_content)
            
            if root.tag != 'paper_evaluation':
                raise Exception(f"Invalid root tag: {root.tag}, expected 'paper_evaluation'")
            
            results = {}
            
            # Extract summary
            summary_element = root.find('summary')
            if summary_element is None or not summary_element.text:
                raise Exception("Missing or empty summary")
            results['summary'] = summary_element.text.strip()
            
            # Extract novelty
            novelty_element = root.find('novelty')
            if novelty_element is None:
                raise Exception("Missing novelty element")
            
            novelty_score = novelty_element.find('score')
            novelty_justification = novelty_element.find('justification')
            
            if novelty_score is None or not novelty_score.text:
                raise Exception("Missing or empty novelty score")
            if novelty_justification is None or not novelty_justification.text:
                raise Exception("Missing or empty novelty justification")
            
            valid_novelty_scores = {'Groundbreaking', 'Significant', 'Incremental', 'Minimal'}
            if novelty_score.text.strip() not in valid_novelty_scores:
                raise Exception(f"Invalid novelty score: {novelty_score.text.strip()}")
            
            results['novelty_score'] = novelty_score.text.strip()
            results['novelty_justification'] = novelty_justification.text.strip()
            
            # Extract impact
            impact_element = root.find('impact')
            if impact_element is None:
                raise Exception("Missing impact element")
            
            impact_score = impact_element.find('score')
            impact_justification = impact_element.find('justification')
            
            if impact_score is None or not impact_score.text:
                raise Exception("Missing or empty impact score")
            if impact_justification is None or not impact_justification.text:
                raise Exception("Missing or empty impact justification")
            
            valid_impact_scores = {'Transformative', 'Substantial', 'Moderate', 'Negligible'}
            if impact_score.text.strip() not in valid_impact_scores:
                raise Exception(f"Invalid impact score: {impact_score.text.strip()}")
            
            results['impact_score'] = impact_score.text.strip()
            results['impact_justification'] = impact_justification.text.strip()
            
            # Extract recommendation
            recommendation_element = root.find('recommendation')
            if recommendation_element is None:
                raise Exception("Missing recommendation element")
            
            recommendation_score = recommendation_element.find('score')
            recommendation_justification = recommendation_element.find('justification')
            
            if recommendation_score is None or not recommendation_score.text:
                raise Exception("Missing or empty recommendation score")
            if recommendation_justification is None or not recommendation_justification.text:
                raise Exception("Missing or empty recommendation justification")
            
            valid_recommendation_scores = {'Must Read', 'Should Read', 'Can Skip', 'Ignore'}
            if recommendation_score.text.strip() not in valid_recommendation_scores:
                raise Exception(f"Invalid recommendation score: {recommendation_score.text.strip()}")
            
            results['recommendation_score'] = recommendation_score.text.strip()
            results['recommendation_justification'] = recommendation_justification.text.strip()
            
            return results
            
        except ET.ParseError as e:
            raise Exception(f"XML parsing error: {str(e)}")
        except Exception as e:
            # Re-raise our custom exceptions
            if "Invalid root tag" in str(e) or "Missing" in str(e) or "Invalid" in str(e):
                raise
            else:
                raise Exception(f"Response parsing error: {str(e)}")
    
    def _update_paper_with_results(self, paper: Paper, scoring_results: Dict[str, str]) -> None:
        """
        Update paper object with scoring results.
        
        Args:
            paper: Paper object to update
            scoring_results: Dictionary of scoring results
        """
        paper.summary = scoring_results['summary']
        paper.novelty_score = scoring_results['novelty_score']
        paper.novelty_justification = scoring_results['novelty_justification']
        paper.impact_score = scoring_results['impact_score']
        paper.impact_justification = scoring_results['impact_justification']
        paper.recommendation_score = scoring_results['recommendation_score']
        paper.recommendation_justification = scoring_results['recommendation_justification']

def run(papers: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Run the LLM scoring module on a batch of papers.
    
    This is the main entry point for the module, matching the common interface
    pattern used by other modules in the pipeline.
    
    Args:
        papers: Dictionary of paper_id -> Paper objects
        config: Configuration dictionary with LLM scoring parameters
        
    Returns:
        The updated papers dictionary
    """
    processor = LLMScoring(config)
    return processor.run(papers)
