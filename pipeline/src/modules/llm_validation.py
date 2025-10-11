"""
LLM Validation Module

This module validates paper relevance to research topics using Large Language Models.
It processes papers that have passed the embedding similarity threshold and gets
detailed relevance assessments with justifications from an LLM.
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

logger = logging.getLogger('LLM_VALIDATION')

class LLMValidation:
    """
    Handles LLM-based validation of paper relevance to research topics.
    
    This class takes papers with embedding similarity scores, identifies those
    that meet the threshold criteria, and validates them using an LLM through
    OpenRouter API with XML-formatted responses.
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
        
        # Topic descriptions for prompt building
        self.topic_descriptions = {
            "Agentic Artificial Intelligence": "Agentic AI and Agentic Workflows - Systems where autonomous AI agents, typically powered by large language models, can perceive high-level goals, decompose them into subtasks, use external tools like APIs or code execution, and orchestrate multi-step workflows with minimal human intervention. Key features include task decomposition, tool use, planning modules, and often hierarchical multi-agent coordination. If the system is just a chatbot or single-prompt LLM without autonomous planning and tool use, it is not agentic AI.",
            "Proximal Policy Optimization": "Proximal Policy Optimization - A specific policy gradient reinforcement learning algorithm that uses a clipped surrogate objective to prevent large, destructive policy updates during training. PPO is an actor-critic method known for stability and sample efficiency. The paper must explicitly mention PPO or describe its clipped probability ratio mechanism. General RL papers or other policy gradient methods like TRPO or A3C without PPO are not PPO papers.",
            "Reinforcement Learning": "Reinforcement Learning - A machine learning paradigm where an autonomous agent learns to make sequential decisions by interacting with an environment to maximize cumulative reward. The problem is formalized as a Markov Decision Process with states, actions, and reward signals. The agent learns a policy through trial-and-error using algorithms like Q-learning, policy gradients, or actor-critic methods. If the paper does not involve an agent learning from rewards through environment interaction, it is not reinforcement learning.",
            "Reasoning Models": "General Reasoning Models - AI systems, particularly large language models, designed to perform complex multi-step logical deduction, mathematical problem-solving, and structured thinking. These models use techniques like chain-of-thought prompting, tree-of-thoughts exploration, self-verification, and explicit step-by-step decomposition to solve problems requiring reasoning beyond pattern matching. Evaluated on benchmarks like mathematical reasoning, logical inference, or multi-hop question answering. If the model performs simple question answering without explicit reasoning traces or evaluation on reasoning tasks, it is not a reasoning model paper.",
            "Inference Time Scaling": "Inference Time Scaling - Techniques that allocate additional computational resources during model inference, after training is complete, to improve prediction accuracy. This includes generating multiple candidate outputs with verifier-based selection, iterative self-correction, extended chain-of-thought reasoning, beam search over reasoning paths, or adaptive compute based on problem difficulty. If the paper focuses on training-time scaling or standard single-pass inference without deliberation mechanisms, it is not inference time scaling."
        }
    
    def run(self, papers: Dict[str, Paper]) -> Dict[str, Paper]:
        """
        Run LLM validation on papers that meet the similarity threshold criteria.
        
        Args:
            papers: Dictionary of paper_id -> Paper objects
            
        Returns:
            The updated papers dictionary with LLM validation results
        """
        logger.info(f"Starting LLM validation for {len(papers)} papers")
        
        # Step 1: Identify papers needing validation
        papers_to_process = self._identify_papers_for_validation(papers)
        skipped_papers = len(papers) - len(papers_to_process)
        
        if not papers_to_process:
            logger.info("No papers require LLM validation")
            return papers
        
        logger.info(f"Processing {len(papers_to_process)} papers for LLM validation using {self.config['max_workers']} workers")
        
        # Step 2: Process papers in parallel batches
        batch_size = self.config['batch_size']
        batches = [papers_to_process[i:i + batch_size] for i in range(0, len(papers_to_process), batch_size)]
        
        total_processed = 0
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)} with {len(batch)} papers")
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
                # Submit all papers in the batch
                future_to_paper = {
                    executor.submit(self._process_paper_with_retry_wrapper, paper, total_processed + i + 1, len(papers_to_process)): paper
                    for i, paper in enumerate(batch)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_paper):
                    paper = future_to_paper[future]
                    try:
                        future.result()  # This will raise any exception that occurred
                    except Exception as e:
                        logger.error(f"Unexpected error processing paper {paper.id}: {e}")
            
            total_processed += len(batch)
            
            # Rate limiting between batches (not individual papers)
            if batch_num < len(batches):  # Don't delay after last batch
                delay = self.config['rate_limit_delay'] + random.uniform(0, self.config['jitter'])
                time.sleep(delay)
        
        # Step 3: Log summary statistics
        completed_count = sum(1 for p in papers.values() if p.llm_validation_status == "completed")
        failed_count = sum(1 for p in papers.values() if p.llm_validation_status == "failed")
        
        logger.info(f"LLM validation complete: {completed_count}/{len(papers)} successful, {failed_count} failed, {skipped_papers} skipped")
        
        return papers
    
    def _identify_papers_for_validation(self, papers: Dict[str, Paper]) -> List[Paper]:
        """
        Identify papers that need LLM validation.
        
        Args:
            papers: Dictionary of papers
            
        Returns:
            List of papers that need validation
        """
        papers_to_process = []
        threshold = self.config['similarity_threshold']
        
        # Counters for detailed logging
        no_embedding_data = 0
        already_validated = 0
        no_topics_above_threshold = 0
        
        for paper in papers.values():
            # Check specific skip reasons for detailed logging
            if not paper.is_embedding_completed():
                no_embedding_data += 1
                continue
            
            if paper.llm_validation_status in ["completed", "failed"]:
                already_validated += 1
                continue
            
            # Check if any topic scores are above threshold
            topic_scores = {
                'Agentic Artificial Intelligence': paper.agentic_ai_score,
                'Proximal Policy Optimization': paper.proximal_policy_optimization_score,
                'Reinforcement Learning': paper.reinforcement_learning_score,
                'Reasoning Models': paper.reasoning_models_score,
                'Inference Time Scaling': paper.inference_time_scaling_score
            }
            
            above_threshold_topics = [
                topic for topic, score in topic_scores.items()
                if score is not None and score >= threshold
            ]
            
            if above_threshold_topics:
                # Set below-threshold topics to "below_threshold" justification
                self._set_below_threshold_justifications(paper, topic_scores, threshold)
                papers_to_process.append(paper)
                
                logger.debug(f"Paper {paper.id} needs validation for topics: {', '.join(above_threshold_topics)}")
            else:
                # All topics below threshold, set all justifications and mark as completed
                self._set_all_below_threshold(paper)
                paper.update_llm_validation_status("completed")
                no_topics_above_threshold += 1
                logger.debug(f"Paper {paper.id} has no topics above threshold, marked as completed")
        
        # Log detailed skip statistics
        total_skipped = no_embedding_data + already_validated + no_topics_above_threshold
        if total_skipped > 0:
            skip_details = []
            if no_embedding_data > 0:
                skip_details.append(f"{no_embedding_data} no embedding data")
            if already_validated > 0:
                skip_details.append(f"{already_validated} already validated")
            if no_topics_above_threshold > 0:
                skip_details.append(f"{no_topics_above_threshold} no topics above threshold")
            
            logger.info(f"Skipping {total_skipped} papers: {', '.join(skip_details)}")
        
        return papers_to_process
    
    def _set_below_threshold_justifications(self, paper: Paper, topic_scores: Dict[str, Optional[float]], threshold: float) -> None:
        """Set justifications for topics below threshold."""
        below_threshold_justification = "below_threshold"
        
        if topic_scores['Agentic Artificial Intelligence'] is None or topic_scores['Agentic Artificial Intelligence'] < threshold:
            paper.agentic_ai_justification = below_threshold_justification
        if topic_scores['Proximal Policy Optimization'] is None or topic_scores['Proximal Policy Optimization'] < threshold:
            paper.proximal_policy_optimization_justification = below_threshold_justification
        if topic_scores['Reinforcement Learning'] is None or topic_scores['Reinforcement Learning'] < threshold:
            paper.reinforcement_learning_justification = below_threshold_justification
        if topic_scores['Reasoning Models'] is None or topic_scores['Reasoning Models'] < threshold:
            paper.reasoning_models_justification = below_threshold_justification
        if topic_scores['Inference Time Scaling'] is None or topic_scores['Inference Time Scaling'] < threshold:
            paper.inference_time_scaling_justification = below_threshold_justification
    
    def _set_all_below_threshold(self, paper: Paper) -> None:
        """Set all topic justifications to below_threshold."""
        below_threshold_justification = "below_threshold"
        paper.agentic_ai_justification = below_threshold_justification
        paper.proximal_policy_optimization_justification = below_threshold_justification
        paper.reinforcement_learning_justification = below_threshold_justification
        paper.reasoning_models_justification = below_threshold_justification
        paper.inference_time_scaling_justification = below_threshold_justification
    
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
        max_retries = self.config['max_retries']
        
        for attempt in range(max_retries + 1):
            try:
                validated_topics = self._process_single_paper(paper)
                paper.update_llm_validation_status("completed")
                logger.info(f"Paper {paper_index}/{total_papers}: {paper.id} - LLM validation SUCCESS for topics: {', '.join(validated_topics)}")
                return
                
            except Exception as e:
                error_msg = str(e)
                
                # Check for rate limiting (429 error) and add extra delay
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    extra_delay = random.uniform(1.0, 3.0)
                    logger.warning(f"Paper {paper_index}/{total_papers}: {paper.id} - rate limited, waiting {extra_delay:.1f}s")
                    time.sleep(extra_delay)
                
                if attempt == max_retries:
                    # Final attempt failed
                    paper.update_llm_validation_status("failed")
                    paper.add_error(f"LLM validation failed after {max_retries + 1} attempts: {error_msg}")
                    logger.error(f"Paper {paper_index}/{total_papers}: {paper.id} - LLM validation FAILED after all retries: {error_msg}")
                else:
                    # Log retry attempt
                    logger.warning(f"Paper {paper_index}/{total_papers}: {paper.id} - attempt {attempt + 1}/{max_retries + 1} FAILED: {error_msg}")
                    # Wait before retry with exponential backoff
                    retry_delay = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(retry_delay)
    
    def _process_single_paper(self, paper: Paper) -> List[str]:
        """
        Process a single paper through LLM validation.
        
        Args:
            paper: Paper object to validate
            
        Returns:
            List of topics that were validated
            
        Raises:
            Exception: If validation fails for any reason
        """
        # Step 1: Identify topics to validate
        topics_to_validate = self._get_topics_to_validate(paper)
        
        if not topics_to_validate:
            raise Exception("No topics above threshold found for validation")
        
        logger.debug(f" {paper.id} - Validating topics: {', '.join(topics_to_validate)}")
        
        # Step 2: Build prompt
        prompt = self._build_validation_prompt(paper, topics_to_validate)
        
        # Step 3: Make API call
        response_content = self._make_api_call(prompt)
        
        # Step 4: Parse and validate response
        validation_results = self._parse_xml_response(response_content, topics_to_validate)
        
        # Step 5: Update paper object
        self._update_paper_with_results(paper, validation_results)
        
        return topics_to_validate
    
    def _get_topics_to_validate(self, paper: Paper) -> List[str]:
        """Get list of topics that need validation (above threshold)."""
        threshold = self.config['similarity_threshold']
        topics_to_validate = []
        
        topic_scores = {
            'Agentic Artificial Intelligence': paper.agentic_ai_score,
            'Proximal Policy Optimization': paper.proximal_policy_optimization_score,
            'Reinforcement Learning': paper.reinforcement_learning_score,
            'Reasoning Models': paper.reasoning_models_score,
            'Inference Time Scaling': paper.inference_time_scaling_score
        }
        
        for topic, score in topic_scores.items():
            if score is not None and score >= threshold:
                topics_to_validate.append(topic)
        
        return topics_to_validate
    
    def _build_validation_prompt(self, paper: Paper, topics_to_validate: List[str]) -> str:
        """
        Build the validation prompt for the LLM.
        
        Args:
            paper: Paper object to validate
            topics_to_validate: List of topic names to validate
            
        Returns:
            Formatted prompt string
        """
        # Build paper information section
        title = paper.title or "No title available"
        abstract = paper.abstract or "No abstract available"
        
        paper_info = f"Title: {title}\nAbstract: {abstract}"
        
        # Add introduction if available
        if paper.introduction_text:
            paper_info += f"\nIntroduction: {paper.introduction_text}"
        
        topics_section = "Topics to evaluate:\n"
        for topic in topics_to_validate:
            topics_section += f"- {topic}: {self.topic_descriptions[topic]}\n"
        
        # Build the complete prompt
        prompt = f"""You are an expert AI researcher evaluating paper relevance to research topics.

Paper Information:
{paper_info}

{topics_section}
Step-by-step instructions:
1. Read the paper's text. Fully understand the paper's main contribution.
2. Evaluate if the paper's main contribution is relevant to any of the topics presented.
3. Respond ONLY in this exact XML format:

<validation_response>
    <topic name="{topics_to_validate[0]}">
        <conclusion>Highly Relevant|Moderately Relevant|Tangentially Relevant|Not Relevant</conclusion>
        <justification><![CDATA[Your detailed reasoning here]]></justification>
    </topic>
    [Include similar structure for each topic listed above]
</validation_response>

Important: Ensure you evaluate ALL {len(topics_to_validate)} topics listed and use only the four conclusion options provided. Keep justifications clear and concise. Wrap all justification text in CDATA tags."""
        
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
    
    def _parse_xml_response(self, response_content: str, expected_topics: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Parse XML response from LLM.
        
        Args:
            response_content: Raw response content from LLM
            expected_topics: List of topics that should be in the response
            
        Returns:
            Dictionary mapping topic names to their results
            
        Raises:
            Exception: If parsing fails or response is invalid
        """
        try:
            # Parse XML
            root = ET.fromstring(response_content)
            
            if root.tag != 'validation_response':
                raise Exception(f"Invalid root tag: {root.tag}, expected 'validation_response'")
            
            results = {}
            valid_conclusions = {'Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant', 'Not Relevant'}
            
            # Extract results for each topic
            for topic_element in root.findall('topic'):
                topic_name = topic_element.get('name')
                
                if not topic_name:
                    raise Exception("Topic missing 'name' attribute")
                
                if topic_name not in expected_topics:
                    raise Exception(f"Unexpected topic in response: {topic_name}")
                
                # Extract conclusion
                conclusion_element = topic_element.find('conclusion')
                if conclusion_element is None or not conclusion_element.text:
                    raise Exception(f"Missing or empty conclusion for topic: {topic_name}")
                
                conclusion = conclusion_element.text.strip()
                if conclusion not in valid_conclusions:
                    raise Exception(f"Invalid conclusion '{conclusion}' for topic: {topic_name}")
                
                # Extract justification
                justification_element = topic_element.find('justification')
                if justification_element is None:
                    raise Exception(f"Missing justification for topic: {topic_name}")
                
                # Handle CDATA
                justification = justification_element.text or ""
                justification = justification.strip()
                
                if not justification:
                    raise Exception(f"Empty justification for topic: {topic_name}")
                
                results[topic_name] = {
                    'conclusion': conclusion,
                    'justification': justification
                }
            
            # Verify all expected topics are present
            missing_topics = set(expected_topics) - set(results.keys())
            if missing_topics:
                raise Exception(f"Missing topics in response: {', '.join(missing_topics)}")
            
            return results
            
        except ET.ParseError as e:
            raise Exception(f"XML parsing error: {str(e)}")
        except Exception as e:
            # Re-raise our custom exceptions
            if "Invalid root tag" in str(e) or "Topic missing" in str(e) or "Missing" in str(e) or "Invalid conclusion" in str(e):
                raise
            else:
                raise Exception(f"Response parsing error: {str(e)}")
    
    def _update_paper_with_results(self, paper: Paper, validation_results: Dict[str, Dict[str, str]]) -> None:
        """
        Update paper object with validation results.
        
        Args:
            paper: Paper object to update
            validation_results: Dictionary of validation results by topic
        """
        for topic_name, result in validation_results.items():
            conclusion = result['conclusion']
            justification = result['justification']
            
            # Update relevance and justification based on topic
            if topic_name == 'Agentic Artificial Intelligence':
                paper.agentic_ai_relevance = conclusion
                paper.agentic_ai_justification = justification
            elif topic_name == 'Proximal Policy Optimization':
                paper.proximal_policy_optimization_relevance = conclusion
                paper.proximal_policy_optimization_justification = justification
            elif topic_name == 'Reinforcement Learning':
                paper.reinforcement_learning_relevance = conclusion
                paper.reinforcement_learning_justification = justification
            elif topic_name == 'Reasoning Models':
                paper.reasoning_models_relevance = conclusion
                paper.reasoning_models_justification = justification
            elif topic_name == 'Inference Time Scaling':
                paper.inference_time_scaling_relevance = conclusion
                paper.inference_time_scaling_justification = justification

def run(papers: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Run the LLM validation module on a batch of papers.
    
    This is the main entry point for the module, matching the common interface
    pattern used by other modules in the pipeline.
    
    Args:
        papers: Dictionary of paper_id -> Paper objects
        config: Configuration dictionary with LLM validation parameters
        
    Returns:
        The updated papers dictionary
    """
    processor = LLMValidation(config)
    return processor.run(papers)
