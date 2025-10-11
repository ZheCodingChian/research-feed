import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from paper import Paper, AuthorHIndex

logger = logging.getLogger('DATABASE')


class PaperDatabase:
    """
    Handles all database operations for caching Paper objects.
    
    This class provides a simple interface to store and retrieve Paper objects
    from SQLite, serving as the persistence layer for the pipeline.
    """
    
    def __init__(self, db_path: str = "database.sqlite"):
        """Initialize the database connection and create tables if needed."""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create the papers table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    authors TEXT,  -- JSON array
                    categories TEXT,  -- JSON array
                    abstract TEXT,
                    published_date TEXT,  -- ISO format
                    arxiv_url TEXT,  -- Main arXiv abstract page URL
                    pdf_url TEXT,    -- Direct PDF download URL
                    latex_url TEXT,   -- LaTeX source files URL
                    scraper_status TEXT,
                    intro_status TEXT DEFAULT 'not_extracted',
                    category_enhancement TEXT DEFAULT 'not_enhanced',
                    introduction_text TEXT,
                    intro_extraction_method TEXT,
                    tex_file_name TEXT,
                    embedding_status TEXT DEFAULT 'not_embedded',
                    agentic_ai_score REAL,
                    proximal_policy_optimization_score REAL,
                    reinforcement_learning_score REAL,
                    reasoning_models_score REAL,
                    inference_time_scaling_score REAL,
                    llm_validation_status TEXT DEFAULT 'not_validated',
                    agentic_ai_relevance TEXT DEFAULT 'not_validated',
                    proximal_policy_optimization_relevance TEXT DEFAULT 'not_validated',
                    reinforcement_learning_relevance TEXT DEFAULT 'not_validated',
                    reasoning_models_relevance TEXT DEFAULT 'not_validated',
                    inference_time_scaling_relevance TEXT DEFAULT 'not_validated',
                    agentic_ai_justification TEXT DEFAULT 'no_justification',
                    proximal_policy_optimization_justification TEXT DEFAULT 'no_justification',
                    reinforcement_learning_justification TEXT DEFAULT 'no_justification',
                    reasoning_models_justification TEXT DEFAULT 'no_justification',
                    inference_time_scaling_justification TEXT DEFAULT 'no_justification',
                    llm_score_status TEXT DEFAULT 'not_scored',
                    summary TEXT,
                    novelty_score TEXT,
                    novelty_justification TEXT,
                    impact_score TEXT,
                    impact_justification TEXT,
                    recommendation_score TEXT,
                    recommendation_justification TEXT,
                    h_index_status TEXT DEFAULT 'not_fetched',
                    semantic_scholar_url TEXT,
                    h_index_fetch_method TEXT,
                    total_authors INTEGER,
                    authors_found INTEGER,
                    highest_h_index INTEGER,
                    average_h_index REAL,
                    notable_authors_count INTEGER,
                    author_h_indexes TEXT,  -- JSON array of AuthorHIndex objects
                    errors TEXT,  -- JSON array
                    created_at TEXT,  -- ISO format
                    updated_at TEXT,  -- ISO format
                    last_generated TEXT  -- YYYY-MM-DD format for cache cleanup
                )
            """)
            
            # Create topic_embeddings table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS topic_embeddings (
                    topic_name TEXT PRIMARY KEY,
                    description TEXT,
                    embedding_vector TEXT,  -- JSON array of floats
                    model TEXT,
                    created_at TEXT
                )
            """)
    
    def save_paper(self, paper: Paper) -> None:
        """Save or update a paper in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO papers (
                    id, title, authors, categories, abstract, published_date,
                    arxiv_url, pdf_url, latex_url, scraper_status, intro_status, category_enhancement, introduction_text,
                    intro_extraction_method, tex_file_name, embedding_status, agentic_ai_score,
                    proximal_policy_optimization_score, reinforcement_learning_score, reasoning_models_score,
                    inference_time_scaling_score, llm_validation_status, agentic_ai_relevance,
                    proximal_policy_optimization_relevance, reinforcement_learning_relevance, reasoning_models_relevance,
                    inference_time_scaling_relevance, agentic_ai_justification, proximal_policy_optimization_justification, reinforcement_learning_justification,
                    reasoning_models_justification, inference_time_scaling_justification, llm_score_status, summary, novelty_score,
                    novelty_justification, impact_score, impact_justification, recommendation_score,
                    recommendation_justification, h_index_status, semantic_scholar_url, h_index_fetch_method,
                    total_authors, authors_found, highest_h_index, average_h_index, notable_authors_count,
                    author_h_indexes, errors, created_at, updated_at, last_generated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.id,
                paper.title,
                json.dumps(paper.authors),
                json.dumps(paper.categories),
                paper.abstract,
                paper.published_date.isoformat(),
                paper.arxiv_url,
                paper.pdf_url,
                paper.latex_url,
                paper.scraper_status,
                paper.intro_status,
                paper.category_enhancement,
                paper.introduction_text,
                paper.intro_extraction_method,
                paper.tex_file_name,
                paper.embedding_status,
                paper.agentic_ai_score,
                paper.proximal_policy_optimization_score,
                paper.reinforcement_learning_score,
                paper.reasoning_models_score,
                paper.inference_time_scaling_score,
                paper.llm_validation_status,
                paper.agentic_ai_relevance,
                paper.proximal_policy_optimization_relevance,
                paper.reinforcement_learning_relevance,
                paper.reasoning_models_relevance,
                paper.inference_time_scaling_relevance,
                paper.agentic_ai_justification,
                paper.proximal_policy_optimization_justification,
                paper.reinforcement_learning_justification,
                paper.reasoning_models_justification,
                paper.inference_time_scaling_justification,
                paper.llm_score_status,
                paper.summary,
                paper.novelty_score,
                paper.novelty_justification,
                paper.impact_score,
                paper.impact_justification,
                paper.recommendation_score,
                paper.recommendation_justification,
                paper.h_index_status,
                paper.semantic_scholar_url,
                paper.h_index_fetch_method,
                paper.total_authors,
                paper.authors_found,
                paper.highest_h_index,
                paper.average_h_index,
                paper.notable_authors_count,
                json.dumps([{
                    'name': auth.name,
                    'profile_url': auth.profile_url,
                    'h_index': auth.h_index
                } for auth in paper.author_h_indexes]),
                json.dumps(paper.errors),
                paper.created_at.isoformat(),
                paper.updated_at.isoformat(),
                paper.last_generated
            ))
    
    def load_paper(self, paper_id: str) -> Optional[Paper]:
        """Load a paper from the database by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return Paper(
                id=row['id'],
                title=row['title'],
                authors=json.loads(row['authors']),
                categories=json.loads(row['categories']),
                abstract=row['abstract'],
                published_date=datetime.fromisoformat(row['published_date']),
                arxiv_url=row['arxiv_url'],
                pdf_url=row['pdf_url'],
                latex_url=row['latex_url'],
                scraper_status=row['scraper_status'],
                intro_status=row['intro_status'],
                category_enhancement=row['category_enhancement'],
                introduction_text=row['introduction_text'],
                intro_extraction_method=row['intro_extraction_method'],
                tex_file_name=row['tex_file_name'],
                embedding_status=row['embedding_status'],
                agentic_ai_score=row['agentic_ai_score'],
                proximal_policy_optimization_score=row['proximal_policy_optimization_score'],
                reinforcement_learning_score=row['reinforcement_learning_score'],
                reasoning_models_score=row['reasoning_models_score'],
                inference_time_scaling_score=row['inference_time_scaling_score'],
                llm_validation_status=row['llm_validation_status'],
                agentic_ai_relevance=row['agentic_ai_relevance'],
                proximal_policy_optimization_relevance=row['proximal_policy_optimization_relevance'],
                reinforcement_learning_relevance=row['reinforcement_learning_relevance'],
                reasoning_models_relevance=row['reasoning_models_relevance'],
                inference_time_scaling_relevance=row['inference_time_scaling_relevance'],
                agentic_ai_justification=row['agentic_ai_justification'],
                proximal_policy_optimization_justification=row['proximal_policy_optimization_justification'],
                reinforcement_learning_justification=row['reinforcement_learning_justification'],
                reasoning_models_justification=row['reasoning_models_justification'],
                inference_time_scaling_justification=row['inference_time_scaling_justification'],
                llm_score_status=row['llm_score_status'],
                summary=row['summary'],
                novelty_score=row['novelty_score'],
                novelty_justification=row['novelty_justification'],
                impact_score=row['impact_score'],
                impact_justification=row['impact_justification'],
                recommendation_score=row['recommendation_score'],
                recommendation_justification=row['recommendation_justification'],
                h_index_status=row['h_index_status'],
                semantic_scholar_url=row['semantic_scholar_url'],
                h_index_fetch_method=row['h_index_fetch_method'],
                total_authors=row['total_authors'],
                authors_found=row['authors_found'],
                highest_h_index=row['highest_h_index'],
                average_h_index=row['average_h_index'],
                notable_authors_count=row['notable_authors_count'],
                author_h_indexes=[
                    AuthorHIndex(
                        name=auth['name'],
                        profile_url=auth['profile_url'],
                        h_index=auth['h_index']
                    ) for auth in json.loads(row['author_h_indexes'])
                ] if row['author_h_indexes'] else [],
                errors=json.loads(row['errors']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                last_generated=row['last_generated']
            )
    
    def save_papers(self, papers: Dict[str, Paper]) -> None:
        """Save multiple papers to the database efficiently."""
        logger.info(f"Saving {len(papers)} papers to database")
        
        with sqlite3.connect(self.db_path) as conn:
            for paper in papers.values():
                conn.execute("""
                    INSERT OR REPLACE INTO papers (
                        id, title, authors, categories, abstract, published_date,
                        arxiv_url, pdf_url, latex_url, scraper_status, intro_status, category_enhancement, introduction_text,
                        intro_extraction_method, tex_file_name, embedding_status, agentic_ai_score,
                        proximal_policy_optimization_score, reinforcement_learning_score, reasoning_models_score,
                        inference_time_scaling_score, llm_validation_status, agentic_ai_relevance,
                        proximal_policy_optimization_relevance, reinforcement_learning_relevance, reasoning_models_relevance,
                        inference_time_scaling_relevance, agentic_ai_justification, proximal_policy_optimization_justification, reinforcement_learning_justification,
                        reasoning_models_justification, inference_time_scaling_justification, llm_score_status, summary, novelty_score,
                        novelty_justification, impact_score, impact_justification, recommendation_score,
                        recommendation_justification, h_index_status, semantic_scholar_url, h_index_fetch_method,
                        total_authors, authors_found, highest_h_index, average_h_index, notable_authors_count,
                        author_h_indexes, errors, created_at, updated_at, last_generated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paper.id,
                    paper.title,
                    json.dumps(paper.authors),
                    json.dumps(paper.categories),
                    paper.abstract,
                    paper.published_date.isoformat(),
                    paper.arxiv_url,
                    paper.pdf_url,
                    paper.latex_url,
                    paper.scraper_status,
                    paper.intro_status,
                    paper.category_enhancement,
                    paper.introduction_text,
                    paper.intro_extraction_method,
                    paper.tex_file_name,
                    paper.embedding_status,
                    paper.agentic_ai_score,
                    paper.proximal_policy_optimization_score,
                    paper.reinforcement_learning_score,
                    paper.reasoning_models_score,
                    paper.inference_time_scaling_score,
                    paper.llm_validation_status,
                    paper.agentic_ai_relevance,
                    paper.proximal_policy_optimization_relevance,
                    paper.reinforcement_learning_relevance,
                    paper.reasoning_models_relevance,
                    paper.inference_time_scaling_relevance,
                    paper.agentic_ai_justification,
                    paper.proximal_policy_optimization_justification,
                    paper.reinforcement_learning_justification,
                    paper.reasoning_models_justification,
                    paper.inference_time_scaling_justification,
                    paper.llm_score_status,
                    paper.summary,
                    paper.novelty_score,
                    paper.novelty_justification,
                    paper.impact_score,
                    paper.impact_justification,
                    paper.recommendation_score,
                    paper.recommendation_justification,
                    paper.h_index_status,
                    paper.semantic_scholar_url,
                    paper.h_index_fetch_method,
                    paper.total_authors,
                    paper.authors_found,
                    paper.highest_h_index,
                    paper.average_h_index,
                    paper.notable_authors_count,
                    json.dumps([{
                        'name': auth.name,
                        'profile_url': auth.profile_url,
                        'h_index': auth.h_index
                    } for auth in paper.author_h_indexes]),
                    json.dumps(paper.errors),
                    paper.created_at.isoformat(),
                    paper.updated_at.isoformat(),
                    paper.last_generated
                ))
        
        logger.info(f"Successfully saved {len(papers)} papers to database")
    
    def load_papers(self, paper_ids: list[str]) -> Dict[str, Paper]:
        """Load multiple papers from the database."""
        papers = {}
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Use parameterized query with IN clause
            placeholders = ','.join('?' * len(paper_ids))
            cursor = conn.execute(
                f"SELECT * FROM papers WHERE id IN ({placeholders})",
                paper_ids
            )
            
            for row in cursor:
                paper = Paper(
                    id=row['id'],
                    title=row['title'],
                    authors=json.loads(row['authors']),
                    categories=json.loads(row['categories']),
                    abstract=row['abstract'],
                    published_date=datetime.fromisoformat(row['published_date']),
                    arxiv_url=row['arxiv_url'],
                    pdf_url=row['pdf_url'],
                    latex_url=row['latex_url'],
                    scraper_status=row['scraper_status'],
                    intro_status=row['intro_status'],
                    category_enhancement=row['category_enhancement'],
                    introduction_text=row['introduction_text'],
                    intro_extraction_method=row['intro_extraction_method'],
                    tex_file_name=row['tex_file_name'],
                    embedding_status=row['embedding_status'],
                    agentic_ai_score=row['agentic_ai_score'],
                    proximal_policy_optimization_score=row['proximal_policy_optimization_score'],
                    reinforcement_learning_score=row['reinforcement_learning_score'],
                    reasoning_models_score=row['reasoning_models_score'],
                    inference_time_scaling_score=row['inference_time_scaling_score'],
                    llm_validation_status=row['llm_validation_status'],
                    agentic_ai_relevance=row['agentic_ai_relevance'],
                    proximal_policy_optimization_relevance=row['proximal_policy_optimization_relevance'],
                    reinforcement_learning_relevance=row['reinforcement_learning_relevance'],
                    reasoning_models_relevance=row['reasoning_models_relevance'],
                    inference_time_scaling_relevance=row['inference_time_scaling_relevance'],
                    agentic_ai_justification=row['agentic_ai_justification'],
                    proximal_policy_optimization_justification=row['proximal_policy_optimization_justification'],
                    reinforcement_learning_justification=row['reinforcement_learning_justification'],
                    reasoning_models_justification=row['reasoning_models_justification'],
                    inference_time_scaling_justification=row['inference_time_scaling_justification'],
                    llm_score_status=row['llm_score_status'],
                    summary=row['summary'],
                    novelty_score=row['novelty_score'],
                    novelty_justification=row['novelty_justification'],
                    impact_score=row['impact_score'],
                    impact_justification=row['impact_justification'],
                    recommendation_score=row['recommendation_score'],
                    recommendation_justification=row['recommendation_justification'],
                    h_index_status=row['h_index_status'],
                    semantic_scholar_url=row['semantic_scholar_url'],
                    h_index_fetch_method=row['h_index_fetch_method'],
                    total_authors=row['total_authors'],
                    authors_found=row['authors_found'],
                    highest_h_index=row['highest_h_index'],
                    average_h_index=row['average_h_index'],
                    notable_authors_count=row['notable_authors_count'],
                    author_h_indexes=[
                        AuthorHIndex(
                            name=auth['name'],
                            profile_url=auth['profile_url'],
                            h_index=auth['h_index']
                        ) for auth in json.loads(row['author_h_indexes'])
                    ] if row['author_h_indexes'] else [],
                    errors=json.loads(row['errors']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                papers[paper.id] = paper
        
        logger.info(f"Loaded {len(papers)} papers from database")
        return papers