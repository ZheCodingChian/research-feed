"""
Slack notification module for paper processing pipeline.

This module sends a summary of processed papers to a Slack channel,
including the total paper count and published date.
"""

import logging
import os
from typing import Dict, List
from datetime import datetime
import requests
from paper import Paper

logger = logging.getLogger('SLACK')


def format_message_blocks(runtime_paper_dict: Dict[str, Paper]) -> List[Dict]:
    """
    Format the Slack message using Block Kit.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
    
    Returns:
        List of Block Kit blocks for the message
    """
    # Get the published date from papers (assume all papers have the same published date)
    published_date = None
    if runtime_paper_dict:
        # Get published date from the first paper
        first_paper = next(iter(runtime_paper_dict.values()))
        published_date = first_paper.published_date
        formatted_published_date = published_date.strftime('%B %d, %Y')
    else:
        # Fallback if no papers
        formatted_published_date = "No date available"
    
    # Format the header - run date is always the current date
    current_date = datetime.now().strftime('%B %d, %Y')
    header_text = f"ResearchFeed Update | Run date: {current_date}"
    
    # Count total papers and recommendations
    total_papers = len(runtime_paper_dict)
    must_read_count = sum(1 for p in runtime_paper_dict.values() if p.recommendation_score == 'Must Read')
    should_read_count = sum(1 for p in runtime_paper_dict.values() if p.recommendation_score == 'Should Read')

    content_text = f"{total_papers} Papers Fetched | Published: {formatted_published_date}\nMust Read: {must_read_count} | Should Read: {should_read_count}"
    
    # Website URL
    website_url = "https://researchfeed.pages.dev"
    
    # Build the message blocks
    message_blocks = [
        {
            "type": "divider"
        },
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": content_text
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Papers"
                    },
                    "url": website_url
                }
            ]
        },
        {
            "type": "divider"
        }
    ]
    
    return message_blocks


def send_slack_message(runtime_paper_dict: Dict[str, Paper]) -> bool:
    """
    Send a message to Slack using the bot token.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
    
    Returns:
        True if message sent successfully, False otherwise
    """
    # Get Slack configuration from environment
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    slack_channel_id = os.getenv('SLACK_CHANNEL_ID')
    
    if not slack_bot_token or not slack_channel_id:
        logger.warning("Missing Slack configuration. Please set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID environment variables.")
        return False
    
    # Format the message
    message_blocks = format_message_blocks(runtime_paper_dict)
    
    # Prepare the request
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        'Authorization': f'Bearer {slack_bot_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'channel': slack_channel_id,
        'blocks': message_blocks,
        'username': 'ResearchFeed Bot',
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
            logger.warning(f"Slack API error: {response_data.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to send Slack notification: {e}")
        return False
    except Exception as e:
        logger.warning(f"Unexpected error sending Slack notification: {e}")
        return False


def run(runtime_paper_dict: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Main entry point for the Slack notification module.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
        config: Module configuration (unused - relies on environment variables)
    
    Returns:
        The unchanged runtime_paper_dict
    """
    logger.info("Starting Slack notification")
    
    try:
        success = send_slack_message(runtime_paper_dict)
        
        if success:
            logger.info("Slack notification sent successfully")
        else:
            logger.warning("Failed to send Slack notification")
            
    except Exception as e:
        logger.error(f"Error in Slack notification module: {e}")
        raise
    
    return runtime_paper_dict


if __name__ == "__main__":
    # This module is designed to be imported and used as part of the pipeline
    print("Slack notification module - designed to be used as part of the main pipeline")
    print("Run from the src directory: python main.py --date YYYY-MM-DD")