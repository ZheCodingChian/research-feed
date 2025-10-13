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
            'Agentic Artificial Intelligence': """Title: Agentic AI

Summary: Agentic AI papers study autonomous systems where AI agents powered by large language models or other architectures can perceive goals, decompose complex tasks into subtasks, use external tools and APIs, make decisions, and execute multi-step workflows with minimal human intervention, featuring architectures with orchestration layers planning modules tool-use capabilities and reflection mechanisms, evaluated on real-world automation benchmarks across domains including customer service software development data analysis supply chain management and business process automation.

Definition: Agentic AI research addresses the design implementation and evaluation of autonomous agent systems that can interpret high-level objectives, perform dynamic planning and reasoning, interact with external environments through tool calling API access code execution and web search, orchestrate workflows across multiple specialized agents, and iteratively refine outputs through self-critique and feedback loops, moving beyond single-shot LLM responses toward persistent goal-directed behavior that handles open-ended tasks requiring adaptation coordination and multi-step problem-solving without explicit step-by-step human guidance.

Positive Signals: Paper discusses autonomous agents with goal-directed behavior and task decomposition into subtasks; describes architectures with orchestrator agents manager agents worker agents or hierarchical multi-agent coordination; implements tool use including function calling API integration code interpreters web search database queries or robotic process automation; features planning modules that break down complex objectives into action sequences; includes reflection loops self-critique verifier agents or iterative refinement mechanisms; evaluates on workflow automation benchmarks measuring task completion accuracy multi-step reasoning success tool selection precision or end-to-end business process metrics; discusses prompt engineering for agentic behavior agent communication protocols state management memory systems or failure recovery strategies; addresses challenges like error propagation tool selection ambiguity hallucination mitigation or alignment in autonomous systems.

Exclusions: Single-prompt LLM responses without task decomposition or tool use; chatbots or conversational AI without autonomous workflow execution; reinforcement learning agents in simulated environments without tool integration or real-world task automation focus; supervised learning classification or prediction models without agentic decision-making loops; retrieval-augmented generation without autonomous planning or multi-step orchestration.

Keywords: agentic AI; agentic workflows; autonomous agents; AI agents; agent systems; multi-agent systems; orchestration; task decomposition; planning; hierarchical agents; manager agent; worker agent; orchestrator; tool use; function calling; tool calling; API integration; code execution; code interpreter; web search; database access; external tools; retrieval; action space; goal-directed; persistent behavior; multi-step reasoning; workflow automation; business process automation; agent architecture; agent frameworks; LangChain; AutoGPT; BabyAGI; agent loop; perception-action loop; reflection; self-critique; self-correction; verifier; critic agent; feedback loop; iterative refinement; prompt engineering; prompt chaining; agent communication; inter-agent communication; message passing; coordination; collaboration; delegation; specialization; memory systems; long-term memory; short-term memory; context management; state tracking; error handling; failure recovery; robustness; reliability; hallucination mitigation; grounding; factuality; alignment; safety; controllability; transparency; explainability; human oversight; human-in-the-loop; approval gates; guardrails; constraints; benchmarking; task success rate; workflow completion; end-to-end evaluation; simulation; real-world deployment; customer service automation; software engineering agents; coding agents; data analysis agents; research assistants; personal assistants; supply chain agents; financial agents; healthcare agents; legal agents; enterprise automation; agentic reasoning; chain of thought; tree of thoughts; ReAct; plan-and-execute; observe-plan-act; agent protocols; OpenAI Assistants API; Anthropic Claude agents; agent SDKs; agent platforms; distributed agents; cloud agents; edge agents; embodied agents; robotic agents with LLMs.""",
            
            'Proximal Policy Optimization': """Title: Proximal Policy Optimization (PPO)

Summary: Proximal Policy Optimization papers study a policy gradient reinforcement learning algorithm that achieves stable reliable policy updates through a clipped surrogate objective function preventing large destructive parameter changes, using actor-critic architecture with advantage estimation and multiple epochs of minibatch updates on collected trajectories, evaluated on continuous control tasks robotic manipulation Atari games and increasingly for fine-tuning large language models with reinforcement learning from human feedback, demonstrating sample efficiency training stability and strong empirical performance across diverse domains.

Definition: PPO research addresses policy optimization in reinforcement learning by constraining policy updates to trust regions through probability ratio clipping rather than explicit KL divergence penalties, optimizing a clipped objective that takes the minimum between the standard policy gradient objective and a clipped version bounded by epsilon hyperparameter typically 0.1 to 0.3, enabling on-policy learning with multiple gradient steps per batch of experience while maintaining monotonic improvement guarantees and avoiding catastrophic policy collapse, combining simplicity of implementation with robustness across hyperparameters and task domains making it a default choice for both continuous and discrete action spaces.

Positive Signals: Paper explicitly mentions Proximal Policy Optimization or PPO algorithm; describes clipped surrogate objective with probability ratio between new and old policies; implements epsilon clipping mechanism to constrain policy updates; uses actor-critic architecture with separate policy network and value function network; discusses advantage estimation techniques like generalized advantage estimation GAE; performs multiple epochs of optimization on fixed batches of trajectories; compares against TRPO A2C A3C or other policy gradient baselines; evaluates on standard RL benchmarks like MuJoCo continuous control OpenAI Gym Atari games or robotic tasks; reports metrics including episode return sample efficiency wall-clock time training stability or convergence speed; addresses hyperparameter sensitivity including clipping range learning rate batch size or number of epochs; applies PPO to language model fine-tuning with RLHF or instruction following; discusses entropy regularization for exploration or variance reduction techniques.

Exclusions: General reinforcement learning without specific PPO algorithm implementation; policy gradient methods using vanilla REINFORCE without clipping mechanism; trust region methods using explicit KL constraints like TRPO without clipping; value-based methods like Q-learning DQN without policy optimization; actor-critic methods that are not PPO variants like SAC TD3 DDPG; supervised learning or imitation learning without RL policy optimization.

Keywords: proximal policy optimization; PPO; policy gradient; clipped objective; clipped surrogate objective; probability ratio; ratio clipping; epsilon clipping; trust region; on-policy; actor-critic; policy network; value network; advantage; advantage estimation; generalized advantage estimation; GAE; lambda return; TD lambda; surrogate loss; policy loss; value loss; multiple epochs; minibatch; trajectory; rollout; horizon; discount factor; gamma; learning rate; clip range; epsilon; entropy bonus; entropy regularization; exploration; KL divergence; KL penalty; TRPO comparison; trust region policy optimization; A2C; A3C; asynchronous advantage actor-critic; sample efficiency; training stability; monotonic improvement; policy collapse; catastrophic forgetting; continuous control; discrete control; MuJoCo; OpenAI Gym; Atari; robotics; manipulation; locomotion; reward shaping; normalization; observation normalization; reward normalization; advantage normalization; policy update; gradient clipping; orthogonal initialization; hyperparameter tuning; ablation study; RLHF; reinforcement learning from human feedback; instruction tuning; language model alignment; reward model; preference learning; OpenAI; Anthropic; InstructGPT; ChatGPT training; fine-tuning LLMs; human preferences; variance reduction; baseline; critic; bootstrapping; temporal difference; episode return; cumulative reward; wall-clock time; convergence; asymptotic performance; sample complexity; PPO1; PPO2; PPOClip; PPOPenalty; distributed PPO; parallel actors; vectorized environments; GPU acceleration.""",
            
            'Reinforcement Learning': """Title: Reinforcement Learning 

Summary: Reinforcement Learning papers study how autonomous agents learn optimal sequential decision-making policies through trial-and-error interaction with an environment to maximize cumulative reward, formalized as Markov Decision Processes with states actions transitions and rewards, using value-based methods like Q-learning DQN, policy gradient methods like REINFORCE PPO TRPO, or actor-critic architectures, with evaluation on interactive control tasks via episode returns sample efficiency and learning curves in domains including robotics games autonomous systems and recommendation engines.

Definition: Reinforcement Learning research addresses sequential decision-making under uncertainty where an agent learns a policy mapping states to actions by receiving reward signals from environment interactions without supervision, optimizing expected cumulative discounted return over horizons through algorithms that estimate value functions Q-functions or directly optimize policies, handling exploration-exploitation tradeoffs, credit assignment problems, and sample efficiency challenges in both model-free and model-based settings with applications requiring adaptive control planning and autonomous behavior.

Positive Signals: Paper discusses agent-environment interaction loops with reward feedback and return maximization; formalizes problem as MDP or POMDP with state spaces action spaces transition dynamics and reward functions; proposes or evaluates algorithms from value-based families like Q-learning SARSA DQN or policy gradient families like REINFORCE A2C A3C PPO TRPO or actor-critic methods; addresses exploration versus exploitation via epsilon-greedy UCB Thompson sampling or intrinsic motivation; compares on-policy versus off-policy learning or model-free versus model-based approaches; evaluates using episode returns learning curves sample complexity rollouts or convergence metrics on interactive benchmarks like Atari MuJoCo robotics simulators or multi-agent environments; discusses temporal-difference learning Bellman equations discount factors replay buffers target networks advantage estimation or trust regions.

Exclusions: Purely supervised learning on labeled datasets with no agent interaction or reward signals; unsupervised learning clustering or dimensionality reduction without sequential decision-making; optimization focused only on loss minimization accuracy or precision without policies values or returns; control theory papers without MDP framing reward-driven learning or policy optimization; planning without learning from interaction feedback.

Keywords: reinforcement learning; RL; agent; environment; state; action; reward; return; policy; value function; Q-function; Q-learning; deep Q-network; DQN; SARSA; Bellman equation; temporal-difference; TD learning; Monte Carlo; policy gradient; REINFORCE; actor-critic; advantage; A2C; A3C; PPO; proximal policy optimization; TRPO; trust region; entropy regularization; exploration; exploitation; epsilon-greedy; UCB; Thompson sampling; intrinsic motivation; curiosity; model-free; model-based; world model; planning; Dyna; model predictive control; MPC; Markov decision process; MDP; POMDP; transition dynamics; discount factor; gamma; learning rate; alpha; on-policy; off-policy; experience replay; replay buffer; target network; double DQN; dueling network; prioritized replay; stability; sample efficiency; data efficiency; reward shaping; reward engineering; credit assignment; sparse rewards; delayed rewards; curriculum learning; multi-task RL; transfer learning; meta-RL; benchmarking; Atari; MuJoCo; OpenAI Gym; episode; episodic; rollout; trajectory; horizon; time step; stochastic policy; deterministic policy; continuous control; discrete control; continuous action space; discrete action space; policy evaluation; policy improvement; policy iteration; value iteration; baseline; variance reduction; generalized advantage estimation; GAE; bootstrapping; bias-variance tradeoff; convergence; asymptotic performance; generalization; overfitting; safety; safe RL; constrained RL; risk-sensitive; multi-agent; MARL; cooperative; competitive; Nash equilibrium; self-play; communication; coordination; opponent modeling; exploration bonus; count-based exploration; novelty; intrinsic reward; extrinsic reward; regret; cumulative regret; bandits; contextual bandits; offline RL; batch RL; imitation learning; inverse RL; reward learning; human feedback; RLHF; sim-to-real; domain randomization; robustness.""",
            
            'Reasoning Models': """Title: Reasoning Models

Summary: Reasoning models papers study AI systems particularly large language models designed to perform complex multi-step logical deduction mathematical problem-solving planning and structured thinking that mimics human cognitive processes, using techniques like chain-of-thought prompting tree-of-thoughts exploration self-verification iterative reasoning and explicit step-by-step decomposition, evaluated on benchmarks requiring mathematical reasoning logical inference commonsense reasoning symbolic manipulation theorem proving code generation and multi-hop question answering, demonstrating improvements in accuracy interpretability and reliability over standard prompt-response paradigms.

Definition: Reasoning models research addresses enhancing AI systems with systematic thinking capabilities beyond pattern matching by generating explicit reasoning traces that break complex problems into intermediate steps verify logical consistency explore alternative solution paths and self-correct errors, leveraging architectural innovations like reasoning tokens scratchpad mechanisms separate planning and execution modules and training techniques including process supervision reward shaping for reasoning steps reinforcement learning on reasoning trajectories and contrastive learning between correct and incorrect reasoning chains, aiming to achieve robust generalizable problem-solving that transfers across domains produces interpretable justifications and exhibits compositionality in handling novel task combinations.

Positive Signals: Paper discusses models that perform explicit multi-step reasoning or chain-of-thought generation; implements techniques for breaking problems into logical steps intermediate calculations or sub-goals; uses prompting strategies like chain-of-thought few-shot exemplars tree-of-thoughts least-to-most decomposition or scratchpad notation; performs self-verification self-consistency checks or critique-and-revise loops; explores multiple reasoning paths solution candidates or search over proof trees; trains models with process supervision step-level rewards or intermediate annotations rather than only outcome supervision; evaluates on reasoning benchmarks including mathematical problem-solving MATH GSM8K SVAMP logical reasoning datasets commonsense reasoning CSQA StrategyQA multi-hop QA HotpotQA symbolic reasoning ARC theorem proving code generation with reasoning or planning tasks; reports metrics like step-by-step accuracy reasoning trace quality interpretability human evaluation of logic or error analysis of reasoning failures; addresses compositionality systematic generalization length generalization or out-of-distribution reasoning; discusses reasoning capabilities emergent from scale versus explicit training or architectural modifications for reasoning.

Exclusions: Standard language models without explicit reasoning mechanisms or evaluation on reasoning tasks; question answering systems using retrieval or pattern matching without multi-step inference; code generation without reasoning traces or planning steps; simple classification or prediction without intermediate logical steps; dialogue systems focused on conversation rather than problem-solving reasoning; models evaluated only on perplexity or next-token prediction without reasoning benchmarks.

Keywords: reasoning models; general reasoning; logical reasoning; multi-step reasoning; step-by-step reasoning; chain-of-thought; CoT; chain of thought prompting; few-shot CoT; zero-shot CoT; tree of thoughts; ToT; self-consistency; self-verification; self-critique; self-correction; least-to-most prompting; decomposition; sub-goals; intermediate steps; reasoning trace; reasoning path; scratchpad; working memory; think step by step; explicit reasoning; systematic reasoning; deductive reasoning; inductive reasoning; abductive reasoning; analogical reasoning; commonsense reasoning; mathematical reasoning; symbolic reasoning; logical inference; problem-solving; planning; proof generation; theorem proving; mathematical problem-solving; MATH dataset; GSM8K; SVAMP; MAWPS; commonsense QA; CSQA; StrategyQA; multi-hop reasoning; HotpotQA; 2WikiMultihopQA; logical reasoning datasets; ARC; CLUTRR; bAbI; symbolic manipulation; compositional generalization; systematic generalization; length generalization; out-of-distribution reasoning; interpretability; explainability; faithful reasoning; reasoning transparency; process supervision; outcome supervision; step-level rewards; intermediate rewards; reasoning annotations; contrastive learning; positive and negative reasoning examples; search over reasoning; beam search reasoning; best-of-n reasoning; verifier models; reasoning quality; error analysis; failure modes; reasoning errors; hallucination in reasoning; reasoning consistency; reasoning robustness; emergent reasoning; scaling and reasoning; LLM reasoning; transformer reasoning; reasoning architectures; reasoning modules; System 1 versus System 2; fast and slow thinking; deliberative reasoning; cognitive models; human-like reasoning; GPT reasoning; ChatGPT reasoning; Claude reasoning; reasoning-enhanced models; instruction tuning for reasoning; RLHF for reasoning; fine-tuning on reasoning tasks.""",
            
            'Inference Time Scaling': """Title: Inference Time Scaling

Summary: Inference time scaling papers study techniques that allocate additional computational resources during model inference or test time after training is complete to improve prediction accuracy and reliability, including methods like generating multiple candidate solutions with verifier-based selection, iterative refinement through self-correction loops, step-by-step reasoning with extended chain-of-thought, beam search over reasoning paths, Monte Carlo tree search for planning, and adaptive compute allocation based on problem difficulty, demonstrating accuracy-compute tradeoffs where increased inference budget yields better performance on complex reasoning mathematical problem-solving coding tasks and decision-making benchmarks.

Definition: Inference time scaling research addresses post-training optimization strategies that leverage additional computation during the prediction phase to enhance model outputs beyond what fixed forward passes provide, moving from single-shot generation to deliberative processes including sampling multiple responses and selecting via learned verifiers or self-consistency voting, performing explicit search over solution spaces or reasoning trajectories, applying iterative refinement where models critique and revise their own outputs, scaling compute adaptively based on uncertainty or task complexity, and trading latency for quality in applications where correctness is more valuable than speed, fundamentally exploring how test-time computation can substitute for or complement pre-training and fine-tuning scale.

Positive Signals: Paper discusses allocating more compute at inference or test time to improve accuracy; implements verifier models or reward models to score and select among multiple generated candidates; uses self-consistency majority voting or ensemble methods over sampled outputs; performs iterative refinement self-correction or critique-revise loops during generation; applies beam search Monte Carlo tree search or other search algorithms over reasoning steps or solution paths; extends chain-of-thought reasoning with more steps longer traces or tree-of-thoughts exploration; measures accuracy versus computational budget tradeoffs showing performance scaling with inference compute; implements adaptive compute mechanisms that allocate more resources to harder problems; evaluates on reasoning benchmarks like mathematical problem-solving MATH GSM8K coding tasks HumanEval APPS or logical inference datasets; reports metrics including pass-at-k solve rate accuracy at different compute budgets wall-clock inference time or FLOPs; discusses prompt-time techniques like generate-then-verify best-of-n sampling or process supervision; addresses deployment considerations balancing latency cost and accuracy in production systems.

Exclusions: Training time scaling or pre-training compute without test-time focus; standard inference without additional computation beyond single forward pass; model ensembles created during training rather than inference-time generation; simple temperature sampling without selection verification or refinement mechanisms; retrieval-augmented generation without explicit reasoning search or iterative improvement; distillation or compression techniques that reduce rather than increase inference compute.

Keywords: inference time scaling; test-time compute; inference compute; test-time scaling; compute at inference; runtime computation; deliberation; extended reasoning; verifier; reward model; outcome supervision; process supervision; best-of-n sampling; generate and verify; candidate generation; multiple candidates; selection; voting; self-consistency; majority voting; ensemble; sampling; temperature; top-p; nucleus sampling; beam search; search algorithms; Monte Carlo tree search; MCTS; tree search; planning; iterative refinement; self-correction; critique; revise; refinement loop; chain-of-thought; CoT; extended CoT; step-by-step reasoning; multi-step reasoning; tree of thoughts; reasoning paths; solution space; exploration; backtracking; accuracy-compute tradeoff; scaling laws; inference scaling laws; compute budget; computational budget; FLOPs; latency; throughput; cost; adaptive compute; dynamic compute; early stopping; uncertainty estimation; difficulty estimation; problem complexity; reasoning benchmarks; mathematical reasoning; MATH dataset; GSM8K; coding; HumanEval; APPS; MBPP; logical reasoning; common sense reasoning; pass-at-k; solve rate; success rate; accuracy scaling; diminishing returns; anytime algorithms; progressive inference; speculative decoding; parallel sampling; batch inference; model-based search; value-guided search; learned heuristics; AlphaCode; AlphaGeometry; process reward models; outcome reward models; verification; correctness checking; test-time training; test-time adaptation; meta-learning at inference; prompt engineering; few-shot prompting; scratchpad; working memory; intermediate steps; trace; rollout."""
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
