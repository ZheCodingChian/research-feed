#!/usr/bin/env python3
"""
Main orchestrator for the modular paper processing pipeline.

This script serves as the central coordinator that manages the execution flow,
handles command-line arguments, configures logging, and manages data persistence
through the caching system.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Dict
from paper import Paper
from database import PaperDatabase


def setup_logging() -> None:
    """
    Configure the centralized logging system.
    
    This function sets up logging to both file and console with a consistent
    format throughout the entire application. Each module will automatically
    tap into this configuration.
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate log filename based on current date
    log_filename = f"logs/{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging format
    log_format = '%(asctime)s,%(msecs)03d [%(name)s] [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Also log to console
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Modular Paper Processing Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --date 2025-01-08        Process papers from January 8, 2025
  %(prog)s --test papers.txt        Process papers listed in papers.txt
        """
    )
    
    # Create mutually exclusive group for run modes
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--date',
        type=str,
        help='Process papers from specific date (YYYY-MM-DD format)'
    )
    mode_group.add_argument(
        '--test',
        type=str,
        help='Process papers from test file (one arXiv ID per line)'
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate the parsed arguments."""
    if args.date:
        try:
            datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {args.date}. Expected YYYY-MM-DD")
    
    if args.test:
        if not os.path.exists(args.test):
            raise FileNotFoundError(f"Test file not found: {args.test}")


def save_to_cache(runtime_paper_dict: Dict[str, Paper]) -> None:
    """
    Save the current state of all papers to the cache database.
    
    This function performs an INSERT OR UPDATE operation for every paper
    in the runtime dictionary, ensuring the cache always reflects the
    latest state of processing.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
    """
    logger = logging.getLogger('MAIN')
    
    if not runtime_paper_dict:
        logger.info("No papers to save to cache")
        return
    
    db = PaperDatabase()
    db.save_papers(runtime_paper_dict)
    logger.info(f"Saved {len(runtime_paper_dict)} papers to cache")


def main() -> None:
    """Main entry point for the pipeline."""
    # Set up logging first
    setup_logging()
    logger = logging.getLogger('MAIN')
    
    try:
        # Parse and validate arguments
        args = parse_arguments()
        validate_arguments(args)
        
        # Determine run mode and value
        if args.date:
            run_mode = 'date'
            run_value = args.date
        else:  # args.test
            run_mode = 'test'
            run_value = args.test
        
        logger.info(f"Starting pipeline with --{run_mode} {run_value}")
        
        # Import appropriate scraper module based on run mode
        if run_mode == 'date':
            from modules import scraper
        else:  # run_mode == 'test'
            from modules import scraper_test as scraper
        
        # Step 1: Execute scraper module
        logger.info("Executing scraper module")
        runtime_paper_dict = scraper.run(run_mode, run_value)
        
        # Save Point: Persist scraper results to cache
        save_to_cache(runtime_paper_dict)
        
        # Future modules will be added here following the same pattern:
        # 1. Execute module
        # 2. Save to cache
        # 3. Continue to next module
        
        # TODO: Add subsequent modules here
        # logger.info("Executing intro_extractor module")
        # runtime_paper_dict = intro_extractor.run(runtime_paper_dict)
        # save_to_cache(runtime_paper_dict)
        
        # logger.info("Executing embed_similarity module")
        # runtime_paper_dict = embed_similarity.run(runtime_paper_dict)
        # save_to_cache(runtime_paper_dict)
        
        # ... and so on for other modules
        
        # Final summary
        total_papers = len(runtime_paper_dict)
        successful_papers = sum(1 for p in runtime_paper_dict.values() if p.is_successfully_scraped())
        failed_papers = sum(1 for p in runtime_paper_dict.values() if p.has_scraping_failed())
        
        logger.info(f"Pipeline completed: {total_papers} total papers, "
                   f"{successful_papers} successful, {failed_papers} failed")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 