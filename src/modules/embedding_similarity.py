"""
Embedding Similarity Module

This module calculates similarity scores between papers and predefined research topics
using embeddings. It supports batch processing for efficiency and caches results
to reduce API costs.
"""

import logging
import json
import os
import time
import numpy as np
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from paper import Paper

# Configure OpenAI client
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger('EMBEDDING_SIMILARITY')

class EmbeddingSimilarity:
    """
    Handles similarity calculation between papers and research topics using embeddings.
    
    This class takes paper objects, generates embeddings for their content,
    and calculates similarity scores against predefined research topics.
    """
    
    def __init__(self, config: dict):
        """Initialize with configuration settings."""
        self.config = config
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Define research topics with concise descriptions
        self.topics = {
            'rlhf': "Reinforcement Learning from Human Feedback for aligning AI systems with human preferences.",
            'weak_supervision': "Machine learning approaches that use weak or noisy labels instead of clean labeled data.",
            'diffusion_reasoning': "AI models that use diffusion processes for reasoning and problem-solving tasks.",
            'distributed_training': "Training machine learning models across multiple machines or devices in parallel."
        }
    
    def run(self, papers: Dict[str, Paper]) -> Dict[str, Paper]:
        """
        Run embedding similarity calculation on a batch of papers.
        
        Args:
            papers: Dictionary of paper_id -> Paper objects
            
        Returns:
            The updated papers dictionary with similarity scores
        """
        logger.info(f"Starting embedding similarity calculation for {len(papers)} papers")
        
        # Step 1: Load or compute topic embeddings
        topic_embeddings = self._ensure_topic_embeddings()
        
        # Step 2: Identify papers needing processing
        papers_to_process = [p for p in papers.values() if not p.is_embedding_completed()]
        skipped_papers = len(papers) - len(papers_to_process)
        
        if skipped_papers > 0:
            logger.info(f"Skipping {skipped_papers} papers with embedding_status='completed'")
        
        if not papers_to_process:
            logger.info("No papers require embedding processing")
            return papers
        
        logger.info(f"Processing {len(papers_to_process)} papers for embedding similarity")
        
        # Step 3: Process papers in batches
        for i, batch in enumerate(self._create_batches(papers_to_process, self.config['batch_size'])):
            batch_size = len(batch)
            logger.info(f"Processing batch {i+1} with {batch_size} papers")
            self._process_batch(batch, topic_embeddings)
        
        # Step 4: Log summary statistics
        completed_count = sum(1 for p in papers.values() if p.embedding_status == "completed")
        failed_count = sum(1 for p in papers.values() if p.embedding_status == "failed")
        
        logger.info(f"Embedding similarity complete: {completed_count}/{len(papers)} successful, {failed_count} failed, {skipped_papers} skipped")
        
        return papers
    
    def _ensure_topic_embeddings(self) -> Dict[str, List[float]]:
        """
        Load topic embeddings from database or compute if not found.
        
        Returns:
            Dictionary mapping topic names to embedding vectors
        """
        # Connect to the database
        conn = sqlite3.connect("cache.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create topic_embeddings table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_embeddings (
                topic_name TEXT PRIMARY KEY,
                description TEXT,
                embedding_vector TEXT,
                model TEXT,
                created_at TEXT
            )
        """)
        
        # Check if we have embeddings for all topics with the current model
        topic_embeddings = {}
        current_model = self.config['model']
        
        for topic_name in self.topics.keys():
            cursor.execute(
                "SELECT embedding_vector FROM topic_embeddings WHERE topic_name = ? AND model = ?",
                (topic_name, current_model)
            )
            result = cursor.fetchone()
            
            if result:
                # Topic embedding exists, load it
                embedding_vector = json.loads(result['embedding_vector'])
                topic_embeddings[topic_name] = embedding_vector
        
        # If any topics are missing embeddings, compute them
        missing_topics = set(self.topics.keys()) - set(topic_embeddings.keys())
        if missing_topics:
            logger.info(f"Computing embeddings for {len(missing_topics)} topics")
            
            for topic_name in missing_topics:
                description = self.topics[topic_name]
                
                try:
                    # Generate embedding for topic description
                    response = self.client.embeddings.create(
                        model=current_model,
                        input=description
                    )
                    embedding_vector = response.data[0].embedding
                    
                    # Store embedding in dictionary and database
                    topic_embeddings[topic_name] = embedding_vector
                    
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO topic_embeddings
                        (topic_name, description, embedding_vector, model, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            topic_name,
                            description,
                            json.dumps(embedding_vector),
                            current_model,
                            datetime.now().isoformat()
                        )
                    )
                    
                    logger.info(f"Generated and saved embedding for topic: {topic_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for topic {topic_name}: {e}")
                    # If we can't generate a topic embedding, we have a serious problem
                    raise RuntimeError(f"Failed to generate critical topic embedding: {e}")
            
            # Commit changes if we added any embeddings
            conn.commit()
        
        conn.close()
        logger.info(f"Loaded embeddings for {len(topic_embeddings)} topics")
        return topic_embeddings
    
    def _build_paper_text(self, paper: Paper) -> str:
        """
        Build a comprehensive text representation of a paper for embedding.
        
        Args:
            paper: The Paper object to process
            
        Returns:
            A formatted string containing the paper's title, authors, categories,
            abstract, and introduction
        """
        title = paper.title or ''
        abstract = paper.abstract or ''
        authors = ', '.join(paper.authors) if paper.authors else ''
        categories = ', '.join(paper.categories) if paper.categories else ''
        
        introduction = ""
        if paper.introduction_text:
            introduction = f" Introduction: {paper.introduction_text}"
        
        return f"Title: {title} Authors: {authors} Categories: {categories} Abstract: {abstract}{introduction}"
    
    def _create_batches(self, papers: List[Paper], batch_size: int) -> List[List[Paper]]:
        """
        Split papers into batches of specified size.
        
        Args:
            papers: List of papers to batch
            batch_size: Maximum size of each batch
            
        Returns:
            List of paper batches
        """
        return [papers[i:i + batch_size] for i in range(0, len(papers), batch_size)]
    
    def _process_batch(self, papers: List[Paper], topic_embeddings: Dict[str, List[float]]) -> None:
        """
        Process a batch of papers with a single API call.
        
        Args:
            papers: List of papers to process in this batch
            topic_embeddings: Dictionary of topic embeddings
        """
        # Prepare paper texts for batch embedding
        paper_texts = [self._build_paper_text(paper) for paper in papers]
        
        try:
            # Generate embeddings for the batch
            response = self.client.embeddings.create(
                model=self.config['model'],
                input=paper_texts
            )
            
            # Process each paper with its embedding
            for i, paper in enumerate(papers):
                try:
                    paper_embedding = response.data[i].embedding
                    
                    # Calculate similarity scores for each topic
                    scores = {
                        topic: self._cosine_similarity(paper_embedding, topic_vec)
                        for topic, topic_vec in topic_embeddings.items()
                    }
                    
                    # Store scores in paper object
                    paper.rlhf_score = scores.get('rlhf')
                    paper.weak_supervision_score = scores.get('weak_supervision')
                    paper.diffusion_reasoning_score = scores.get('diffusion_reasoning')
                    paper.distributed_training_score = scores.get('distributed_training')
                    
                    # Find highest scoring topic
                    highest_topic = max(scores, key=scores.get)
                    paper.highest_similarity_topic = highest_topic
                    
                    # Mark as completed
                    paper.update_embedding_status("completed")
                    
                    logger.debug(f"Processed paper {paper.id} - Highest topic: {highest_topic}")
                    
                except Exception as e:
                    paper.update_embedding_status("failed")
                    paper.add_error(f"Error calculating similarity scores: {str(e)}")
                    logger.error(f"Error processing paper {paper.id}: {e}")
            
        except Exception as e:
            # Check for token limit errors
            if "token" in str(e).lower():
                error_message = "embedding_token_limit_exceeded"
            else:
                error_message = f"Embedding generation failed: {str(e)}"
            
            # Mark all papers in batch as failed
            for paper in papers:
                paper.update_embedding_status("failed")
                paper.add_error(error_message)
            
            logger.error(f"Batch processing failed: {e}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1, vec2: The vectors to compare
            
        Returns:
            Cosine similarity score (range -1 to 1)
        """
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        
        dot_product = np.dot(vec1_array, vec2_array)
        norm_product = np.linalg.norm(vec1_array) * np.linalg.norm(vec2_array)
        
        return dot_product / norm_product

def run(papers: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Run the embedding similarity module on a batch of papers.
    
    This is the main entry point for the module, matching the common interface
    pattern used by other modules in the pipeline.
    
    Args:
        papers: Dictionary of paper_id -> Paper objects
        config: Configuration dictionary with embedding parameters
        
    Returns:
        The updated papers dictionary
    """
    processor = EmbeddingSimilarity(config)
    return processor.run(papers)
