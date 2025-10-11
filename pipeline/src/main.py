#!/usr/bin/env python3
"""
Main orchestrator for the arXiv paper data generation pipeline.

This script serves as the central coordinator that manages the execution flow,
handles command-line arguments, configures logging, and manages data persistence
in the SQLite database.
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
    # Create logs directory if it doesn't exist (force to pipeline root)
    pipeline_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(pipeline_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename based on current date
    log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
    
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
        description='arXiv Paper Data Generation Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --date 2025-01-15        Process papers from January 15, 2025
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


def save_to_database(runtime_paper_dict: Dict[str, Paper]) -> None:
    """
    Save the current state of all papers to the database.

    This function performs an INSERT OR UPDATE operation for every paper
    in the runtime dictionary, ensuring the database always reflects the
    latest state of processing.

    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
    """
    logger = logging.getLogger('MAIN')

    if not runtime_paper_dict:
        logger.info("No papers to save to database")
        return

    db = PaperDatabase()
    db.save_papers(runtime_paper_dict)
    logger.info(f"Saved {len(runtime_paper_dict)} papers to database")


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
            logger.info(f"Starting pipeline with --date {run_value}")
            
            # Import and run date-based scraper
            from modules import scraper
            runtime_paper_dict = scraper.run(run_mode, run_value)
        else:  # args.test
            run_mode = 'test'
            run_value = args.test
            logger.info(f"Starting pipeline with --test {run_value}")
            
            # Import and run test-based scraper
            from modules import test_scraper
            runtime_paper_dict = test_scraper.run(run_mode, run_value)
        
        # Step 1: Save scraped papers to database
        logger.info("Executing scraper module")
        save_to_database(runtime_paper_dict)

        # Step 2: Execute introduction extractor module
        logger.info("Executing introduction extractor module")
        from modules import intro_extractor
        import config
        runtime_paper_dict = intro_extractor.run(runtime_paper_dict, config.LATEX_EXTRACTION)
        save_to_database(runtime_paper_dict)

        # Step 3: Execute embedding similarity module
        logger.info("Executing embedding similarity module")
        from modules import embedding_similarity
        runtime_paper_dict = embedding_similarity.run(runtime_paper_dict, config.EMBEDDING)
        save_to_database(runtime_paper_dict)

        # Step 4: Execute LLM validation module
        logger.info("Executing LLM validation module")
        from modules import llm_validation
        runtime_paper_dict = llm_validation.run(runtime_paper_dict, config.LLM_VALIDATION)
        save_to_database(runtime_paper_dict)

        # Step 5: Execute LLM scoring module
        logger.info("Executing LLM scoring module")
        from modules import llm_scoring
        runtime_paper_dict = llm_scoring.run(runtime_paper_dict, config.LLM_SCORING)
        save_to_database(runtime_paper_dict)

        # Step 6: Execute H-index fetching module
        logger.info("Executing H-index fetching module")
        from modules import h_index_fetching
        runtime_paper_dict = h_index_fetching.run(runtime_paper_dict, config.H_INDEX_FETCHING)
        save_to_database(runtime_paper_dict)

        # Step 7: Execute database cleanup module
        logger.info("Executing database cleanup module")
        try:
            from modules import database_cleanup
            runtime_paper_dict = database_cleanup.run(runtime_paper_dict, config.DATABASE_CLEANUP)
            save_to_database(runtime_paper_dict)
        except Exception as e:
            logger.warning(f"Database cleanup failed: {e}")
            logger.info("Pipeline will continue despite database cleanup failure")

        # Step 8: Execute Slack notification module
        logger.info("Executing Slack notification module")
        try:
            from modules import slack
            runtime_paper_dict = slack.run(runtime_paper_dict, {})
            save_to_database(runtime_paper_dict)
        except Exception as e:
            logger.warning(f"Slack notification failed: {e}")
            logger.info("Pipeline will continue despite Slack notification failure")

        # Final summary
        total_papers = len(runtime_paper_dict)
        successful_papers = sum(1 for p in runtime_paper_dict.values() if p.is_successfully_scraped())
        failed_papers = sum(1 for p in runtime_paper_dict.values() if p.has_scraping_failed())
        intro_successful = sum(1 for p in runtime_paper_dict.values() if p.is_intro_successful())
        intro_failed = sum(1 for p in runtime_paper_dict.values() if p.intro_status not in ["not_extracted", "intro_successful"])
        embedding_successful = sum(1 for p in runtime_paper_dict.values() if p.is_embedding_completed())
        embedding_failed = sum(1 for p in runtime_paper_dict.values() if p.embedding_status == "failed")
        llm_validation_successful = sum(1 for p in runtime_paper_dict.values() if p.is_llm_validation_completed())
        llm_validation_failed = sum(1 for p in runtime_paper_dict.values() if p.llm_validation_status == "failed")
        llm_scoring_successful = sum(1 for p in runtime_paper_dict.values() if p.is_llm_score_completed())
        llm_scoring_failed = sum(1 for p in runtime_paper_dict.values() if p.llm_score_status == "failed")
        h_index_successful = sum(1 for p in runtime_paper_dict.values() if p.is_h_index_completed())
        h_index_failed = sum(1 for p in runtime_paper_dict.values() if p.h_index_status == "failed")

        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Total papers processed: {total_papers}")
        logger.info(f"  Scraping: {successful_papers} successful, {failed_papers} failed")
        logger.info(f"  Introduction extraction: {intro_successful} successful, {intro_failed} failed/skipped")
        logger.info(f"  Embedding similarity: {embedding_successful} successful, {embedding_failed} failed")
        logger.info(f"  LLM validation: {llm_validation_successful} successful, {llm_validation_failed} failed")
        logger.info(f"  LLM scoring: {llm_scoring_successful} successful, {llm_scoring_failed} failed")
        logger.info(f"  H-index fetching: {h_index_successful} successful, {h_index_failed} failed")
        logger.info(f"Data saved to: database.sqlite")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()