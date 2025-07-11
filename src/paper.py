from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


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
    highest_similarity_topic: Optional[str] = None  # Topic with highest similarity score
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
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