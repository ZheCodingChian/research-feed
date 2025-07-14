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
        
        # Define research topics with detailed descriptions
        self.topics = {
            'Reinforcement Learning from Human Feedback': """RLHF (Reinforcement Learning from Human Feedback)
This field focuses on aligning AI systems, particularly large language and vision models, with human values and intentions. The core idea is to use human feedback to guide the model's learning process, moving beyond standard supervised fine-tuning. This includes techniques for collecting and modeling human preferences, often through pairwise comparisons or ratings, to learn a reward model. This reward model is then used to fine-tune the base model using reinforcement learning algorithms like Proximal Policy Optimization (PPO). Key areas include the development of high-quality preference datasets, methods to improve the sample efficiency of feedback, and alternative approaches that bypass an explicit reward model, such as Direct Preference Optimization (DPO). The ultimate goal is to create models that are more helpful, harmless, and honest by steering their behavior toward desired outcomes defined by human judges. This also encompasses related concepts like Constitutional AI, AI safety, value alignment, and mitigating reward hacking.

Keywords: Reinforcement Learning from Human Feedback, RLHF, Direct Preference Optimization, DPO, Proximal Policy Optimization, PPO, reward model, preference learning, human preferences, pairwise comparison, preference dataset, instruction tuning, AI alignment, AI safety, Constitutional AI, human-in-the-loop, value alignment, helpfulness, harmlessness, honesty.""",
            
            'Weak Supervision': """Weak Supervision
This area of machine learning addresses the challenge of creating large labeled datasets by using lower-quality, noisy, or imprecise sources of supervision instead of relying on manually annotated data. The central theme is leveraging imperfect information to train high-performing models. This includes methods like distant supervision, where knowledge bases are used to automatically label text, and data programming, where users provide a set of heuristic rules or "labeling functions" that are combined via a generative model to produce probabilistic labels. Frameworks like Snorkel are central to this paradigm. The research explores techniques for handling label noise, resolving conflicts between different weak sources, and programmatically creating and augmenting training data. The goal is to dramatically reduce the time and cost associated with data labeling while maintaining competitive model performance.

Keywords: Weak supervision, distant supervision, programmatic labeling, data programming, labeling functions, noisy labels, imperfect labels, heuristic rules, label model, generative label model, Snorkel, data augmentation, semi-supervised learning, unreliable labels, probabilistic labels.""",
            
            'Diffusion-based Reasoning': """Diffusion-based Reasoning Models
This emerging research direction explores the application of diffusion models, traditionally used for high-fidelity image and audio generation, to tasks requiring complex reasoning and structured thinking. Instead of simply generating pixels, these models are being adapted to produce structured outputs like text, code, or logical plans. A key focus is on emulating multi-step or chain-of-thought reasoning by conceptualizing the reasoning process as a denoising trajectory, generating intermediate steps to arrive at a final answer. This includes developing hybrid architectures that integrate diffusion mechanisms with transformers or other established reasoning modules. The research investigates how the iterative refinement process inherent in diffusion can be harnessed for logical inference, mathematical problem-solving, planning, and other cognitive tasks typically associated with large language models.

Keywords: Diffusion model, denoising diffusion probabilistic models, DDPM, score-based generation, chain-of-thought, step-by-step reasoning, structured prediction, logical reasoning, planning, latent diffusion, generative reasoning, diffusion for language, hybrid architectures, transformer-diffusion models, iterative refinement.""",
            
            'Distributed Training': """Distributed Training
This field focuses on the algorithms, systems, and infrastructure required to train massive machine learning models that cannot fit on a single accelerator (GPU/TPU). It involves techniques for parallelizing the training process across multiple devices, which can be located within a single server or distributed across a cluster of nodes. Core strategies include data parallelism, where the dataset is split across devices; model parallelism, where the model itself is partitioned (including tensor and pipeline parallelism); and ZeRO (Zero Redundancy Optimizer), which shards optimizer states, gradients, and parameters. Research in this area develops new parallelization strategies, communication-efficient algorithms to reduce network bottlenecks (e.g., gradient compression, collective communication libraries like NCCL), and robust systems for managing training at scale. This includes work on fault tolerance, checkpointing, and hardware-software co-design to optimize for specific network topologies and interconnects like NVLink and InfiniBand.

Keywords: Distributed training, large-scale training, model parallelism, data parallelism, pipeline parallelism, tensor parallelism, Zero Redundancy Optimizer, ZeRO, FSDP, DeepSpeed, Megatron-LM, multi-GPU, multi-node, gradient accumulation, collective communication, all-reduce, parameter server, gradient compression, HPC, High-Performance Computing."""
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
        
        # Step 4: Round similarity scores to 3 significant figures
        self._round_similarity_scores(papers)
        
        # Step 5: Log summary statistics
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
                    
                    # Store scores in paper object (mapping natural language topic names to existing fields)
                    paper.rlhf_score = scores.get('Reinforcement Learning from Human Feedback')
                    paper.weak_supervision_score = scores.get('Weak Supervision')
                    paper.diffusion_reasoning_score = scores.get('Diffusion-based Reasoning')
                    paper.distributed_training_score = scores.get('Distributed Training')
                    
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
    
    def _round_to_3_sig_figs(self, value: Optional[float]) -> Optional[float]:
        """
        Round a value to 3 significant figures.
        
        Args:
            value: The value to round, can be None
            
        Returns:
            Rounded value or None if input was None
        """
        if value is None:
            return None
        
        if value == 0:
            return 0.0
            
        import math
        # Calculate the number of digits before the decimal point
        magnitude = math.floor(math.log10(abs(value)))
        # Round to 3 significant figures
        factor = 10 ** (2 - magnitude)
        return round(value * factor) / factor
    
    def _round_similarity_scores(self, papers: Dict[str, Paper]) -> None:
        """
        Round all similarity scores in papers to 3 significant figures.
        
        Args:
            papers: Dictionary of paper objects to process
        """
        for paper in papers.values():
            # Only round papers that have embedding scores
            if paper.embedding_status == "completed":
                paper.rlhf_score = self._round_to_3_sig_figs(paper.rlhf_score)
                paper.weak_supervision_score = self._round_to_3_sig_figs(paper.weak_supervision_score)
                paper.diffusion_reasoning_score = self._round_to_3_sig_figs(paper.diffusion_reasoning_score)
                paper.distributed_training_score = self._round_to_3_sig_figs(paper.distributed_training_score)

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
