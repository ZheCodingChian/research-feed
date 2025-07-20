"""
Slack notification module for paper processing pipeline.

This module sends a summary of processed papers to a Slack channel,
including relevance statistics for each topic.
"""

import logging
import os
from typing import Dict, List
from datetime import datetime
import requests
from paper import Paper


# Topic configuration
TOPICS = {
    'RLHF': 'rlhf_relevance',
    'Weak supervision': 'weak_supervision_relevance', 
    'Diffusion Reasoning': 'diffusion_reasoning_relevance',
    'Distributed Training': 'distributed_training_relevance',
    'Datasets': 'datasets_relevance'
}

# Relevance levels to count
RELEVANCE_LEVELS = ['Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant']


def count_papers_by_relevance(runtime_paper_dict: Dict[str, Paper], topic_field: str) -> Dict[str, int]:
    """
    Count papers by relevance level for a specific topic.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
        topic_field: The field name to check for relevance (e.g., 'rlhf_relevance')
    
    Returns:
        Dictionary with counts for each relevance level
    """
    counts = {level: 0 for level in RELEVANCE_LEVELS}
    
    for paper in runtime_paper_dict.values():
        relevance = getattr(paper, topic_field, "not_validated")
        if relevance in counts:
            counts[relevance] += 1
    
    return counts


def format_slack_message(runtime_paper_dict: Dict[str, Paper], run_mode: str, run_value: str) -> str:
    """
    Format the Slack message with paper processing summary.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
        run_mode: 'date' or 'test' mode
        run_value: The date string or test file name
    
    Returns:
        Formatted Slack message string
    """
    # Format the date/source line
    if run_mode == 'date':
        # Convert YYYY-MM-DD to DD-MM-YYYY format
        try:
            date_obj = datetime.strptime(run_value, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d-%m-%Y')
            source_line = f"Date papers are fetched from: {formatted_date}"
        except ValueError:
            source_line = f"Date papers are fetched from: {run_value}"
    else:
        source_line = f"Papers fetched from test file: {run_value}"
    
    # Count total papers
    total_papers = len(runtime_paper_dict)
    
    # Build the message
    message_parts = [
        source_line,
        f"{total_papers} papers fetched",
        ""  # Empty line for spacing
    ]
    
    # Add topic-specific relevance counts
    for topic_name, topic_field in TOPICS.items():
        counts = count_papers_by_relevance(runtime_paper_dict, topic_field)
        
        message_parts.append(f"*{topic_name}*")
        message_parts.append(f"Highly relevant: {counts['Highly Relevant']}")
        message_parts.append(f"Moderately Relevant: {counts['Moderately Relevant']}")
        message_parts.append(f"Tangentially Relevant: {counts['Tangentially Relevant']}")
        message_parts.append("")  # Empty line for spacing
    
    return "\n".join(message_parts).strip()


def send_slack_message(message: str) -> bool:
    """
    Send a message to Slack using the webhook URL or bot token.
    
    Args:
        message: The message text to send
    
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('SLACK')
    
    # Get Slack configuration from environment
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    slack_channel_id = os.getenv('SLACK_CHANNEL_ID')
    
    if not slack_bot_token or not slack_channel_id:
        logger.error("Missing Slack configuration. Please set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID environment variables.")
        return False
    
    # Prepare the request
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        'Authorization': f'Bearer {slack_bot_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'channel': slack_channel_id,
        'text': message,
        'username': 'Paper Pipeline Bot',
        'icon_emoji': ':page_facing_up:'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        if response_data.get('ok'):
            logger.info("Successfully sent Slack notification")
            return True
        else:
            logger.error(f"Slack API error: {response_data.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Slack notification: {e}")
        return False


def run(runtime_paper_dict: Dict[str, Paper], run_mode: str, run_value: str) -> None:
    """
    Main entry point for the Slack notification module.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
        run_mode: 'date' or 'test' mode
        run_value: The date string or test file name
    """
    logger = logging.getLogger('SLACK')
    logger.info("Starting Slack notification")
    
    try:
        # Format the message
        message = format_slack_message(runtime_paper_dict, run_mode, run_value)
        
        # Send the notification
        success = send_slack_message(message)
        
        if success:
            logger.info("Slack notification sent successfully")
        else:
            logger.warning("Failed to send Slack notification")
            
    except Exception as e:
        logger.error(f"Error in Slack notification module: {e}")
        raise


if __name__ == "__main__":
    # This module is designed to be imported and used as part of the pipeline
    print("Slack notification module - designed to be used as part of the main pipeline")
    print("Run from the src directory: python main.py --date YYYY-MM-DD")
