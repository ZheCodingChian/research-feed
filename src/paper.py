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
    
    # Processing status and error tracking
    status: str = "initial"  # Track processing state
    errors: List[str] = field(default_factory=list)  # Store any error messages
    

    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_error(self, error_message: str) -> None:
        """Add an error message to the paper's error list."""
        self.errors.append(error_message)
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: str) -> None:
        """Update the paper's processing status."""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def is_successfully_scraped(self) -> bool:
        """Check if the paper has been successfully scraped."""
        return self.status == "successfully_scraped"
    
    def has_scraping_failed(self) -> bool:
        """Check if scraping has failed for this paper."""
        return self.status == "scraping_failed" 