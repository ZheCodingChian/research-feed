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
from openai import OpenAI

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
            'Agentic Artificial Intelligence': """Agentic AI systems are autonomous agents that operate proactively to achieve complex, multi-step goals with minimal human supervision. Unlike reactive models that simply respond to prompts, agentic systems exhibit goal-driven autonomy by perceiving their environment, decomposing high-level objectives into a sequence of executable sub-tasks, and taking independent action. The core of an agentic architecture is a continuous operational loop involving planning, tool use, and memory. A planning module breaks down goals, a tool-use module allows interaction with external environments via APIs or functions, and a memory system (both short-term and long-term) provides context and enables learning from past actions. This framework is often powered by a large language model acting as a reasoning engine, enabling the agent to reflect, self-correct, and adapt its strategy based on outcomes and feedback. The defining characteristic is the ability to complete a mission, not just a single task.

Keywords: Agentic AI, AI agents, autonomous agents, goal-driven autonomy, task decomposition, hierarchical planning, strategic planning, ReAct framework, Reasoning and Acting, tool use, function calling, API execution, memory module, long-term memory, short-term memory, self-correction, reflection, multi-agent systems, CrewAI, AutoGPT, BabyAGI, proactive systems, autonomous execution.""",
            
            'Proximal Policy Optimization': """Proximal Policy Optimization (PPO) is a family of policy gradient methods for reinforcement learning that optimizes an agent's policy while ensuring that the updates are not too large, which promotes stable and reliable training. Developed by OpenAI, PPO has become a default algorithm for many deep reinforcement learning tasks due to its sample efficiency, ease of implementation, and robust performance. The core innovation of PPO is its use of a clipped surrogate objective function. This mechanism discourages the new policy from deviating too far from the old policy by clipping the probability ratio of actions, effectively creating a trust region without the complexity of its predecessor, TRPO. The algorithm alternates between collecting a batch of experience by interacting with the environment (on-policy) and performing several epochs of stochastic gradient ascent to optimize the surrogate objective. It is typically implemented within an actor-critic framework, where the actor network learns the policy and the critic network estimates the value function, often using Generalized Advantage Estimation (GAE) to reduce variance in the advantage estimates.

Keywords: Proximal Policy Optimization, PPO, policy gradient, reinforcement learning, actor-critic, on-policy, surrogate objective, clipped objective function, probability ratio, trust region, Trust Region Policy Optimization, TRPO, Generalized Advantage Estimation, GAE, advantage function, value function, sample efficiency, policy update, entropy bonus, deep reinforcement learning.""",
            
            'Reinforcement Learning': """Reinforcement Learning (RL) is a computational approach to goal-directed learning from interaction, formalized by the Markov Decision Process (MDP) framework. It addresses the problem of how an agent situated in an environment learns to map states to actions to maximize a numerical reward signal. The agent's goal is not to maximize immediate reward, but the expected cumulative reward, often expressed as a discounted sum of future rewards, known as the return. The core task is to find an optimal policy (π), which is a mapping from states to a probability distribution over actions. This is typically achieved by learning a value function, such as the state-value function V(s) or the action-value function Q(s, a), which quantifies the expected return. These value functions adhere to the Bellman equations, which provide a recursive definition that forms the basis for many RL algorithms. Key challenges include the credit assignment problem (determining which actions led to a given reward) and managing the exploration-exploitation trade-off.

Keywords: Reinforcement Learning, RL, Markov Decision Process, MDP, agent-environment interaction, reward signal, cumulative reward, return, policy optimization, value function, action-value function, state-value function, Q-function, Bellman equation, Bellman optimality equation, credit assignment problem, exploration-exploitation trade-off, temporal-difference learning, TD learning, dynamic programming, policy iteration, value iteration, on-policy, off-policy, model-free, model-based, state space, action space.""",
            
            'Reasoning Models': """A reasoning model is a machine learning model, typically a large language model (LLM), that has been specifically engineered or fine-tuned to perform explicit, multi-step problem decomposition before producing a final output. Unlike standard generative models that operate in a single autoregressive pass, a reasoning model is trained to first generate a reasoning trace or chain of thought (CoT). This trace externalizes the model's "thinking process" by breaking a complex query into a sequence of simpler, logical sub-problems. The architecture often consists of a knowledge base and an inference engine that applies logical methods like deduction or induction to this knowledge. The defining characteristic is the model's ability to maintain state and systematically work through a problem, often leveraging inference-time compute to evaluate different reasoning paths or self-correct based on intermediate results. This deliberative process, which moves from reactive "thinking fast" to proactive "thinking slow," allows these models to achieve higher accuracy on logic-driven tasks such as mathematics, coding, and complex planning.

Keywords: Reasoning model, large reasoning model, LRM, chain of thought, CoT, reasoning trace, step-by-step thinking, problem decomposition, multi-step reasoning, inference engine, knowledge base, logical inference, deductive reasoning, inductive reasoning, abductive reasoning, deliberative process, inference-time scaling, self-correction.""",
            
            'Inference Time Scaling': """Inference-time scaling is a computational strategy that decouples a model's performance from its fixed, pre-trained parameters by investing a variable computational budget at the point of inference. It fundamentally operates by transforming a single-pass autoregressive generation into a deliberative search or optimization problem. The core mechanism involves using the base model as a generator within a larger algorithmic scaffold. This scaffold executes processes that are impossible in a standard forward pass, such as multi-path exploration of reasoning traces (e.g., self-consistency), explicit verification of intermediate steps against a learned reward model or external constraints, and iterative refinement through self-critique or structured feedback loops. These methods often leverage search algorithms like Monte Carlo Tree Search (MCTS) or genetic algorithms to navigate the solution space. The defining characteristic is the trade-off between latency and accuracy through a structured, multi-step process where additional compute is not just used for longer generation, but for explicit evaluation, selection, and correction of generated outputs before a final answer is produced.

Keywords: Inference-time scaling, test-time compute, inference-time search, computational budget, deliberative search, multi-path exploration, self-consistency, best-of-n, verifier, reward model, iterative refinement, self-critique, backtracking, Monte Carlo Tree Search, MCTS, solution space navigation, autoregressive generation, sequential decision making, reasoning traces."""
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
        conn = sqlite3.connect("/data/cache.sqlite")
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
                    paper.agentic_ai_score = scores.get('Agentic Artificial Intelligence')
                    paper.proximal_policy_optimization_score = scores.get('Proximal Policy Optimization')
                    paper.reinforcement_learning_score = scores.get('Reinforcement Learning')
                    paper.reasoning_models_score = scores.get('Reasoning Models')
                    paper.inference_time_scaling_score = scores.get('Inference Time Scaling')
                    
                    # Mark as completed
                    paper.update_embedding_status("completed")
                    
                    logger.debug(f"Processed paper {paper.id} - Embedding scores calculated")
                    
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
                paper.agentic_ai_score = self._round_to_3_sig_figs(paper.agentic_ai_score)
                paper.proximal_policy_optimization_score = self._round_to_3_sig_figs(paper.proximal_policy_optimization_score)
                paper.reinforcement_learning_score = self._round_to_3_sig_figs(paper.reinforcement_learning_score)
                paper.reasoning_models_score = self._round_to_3_sig_figs(paper.reasoning_models_score)
                paper.inference_time_scaling_score = self._round_to_3_sig_figs(paper.inference_time_scaling_score)

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
