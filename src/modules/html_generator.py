#!/usr/bin/env python3
"""
HTML Generator Module - Enhanced Version

Generates beautiful HTML reports from cache.db using the improved template system.
Adapted from the new report generator to work within the pipeline framework.
"""

import sqlite3
import json
import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from paper import Paper

logger = logging.getLogger('HTML_GENERATOR')

# Template paths relative to project root
TEMPLATE_PATH = 'templates/papers.html'
LANDING_TEMPLATE_PATH = 'templates/landing.html'


def safe_json_escape(text: Any) -> Any:
    """
    Safely escape text for JSON embedding in HTML.
    Handles LaTeX notation, special characters, and potential injection issues.
    """
    if text is None:
        return None
    
    if not isinstance(text, str):
        return text
    
    return text


def safe_json_dumps(data: Dict[str, Any]) -> str:
    """
    Safely serialize data to JSON with proper escaping and formatting.
    """
    try:
        # Use ensure_ascii=False to preserve Unicode, with proper indentation
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        # Additional HTML-safe escaping for script injection prevention
        json_str = json_str.replace('</script>', '<\\/script>')
        json_str = json_str.replace('<!--', '<\\!--')
        json_str = json_str.replace('-->', '--\\>')
        
        return json_str
        
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization failed: {e}")
        raise Exception(f"Failed to serialize data to JSON: {e}")


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Get database connection with proper error handling."""
    try:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
        
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise Exception(f"Cannot connect to database: {e}")


def parse_json_field(field_value: str) -> List[Any]:
    """Safely parse JSON fields from database."""
    if not field_value:
        return []
    
    try:
        return json.loads(field_value)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON field: {field_value[:50]}...")
        return []


def format_paper_data(row: sqlite3.Row) -> Dict[str, Any]:
    """
    Format a database row into the required JSON structure with safe escaping.
    """
    try:
        # Parse JSON fields with validation
        authors = parse_json_field(row['authors'])
        categories = parse_json_field(row['categories']) 
        author_h_indexes = parse_json_field(row['author_h_indexes'])
        
        # Apply safe escaping to text fields
        title = safe_json_escape(row['title'])
        abstract = safe_json_escape(row['abstract'])
        summary = safe_json_escape(row['summary'])
        
        # Apply escaping to justification fields
        recommendation_justification = safe_json_escape(row['recommendation_justification'])
        novelty_justification = safe_json_escape(row['novelty_justification'])
        impact_justification = safe_json_escape(row['impact_justification'])
        rlhf_justification = safe_json_escape(row['rlhf_justification'])
        weak_supervision_justification = safe_json_escape(row['weak_supervision_justification'])
        diffusion_reasoning_justification = safe_json_escape(row['diffusion_reasoning_justification'])
        distributed_training_justification = safe_json_escape(row['distributed_training_justification'])
        datasets_justification = safe_json_escape(row['datasets_justification'])
        
        # Apply escaping to author names in arrays
        escaped_authors = [safe_json_escape(author) for author in authors]
        escaped_categories = [safe_json_escape(cat) for cat in categories]
        
        # Handle author h-indexes with escaping
        escaped_author_h_indexes = []
        for author_info in author_h_indexes:
            if isinstance(author_info, dict):
                escaped_author_info = {
                    'name': safe_json_escape(author_info.get('name', '')),
                    'h_index': author_info.get('h_index', 0),
                    'profile_url': safe_json_escape(author_info.get('profile_url', ''))
                }
                escaped_author_h_indexes.append(escaped_author_info)
        
        # Format date (extract date part from ISO datetime)
        published_date = row['published_date']
        if published_date:
            try:
                # Parse ISO format and extract date
                dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                published_date = dt.strftime('%Y-%m-%d')
            except (ValueError, AttributeError):
                # If parsing fails, try to extract YYYY-MM-DD pattern
                match = re.search(r'(\d{4}-\d{2}-\d{2})', published_date)
                published_date = match.group(1) if match else published_date
        
        # Build complete paper data structure
        paper_data = {
            "id": row['id'],
            "title": title,
            "authors": escaped_authors,
            "categories": escaped_categories,
            "abstract": abstract,
            "published_date": published_date,
            "arxiv_url": row['arxiv_url'],
            "pdf_url": row['pdf_url'],
            "scraper_status": row['scraper_status'],
            "intro_status": row['intro_status'],
            "embedding_status": row['embedding_status'],
            "rlhf_score": float(row['rlhf_score']) if row['rlhf_score'] is not None else 0.0,
            "weak_supervision_score": float(row['weak_supervision_score']) if row['weak_supervision_score'] is not None else 0.0,
            "diffusion_reasoning_score": float(row['diffusion_reasoning_score']) if row['diffusion_reasoning_score'] is not None else 0.0,
            "distributed_training_score": float(row['distributed_training_score']) if row['distributed_training_score'] is not None else 0.0,
            "datasets_score": float(row['datasets_score']) if row['datasets_score'] is not None else 0.0,
            "llm_validation_status": row['llm_validation_status'],
            "rlhf_relevance": row['rlhf_relevance'],
            "weak_supervision_relevance": row['weak_supervision_relevance'],
            "diffusion_reasoning_relevance": row['diffusion_reasoning_relevance'],
            "distributed_training_relevance": row['distributed_training_relevance'],
            "datasets_relevance": row['datasets_relevance'],
            "rlhf_justification": rlhf_justification,
            "weak_supervision_justification": weak_supervision_justification,
            "diffusion_reasoning_justification": diffusion_reasoning_justification,
            "distributed_training_justification": distributed_training_justification,
            "datasets_justification": datasets_justification,
            "llm_score_status": row['llm_score_status'],
            "summary": summary,
            "novelty_score": row['novelty_score'],
            "novelty_justification": novelty_justification,
            "impact_score": row['impact_score'],
            "impact_justification": impact_justification,
            "recommendation_score": row['recommendation_score'],
            "recommendation_justification": recommendation_justification,
            "h_index_status": row['h_index_status'],
            "semantic_scholar_url": row['semantic_scholar_url'],
            "total_authors": row['total_authors'] if row['total_authors'] is not None else 0,
            "authors_found": row['authors_found'] if row['authors_found'] is not None else 0,
            "highest_h_index": row['highest_h_index'] if row['highest_h_index'] is not None else 0,
            "average_h_index": float(row['average_h_index']) if row['average_h_index'] is not None else 0.0,
            "notable_authors_count": row['notable_authors_count'] if row['notable_authors_count'] is not None else 0,
            "author_h_indexes": escaped_author_h_indexes
        }
        
        return paper_data
        
    except Exception as e:
        logger.error(f"Error formatting paper {row.get('id', 'unknown')}: {e}")
        raise Exception(f"Failed to format paper data: {e}")


def get_papers_for_date(db_path: str, date: str) -> Dict[str, Any]:
    """Get all papers for a specific date."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        
        # Get total count first
        cursor.execute(
            "SELECT COUNT(*) as total FROM papers WHERE DATE(published_date) = ?",
            (date,)
        )
        total_papers = cursor.fetchone()['total']
        
        if total_papers == 0:
            logger.warning(f"No papers found for date {date}")
            return {
                "papers": [],
                "total_papers": 0,
                "date": date
            }
        
        # Get papers for the date
        query = """
        SELECT id, title, authors, categories, abstract, published_date, arxiv_url, pdf_url,
               scraper_status, intro_status, embedding_status, rlhf_score, weak_supervision_score,
               diffusion_reasoning_score, distributed_training_score, datasets_score,
               llm_validation_status, rlhf_relevance, weak_supervision_relevance,
               diffusion_reasoning_relevance, distributed_training_relevance, datasets_relevance,
               rlhf_justification, weak_supervision_justification, diffusion_reasoning_justification,
               distributed_training_justification, datasets_justification, llm_score_status,
               summary, novelty_score, novelty_justification, impact_score, impact_justification,
               recommendation_score, recommendation_justification, h_index_status, semantic_scholar_url,
               total_authors, authors_found, highest_h_index, average_h_index, notable_authors_count,
               author_h_indexes
        FROM papers 
        WHERE DATE(published_date) = ?
        ORDER BY id ASC
        """
        
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        
        # Format papers data
        papers = []
        for row in rows:
            paper_data = format_paper_data(row)
            papers.append(paper_data)
        
        result = {
            "papers": papers,
            "total_papers": len(papers),
            "date": date
        }
        
        logger.info(f"Processed {len(papers)} papers for {date}")
        return result
        
    except sqlite3.Error as e:
        logger.error(f"Database query failed for {date}: {e}")
        raise Exception(f"Failed to query papers for {date}: {e}")
    finally:
        conn.close()


def format_date_for_title(date_str: str) -> str:
    """Format YYYY-MM-DD date into human readable format."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d %B %Y')  # "15 July 2025"
    except ValueError:
        logger.warning(f"Invalid date format: {date_str}")
        return date_str


def get_day_name(date_str: str) -> str:
    """Get day name from YYYY-MM-DD date string."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%A')  # "Friday"
    except ValueError:
        logger.warning(f"Invalid date format: {date_str}")
        return ""


def get_landing_page_data(db_path: str) -> List[Dict[str, Any]]:
    """
    Get data for all dates to populate the landing page.
    Returns list of date objects with stats and URL.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        
        # Get all dates with papers
        cursor.execute("""
            SELECT DISTINCT DATE(published_date) as date 
            FROM papers 
            WHERE published_date IS NOT NULL 
            ORDER BY date DESC
        """)
        
        dates = [row['date'] for row in cursor.fetchall()]
        logger.info(f"Processing {len(dates)} dates for landing page")
        
        landing_data = []
        
        for date in dates:
            # Get total papers for this date
            cursor.execute(
                "SELECT COUNT(*) as total FROM papers WHERE DATE(published_date) = ?",
                (date,)
            )
            total_papers = cursor.fetchone()['total']
            
            if total_papers == 0:
                continue
            
            # Get recommendation score counts
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN recommendation_score = 'Must Read' THEN 1 END) as must_read,
                    COUNT(CASE WHEN recommendation_score = 'Should Read' THEN 1 END) as should_read
                FROM papers 
                WHERE DATE(published_date) = ?
            """, (date,))
            
            recommendation_counts = cursor.fetchone()
            
            # Get relevance counts for each category
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN rlhf_relevance IN ('Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant') THEN 1 END) as rlhf,
                    COUNT(CASE WHEN weak_supervision_relevance IN ('Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant') THEN 1 END) as weak_supervision,
                    COUNT(CASE WHEN diffusion_reasoning_relevance IN ('Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant') THEN 1 END) as diffusion_reasoning,
                    COUNT(CASE WHEN distributed_training_relevance IN ('Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant') THEN 1 END) as distributed_training,
                    COUNT(CASE WHEN datasets_relevance IN ('Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant') THEN 1 END) as datasets
                FROM papers 
                WHERE DATE(published_date) = ?
            """, (date,))
            
            relevance_counts = cursor.fetchone()
            
            # Format the data
            date_data = {
                "date": format_date_for_title(date),
                "day": get_day_name(date),
                "stats": {
                    "Must Read": recommendation_counts['must_read'],
                    "Should Read": recommendation_counts['should_read'],
                    "RLHF": relevance_counts['rlhf'],
                    "Weak Supervision": relevance_counts['weak_supervision'],
                    "Diffusion Reasoning": relevance_counts['diffusion_reasoning'],
                    "Distributed Training": relevance_counts['distributed_training'],
                    "Datasets": relevance_counts['datasets']
                },
                "total": total_papers,
                "url": f"{date}.html"
            }
            
            landing_data.append(date_data)
            logger.debug(f"Processed date {date}: {total_papers} papers")
        
        logger.info(f"Generated landing page data for {len(landing_data)} dates")
        return landing_data
        
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        raise Exception(f"Failed to generate landing page data: {e}")
    finally:
        conn.close()


def generate_static_page(date: str, paper_data: Dict[str, Any], template_content: str) -> str:
    """
    Generate static HTML page by injecting paper data into template.
    """
    try:
        # Format date for titles
        formatted_date = format_date_for_title(date)
        page_title = f"Papers Published on {formatted_date}"
        
        # Serialize paper data to JSON
        json_data = safe_json_dumps(paper_data)
        
        # Replace placeholders in template
        html_content = template_content
        
        # Replace title placeholders
        html_content = html_content.replace('PLACEHOLDER_TITLE', formatted_date)
        html_content = html_content.replace('PLACEHOLDER_MOBILE_TITLE', page_title)
        html_content = html_content.replace('PLACEHOLDER_DESKTOP_TITLE', page_title)
        
        # Replace data placeholder
        html_content = html_content.replace('<!--DATA_HERE-->', json_data)
        
        return html_content
        
    except Exception as e:
        logger.error(f"Failed to generate page for {date}: {e}")
        raise Exception(f"Page generation failed: {e}")


def generate_landing_page(landing_data: List[Dict[str, Any]], landing_template_content: str) -> str:
    """
    Generate landing page by injecting feed data into landing page template.
    """
    try:
        # Serialize landing data to JSON
        json_data = safe_json_dumps(landing_data)
        
        # Replace data placeholder in landing page template
        html_content = landing_template_content.replace('<!--LANDING_DATA_HERE-->', json_data)
        
        return html_content
        
    except Exception as e:
        logger.error(f"Failed to generate landing page: {e}")
        raise Exception(f"Landing page generation failed: {e}")


def run(papers: Dict[str, Paper], run_mode: str, run_value: str, config: dict) -> Dict[str, Paper]:
    """
    Run HTML generation for the processed papers.
    
    Args:
        papers: Dictionary of paper_id -> Paper objects (ignored - we read from cache.db)
        run_mode: 'date' or 'test'
        run_value: Date string (YYYY-MM-DD) or test file name
        config: HTML generation configuration
        
    Returns:
        The unchanged papers dictionary
    """
    logger.info(f"Starting HTML generation with new enhanced templates")
    logger.info(f"Run mode: {run_mode}, Run value: {run_value}")
    
    # Handle test runs - not implemented yet
    if run_mode == 'test':
        raise NotImplementedError("Test run HTML generation not yet implemented")
    
    try:
        # Get project root and set up paths
        project_root = Path(__file__).parent.parent.parent
        template_path = project_root / TEMPLATE_PATH
        landing_template_path = project_root / LANDING_TEMPLATE_PATH
        output_dir = project_root / config.get('output_dir', 'report')
        db_path = project_root / 'cache.db'
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate templates exist
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        if not landing_template_path.exists():
            raise FileNotFoundError(f"Landing page template not found: {landing_template_path}")
        
        # Read template contents
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        logger.info(f"Loaded template from {template_path}")
        
        with open(landing_template_path, 'r', encoding='utf-8') as f:
            landing_template_content = f.read()
        logger.info(f"Loaded landing page template from {landing_template_path}")
        
        # Generate papers page for the current date
        logger.info(f"Processing papers for date: {run_value}")
        
        # Get paper data for this date from cache.db
        paper_data = get_papers_for_date(str(db_path), run_value)
        
        if paper_data['total_papers'] == 0:
            logger.warning(f"No papers found for date {run_value}")
            return papers
        
        # Generate HTML page for this date
        html_content = generate_static_page(run_value, paper_data, template_content)
        
        # Write to file
        output_file = output_dir / f"{run_value}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated {output_file} with {paper_data['total_papers']} papers")
        
        # Generate/update landing page with all dates
        logger.info("Generating updated landing page")
        landing_data = get_landing_page_data(str(db_path))
        landing_html = generate_landing_page(landing_data, landing_template_content)
        
        # Write landing page
        landing_output_file = output_dir / "index.html"
        with open(landing_output_file, 'w', encoding='utf-8') as f:
            f.write(landing_html)
        
        logger.info(f"Generated {landing_output_file} with {len(landing_data)} date entries")
        logger.info(f"HTML generation complete")
        
    except Exception as e:
        logger.error(f"HTML generation failed: {e}")
        raise
    
    return papers