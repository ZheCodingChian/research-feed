"""
Database Cleanup Module

This module manages the cleanup of old papers from the database to prevent 
unlimited growth. It updates the last_generated date for all papers in the current 
runtime and removes papers older than the configured retention period.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict
from paper import Paper

logger = logging.getLogger('DATABASE_CLEANUP')


def run(runtime_paper_dict: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Run database cleanup operations.
    
    This function:
    1. Adds the last_generated column if it doesn't exist (for backward compatibility)
    2. Updates the last_generated date for all papers in the runtime dictionary
    3. Removes papers from the database that are older than the retention period
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects from current run
        config: Database cleanup configuration containing retention_days
        
    Returns:
        The unchanged papers dictionary
    """
    logger.info(f"Starting database cleanup for {len(runtime_paper_dict)} runtime papers")
    
    try:
        # Get configuration
        retention_days = config.get('retention_days', 14)
        current_date = datetime.now().strftime('%Y-%m-%d')
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d')
        
        logger.info(f"Using retention period: {retention_days} days (cutoff date: {cutoff_date})")
        
        # Connect to the database
        with sqlite3.connect("cache.sqlite") as conn:
            # Step 1: Ensure the last_generated column exists (for backward compatibility)
            _ensure_last_generated_column(conn)
            
            # Step 2: Update last_generated for all runtime papers
            updated_count = _update_runtime_papers(conn, runtime_paper_dict, current_date)
            
            # Step 3: Clean up old papers
            deleted_count = _cleanup_old_papers(conn, cutoff_date)
            
        logger.info(f"Database cleanup complete: {updated_count} papers updated, {deleted_count} papers deleted")
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        raise
    
    return runtime_paper_dict


def _ensure_last_generated_column(conn: sqlite3.Connection) -> None:
    """
    Ensure the last_generated column exists in the papers table.
    
    This is for backward compatibility with existing databases that might not
    have this column yet.
    """
    try:
        # Check if column exists by trying to select it
        cursor = conn.execute("SELECT last_generated FROM papers LIMIT 1")
        cursor.fetchone()
        logger.debug("last_generated column already exists")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        logger.info("Adding last_generated column to papers table")
        conn.execute("ALTER TABLE papers ADD COLUMN last_generated TEXT")
        logger.info("Successfully added last_generated column")


def _update_runtime_papers(conn: sqlite3.Connection, runtime_paper_dict: Dict[str, Paper], current_date: str) -> int:
    """
    Update the last_generated date for all papers in the runtime dictionary.
    
    Args:
        conn: Database connection
        runtime_paper_dict: Dictionary of runtime papers
        current_date: Current date in YYYY-MM-DD format
        
    Returns:
        Number of papers updated
    """
    logger.info(f"Updating last_generated date to {current_date} for runtime papers")
    
    # Update the Paper objects in memory
    for paper in runtime_paper_dict.values():
        paper.last_generated = current_date
    
    # Update the database
    paper_ids = list(runtime_paper_dict.keys())
    placeholders = ','.join('?' for _ in paper_ids)
    
    cursor = conn.execute(f"""
        UPDATE papers 
        SET last_generated = ? 
        WHERE id IN ({placeholders})
    """, [current_date] + paper_ids)
    
    updated_count = cursor.rowcount
    logger.info(f"Updated last_generated for {updated_count} papers in database")
    
    return updated_count


def _cleanup_old_papers(conn: sqlite3.Connection, cutoff_date: str) -> int:
    """
    Remove papers from the database that are older than the cutoff date.
    
    Args:
        conn: Database connection
        cutoff_date: Papers older than this date will be deleted (YYYY-MM-DD format)
        
    Returns:
        Number of papers deleted
    """
    logger.info(f"Deleting papers with last_generated older than {cutoff_date}")
    
    # First, count how many papers will be deleted for logging
    cursor = conn.execute("""
        SELECT COUNT(*) FROM papers 
        WHERE last_generated IS NOT NULL AND last_generated < ?
    """, (cutoff_date,))
    
    count_to_delete = cursor.fetchone()[0]
    
    if count_to_delete == 0:
        logger.info("No old papers found to delete")
        return 0
    
    logger.info(f"Found {count_to_delete} papers to delete")
    
    # Delete the old papers
    cursor = conn.execute("""
        DELETE FROM papers 
        WHERE last_generated IS NOT NULL AND last_generated < ?
    """, (cutoff_date,))
    
    deleted_count = cursor.rowcount
    logger.info(f"Successfully deleted {deleted_count} old papers from database")
    
    return deleted_count
