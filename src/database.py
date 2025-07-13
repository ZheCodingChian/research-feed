import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from paper import Paper

logger = logging.getLogger('DATABASE')


class PaperDatabase:
    """
    Handles all database operations for caching Paper objects.
    
    This class provides a simple interface to store and retrieve Paper objects
    from SQLite, serving as the persistence layer for the pipeline.
    """
    
    def __init__(self, db_path: str = "cache.db"):
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
                    introduction_text TEXT,
                    intro_extraction_method TEXT,
                    tex_file_name TEXT,
                    embedding_status TEXT DEFAULT 'not_embedded',
                    rlhf_score REAL,
                    weak_supervision_score REAL,
                    diffusion_reasoning_score REAL,
                    distributed_training_score REAL,
                    highest_similarity_topic TEXT,
                    llm_validation_status TEXT DEFAULT 'not_validated',
                    rlhf_relevance TEXT DEFAULT 'not_validated',
                    weak_supervision_relevance TEXT DEFAULT 'not_validated',
                    diffusion_reasoning_relevance TEXT DEFAULT 'not_validated',
                    distributed_training_relevance TEXT DEFAULT 'not_validated',
                    rlhf_justification TEXT DEFAULT 'no_justification',
                    weak_supervision_justification TEXT DEFAULT 'no_justification',
                    diffusion_reasoning_justification TEXT DEFAULT 'no_justification',
                    distributed_training_justification TEXT DEFAULT 'no_justification',
                    llm_score_status TEXT DEFAULT 'not_scored',
                    summary TEXT,
                    novelty_score TEXT,
                    novelty_justification TEXT,
                    impact_score TEXT,
                    impact_justification TEXT,
                    recommendation_score TEXT,
                    recommendation_justification TEXT,
                    errors TEXT,  -- JSON array
                    created_at TEXT,  -- ISO format
                    updated_at TEXT   -- ISO format
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
                    arxiv_url, pdf_url, latex_url, scraper_status, intro_status, introduction_text,
                    intro_extraction_method, tex_file_name, embedding_status, rlhf_score,
                    weak_supervision_score, diffusion_reasoning_score, distributed_training_score,
                    highest_similarity_topic, llm_validation_status, rlhf_relevance,
                    weak_supervision_relevance, diffusion_reasoning_relevance, distributed_training_relevance,
                    rlhf_justification, weak_supervision_justification, diffusion_reasoning_justification,
                    distributed_training_justification, llm_score_status, summary, novelty_score,
                    novelty_justification, impact_score, impact_justification, recommendation_score,
                    recommendation_justification, errors, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                paper.introduction_text,
                paper.intro_extraction_method,
                paper.tex_file_name,
                paper.embedding_status,
                paper.rlhf_score,
                paper.weak_supervision_score,
                paper.diffusion_reasoning_score,
                paper.distributed_training_score,
                paper.highest_similarity_topic,
                paper.llm_validation_status,
                paper.rlhf_relevance,
                paper.weak_supervision_relevance,
                paper.diffusion_reasoning_relevance,
                paper.distributed_training_relevance,
                paper.rlhf_justification,
                paper.weak_supervision_justification,
                paper.diffusion_reasoning_justification,
                paper.distributed_training_justification,
                paper.llm_score_status,
                paper.summary,
                paper.novelty_score,
                paper.novelty_justification,
                paper.impact_score,
                paper.impact_justification,
                paper.recommendation_score,
                paper.recommendation_justification,
                json.dumps(paper.errors),
                paper.created_at.isoformat(),
                paper.updated_at.isoformat()
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
                introduction_text=row['introduction_text'],
                intro_extraction_method=row['intro_extraction_method'],
                tex_file_name=row['tex_file_name'],
                embedding_status=row['embedding_status'],
                rlhf_score=row['rlhf_score'],
                weak_supervision_score=row['weak_supervision_score'],
                diffusion_reasoning_score=row['diffusion_reasoning_score'],
                distributed_training_score=row['distributed_training_score'],
                highest_similarity_topic=row['highest_similarity_topic'],
                llm_validation_status=row['llm_validation_status'],
                rlhf_relevance=row['rlhf_relevance'],
                weak_supervision_relevance=row['weak_supervision_relevance'],
                diffusion_reasoning_relevance=row['diffusion_reasoning_relevance'],
                distributed_training_relevance=row['distributed_training_relevance'],
                rlhf_justification=row['rlhf_justification'],
                weak_supervision_justification=row['weak_supervision_justification'],
                diffusion_reasoning_justification=row['diffusion_reasoning_justification'],
                distributed_training_justification=row['distributed_training_justification'],
                llm_score_status=row['llm_score_status'],
                summary=row['summary'],
                novelty_score=row['novelty_score'],
                novelty_justification=row['novelty_justification'],
                impact_score=row['impact_score'],
                impact_justification=row['impact_justification'],
                recommendation_score=row['recommendation_score'],
                recommendation_justification=row['recommendation_justification'],
                errors=json.loads(row['errors']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
    
    def save_papers(self, papers: Dict[str, Paper]) -> None:
        """Save multiple papers to the database efficiently."""
        logger.info(f"Saving {len(papers)} papers to database")
        
        with sqlite3.connect(self.db_path) as conn:
            for paper in papers.values():
                conn.execute("""
                    INSERT OR REPLACE INTO papers (
                        id, title, authors, categories, abstract, published_date,
                        arxiv_url, pdf_url, latex_url, scraper_status, intro_status, introduction_text,
                        intro_extraction_method, tex_file_name, embedding_status, rlhf_score,
                        weak_supervision_score, diffusion_reasoning_score, distributed_training_score,
                        highest_similarity_topic, llm_validation_status, rlhf_relevance,
                        weak_supervision_relevance, diffusion_reasoning_relevance, distributed_training_relevance,
                        rlhf_justification, weak_supervision_justification, diffusion_reasoning_justification,
                        distributed_training_justification, llm_score_status, summary, novelty_score,
                        novelty_justification, impact_score, impact_justification, recommendation_score,
                        recommendation_justification, errors, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    paper.introduction_text,
                    paper.intro_extraction_method,
                    paper.tex_file_name,
                    paper.embedding_status,
                    paper.rlhf_score,
                    paper.weak_supervision_score,
                    paper.diffusion_reasoning_score,
                    paper.distributed_training_score,
                    paper.highest_similarity_topic,
                    paper.llm_validation_status,
                    paper.rlhf_relevance,
                    paper.weak_supervision_relevance,
                    paper.diffusion_reasoning_relevance,
                    paper.distributed_training_relevance,
                    paper.rlhf_justification,
                    paper.weak_supervision_justification,
                    paper.diffusion_reasoning_justification,
                    paper.distributed_training_justification,
                    paper.llm_score_status,
                    paper.summary,
                    paper.novelty_score,
                    paper.novelty_justification,
                    paper.impact_score,
                    paper.impact_justification,
                    paper.recommendation_score,
                    paper.recommendation_justification,
                    json.dumps(paper.errors),
                    paper.created_at.isoformat(),
                    paper.updated_at.isoformat()
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
                    introduction_text=row['introduction_text'],
                    intro_extraction_method=row['intro_extraction_method'],
                    tex_file_name=row['tex_file_name'],
                    embedding_status=row['embedding_status'],
                    rlhf_score=row['rlhf_score'],
                    weak_supervision_score=row['weak_supervision_score'],
                    diffusion_reasoning_score=row['diffusion_reasoning_score'],
                    distributed_training_score=row['distributed_training_score'],
                    highest_similarity_topic=row['highest_similarity_topic'],
                    errors=json.loads(row['errors']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                papers[paper.id] = paper
        
        logger.info(f"Loaded {len(papers)} papers from database")
        return papers