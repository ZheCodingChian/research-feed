from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class AuthorHIndex:
    """Represents H-index data for a single author."""
    name: str
    profile_url: Optional[str] = None
    h_index: Optional[int] = None


@dataclass
class Paper:
    """
    Represents a single academic paper with all its metadata and processing status.
    
    This class serves as the core data structure that flows through the entire pipeline,
    with each module potentially adding or modifying fields as processing progresses.
    """
    
    # Core arXiv metadata
    id: str  # arXiv ID (e.g., "2501.12345")
    title: str
    authors: List[str]
    categories: List[str]  # arXiv categories (e.g., ["cs.AI", "cs.LG"])
    abstract: str
    published_date: datetime
    
    # URL fields for paper access
    arxiv_url: Optional[str] = None  # Main arXiv abstract page URL
    pdf_url: Optional[str] = None    # Direct PDF download URL
    latex_url: Optional[str] = None  # LaTeX source files URL
    
    # Processing status and error tracking
    scraper_status: str = "initial"  # Track scraping state
    intro_status: str = "not_extracted"  # Track introduction extraction state
    errors: List[str] = field(default_factory=list)  # Store any error messages
    
    # Introduction extraction fields
    introduction_text: Optional[str] = None  # Extracted introduction content
    intro_extraction_method: Optional[str] = None  # How introduction was extracted
    tex_file_name: Optional[str] = None  # Source file name
    
    # Embedding similarity fields
    embedding_status: str = "not_embedded"  # Track embedding processing state
    rlhf_score: Optional[float] = None  # Similarity score for RLHF topic
    weak_supervision_score: Optional[float] = None  # Similarity score for weak supervision topic
    diffusion_reasoning_score: Optional[float] = None  # Similarity score for diffusion reasoning topic
    distributed_training_score: Optional[float] = None  # Similarity score for distributed training topic
    datasets_score: Optional[float] = None  # Similarity score for datasets topic
    highest_similarity_topic: Optional[str] = None  # Topic with highest similarity score
    
    # LLM validation fields
    llm_validation_status: str = "not_validated"  # Track LLM validation state
    rlhf_relevance: str = "not_validated"  # LLM relevance assessment for RLHF
    weak_supervision_relevance: str = "not_validated"  # LLM relevance assessment for weak supervision
    diffusion_reasoning_relevance: str = "not_validated"  # LLM relevance assessment for diffusion reasoning
    distributed_training_relevance: str = "not_validated"  # LLM relevance assessment for distributed training
    datasets_relevance: str = "not_validated"  # LLM relevance assessment for datasets
    rlhf_justification: str = "no_justification"  # LLM justification for RLHF assessment
    weak_supervision_justification: str = "no_justification"  # LLM justification for weak supervision assessment
    diffusion_reasoning_justification: str = "no_justification"  # LLM justification for diffusion reasoning assessment
    distributed_training_justification: str = "no_justification"  # LLM justification for distributed training assessment
    datasets_justification: str = "no_justification"  # LLM justification for datasets assessment
    
    # LLM scoring fields
    llm_score_status: str = "not_scored"  # Track LLM scoring state: not_scored, completed, failed, not_relevant_enough
    summary: Optional[str] = None  # LLM-generated paper summary
    novelty_score: Optional[str] = None  # High, Moderate, Low, None
    novelty_justification: Optional[str] = None  # LLM justification for novelty score
    impact_score: Optional[str] = None  # High, Moderate, Low, Negligible
    impact_justification: Optional[str] = None  # LLM justification for impact score
    recommendation_score: Optional[str] = None  # Must Read, Should Read, Can Skip, Ignore
    recommendation_justification: Optional[str] = None  # LLM justification for recommendation
    
    # H-index fetching fields
    h_index_status: str = "not_fetched"  # Track H-index processing: not_fetched, completed, failed
    semantic_scholar_url: Optional[str] = None  # URL to paper on Semantic Scholar
    h_index_fetch_method: Optional[str] = None  # Method used: full_id, base_id, title_search
    total_authors: Optional[int] = None  # Total number of authors
    authors_found: Optional[int] = None  # Authors found with profile data
    highest_h_index: Optional[int] = None  # Highest H-index among authors
    average_h_index: Optional[float] = None  # Average H-index of authors with data
    notable_authors_count: Optional[int] = None  # Authors with H-index > 5
    author_h_indexes: List[AuthorHIndex] = field(default_factory=list)  # Detailed author H-index data
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_generated: Optional[str] = None  # YYYY-MM-DD format for cache cleanup
    
    def add_error(self, error_message: str) -> None:
        """Add an error message to the paper's error list."""
        self.errors.append(error_message)
        self.updated_at = datetime.now()
    
    def update_scraper_status(self, new_status: str) -> None:
        """Update the paper's scraping status."""
        self.scraper_status = new_status
        self.updated_at = datetime.now()
    
    def update_intro_status(self, new_status: str) -> None:
        """Update the paper's introduction extraction status."""
        self.intro_status = new_status
        self.updated_at = datetime.now()
    
    def update_embedding_status(self, new_status: str) -> None:
        """Update the paper's embedding status."""
        self.embedding_status = new_status
        self.updated_at = datetime.now()
    
    def is_successfully_scraped(self) -> bool:
        """Check if the paper has been successfully scraped."""
        return self.scraper_status == "successfully_scraped"
    
    def has_scraping_failed(self) -> bool:
        """Check if scraping has failed for this paper."""
        return self.scraper_status == "scraping_failed"
    
    def is_intro_successful(self) -> bool:
        """Check if introduction extraction was successful."""
        return self.intro_status == "intro_successful"
    
    def can_skip_intro_extraction(self) -> bool:
        """Check if paper can skip introduction extraction."""
        return self.intro_status in ["intro_successful", "no_latex_source", "no_intro_found"]
    
    def is_embedding_completed(self) -> bool:
        """Check if embedding similarity calculation was successful."""
        return self.embedding_status == "completed"
    
    def update_llm_validation_status(self, new_status: str) -> None:
        """Update the paper's LLM validation status."""
        self.llm_validation_status = new_status
        self.updated_at = datetime.now()
    
    def is_llm_validation_completed(self) -> bool:
        """Check if LLM validation was successful."""
        return self.llm_validation_status == "completed"
    
    def can_skip_llm_validation(self) -> bool:
        """Check if paper can skip LLM validation."""
        return self.llm_validation_status in ["completed", "failed"] or not self.is_embedding_completed()
    
    def update_llm_score_status(self, new_status: str) -> None:
        """Update the paper's LLM scoring status."""
        self.llm_score_status = new_status
        self.updated_at = datetime.now()
    
    def is_llm_score_completed(self) -> bool:
        """Check if LLM scoring was successful."""
        return self.llm_score_status == "completed"
    
    def can_skip_llm_scoring(self) -> bool:
        """Check if paper can skip LLM scoring."""
        return self.llm_score_status in ["completed", "failed", "not_relevant_enough"]
    
    def has_highly_relevant_topic(self) -> bool:
        """Check if paper has at least one highly relevant or moderately relevant topic."""
        relevance_scores = [
            self.rlhf_relevance,
            self.weak_supervision_relevance,
            self.diffusion_reasoning_relevance,
            self.distributed_training_relevance,
            self.datasets_relevance
        ]
        return "Highly Relevant" in relevance_scores or "Moderately Relevant" in relevance_scores
    
    def update_h_index_status(self, new_status: str) -> None:
        """Update the paper's H-index fetching status."""
        self.h_index_status = new_status
        self.updated_at = datetime.now()
    
    def is_h_index_completed(self) -> bool:
        """Check if H-index fetching was successful."""
        return self.h_index_status == "completed"
    
    def can_skip_h_index_fetching(self) -> bool:
        """Check if paper can skip H-index fetching."""
        return self.h_index_status in ["completed", "failed"]
    
    def is_valuable_paper(self) -> bool:
        """Check if paper has Must Read or Should Read recommendation."""
        return self.recommendation_score in ["Must Read", "Should Read"]