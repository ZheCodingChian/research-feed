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

# Topic URL parameters for filtering
TOPIC_URL_PARAMS = {
    'RLHF': 'sort=relevance-desc&topics=rlhf&relevance=highly%2Cmoderately%2Ctangentially',
    'Weak supervision': 'sort=relevance-desc&topics=weak_supervision&relevance=highly%2Cmoderately%2Ctangentially',
    'Diffusion Reasoning': 'sort=relevance-desc&topics=diffusion_reasoning&relevance=highly%2Cmoderately%2Ctangentially',
    'Distributed Training': 'sort=relevance-desc&topics=distributed_training&relevance=highly%2Cmoderately%2Ctangentially',
    'Datasets': 'sort=relevance-desc&topics=datasets&relevance=highly%2Cmoderately%2Ctangentially'
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


def format_main_slack_message(runtime_paper_dict: Dict[str, Paper], run_mode: str, run_value: str) -> List[Dict]:
    """
    Format the main Slack message (parent) with basic summary using Block Kit.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
        run_mode: 'date' or 'test' mode
        run_value: The date string or test file name
    
    Returns:
        List of Block Kit blocks for the main Slack message
    """
    # Get the published date from papers (assume all papers have the same published date)
    published_date = None
    if runtime_paper_dict:
        # Get published date from the first paper
        first_paper = next(iter(runtime_paper_dict.values()))
        published_date = first_paper.published_date
        published_date_str = published_date.strftime('%Y-%m-%d')
        formatted_published_date = published_date.strftime('%B %d, %Y')
        
        # Generate the newsletter URL based on published date
        newsletter_url = f"https://zhecodingchian.github.io/arXiv-Newsletter-Papers/{published_date_str}.html"
    else:
        # Fallback if no papers
        published_date_str = "2025-07-01"
        formatted_published_date = "July 1, 2025"
        newsletter_url = f"https://zhecodingchian.github.io/arXiv-Newsletter-Papers/{published_date_str}.html"
    
    # Format the header - run date is always the current date
    current_date = datetime.now().strftime('%B %d, %Y')
    if run_mode == 'date':
        header_text = f"arXiv Daily Newsletter | Run date: {current_date}"
    else:
        header_text = f"arXiv Daily Newsletter | Test run: {current_date}"
    
    # Count total papers
    total_papers = len(runtime_paper_dict)
    
    # Build the simple main message
    message_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*{total_papers}* Papers Fetched   |   Published: *{formatted_published_date}*"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Read papers"
                    },
                    "url": newsletter_url
                }
            ]
        }
    ]
    
    return message_blocks


def format_thread_message(runtime_paper_dict: Dict[str, Paper], run_mode: str, run_value: str) -> List[Dict]:
    """
    Format the single thread message with all detailed breakdowns.
    
    Args:
        runtime_paper_dict: Dictionary of paper_id -> Paper objects
        run_mode: 'date' or 'test' mode
        run_value: The date string or test file name
    
    Returns:
        List of Block Kit blocks for the single thread message
    """
    # Get the published date and newsletter URL
    if runtime_paper_dict:
        first_paper = next(iter(runtime_paper_dict.values()))
        published_date = first_paper.published_date
        published_date_str = published_date.strftime('%Y-%m-%d')
        newsletter_url = f"https://zhecodingchian.github.io/arXiv-Newsletter-Papers/{published_date_str}.html"
    else:
        published_date_str = "2025-07-01"
        newsletter_url = f"https://zhecodingchian.github.io/arXiv-Newsletter-Papers/{published_date_str}.html"
    
    # Count papers by their actual recommendation scores
    must_read_count = 0
    should_read_count = 0
    
    for paper in runtime_paper_dict.values():
        recommendation = paper.recommendation_score
        if recommendation == "Must Read":
            must_read_count += 1
        elif recommendation == "Should Read":
            should_read_count += 1
    
    # Build the combined thread message
    thread_blocks = [
        # Must Read section
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Must Read: {must_read_count} papers*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View papers"
                    },
                    "url": f"{newsletter_url}?status=completed&recommendation=must_read"
                }
            ]
        },
        {
            "type": "divider"
        },
        # Should Read section
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Should Read: {should_read_count} papers*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View papers"
                    },
                    "url": f"{newsletter_url}?status=completed&recommendation=should_read"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]
    
    # Add topic-specific sections
    for topic_name, topic_field in TOPICS.items():
        counts = count_papers_by_relevance(runtime_paper_dict, topic_field)
        total_topic_papers = sum(counts.values())
        
        # Get the URL parameters for this topic
        topic_url_params = TOPIC_URL_PARAMS.get(topic_name, '')
        topic_url = f"{newsletter_url}?{topic_url_params}" if topic_url_params else newsletter_url
        
        thread_blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{topic_name}: {total_topic_papers} papers*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Highly relevant: {counts['Highly Relevant']}   |   Moderately relevant: {counts['Moderately Relevant']}   |   Tangentially relevant: {counts['Tangentially Relevant']}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View papers"
                        },
                        "url": topic_url
                    }
                ]
            },
            {
                "type": "divider"
            }
        ])
    
    return thread_blocks


def send_slack_message(message_blocks: List[Dict], thread_ts: str = None) -> tuple[bool, str]:
    """
    Send a Block Kit message to Slack using the bot token.
    
    Args:
        message_blocks: List of Block Kit blocks to send
        thread_ts: Optional timestamp of parent message to reply to (for threading)
    
    Returns:
        Tuple of (success boolean, message timestamp or None)
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
        'blocks': message_blocks,
        'username': 'Paper Pipeline Bot',
        'icon_emoji': ':page_facing_up:'
    }
    
    # Add thread_ts if this is a reply
    if thread_ts:
        payload['thread_ts'] = thread_ts
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        if response_data.get('ok'):
            logger.info("Successfully sent Slack notification")
            message_ts = response_data.get('ts')
            return True, message_ts
        else:
            logger.error(f"Slack API error: {response_data.get('error', 'Unknown error')}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Unexpected error sending Slack notification: {e}")
        return False, None


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
        # Format the main message and thread message
        main_message_blocks = format_main_slack_message(runtime_paper_dict, run_mode, run_value)
        thread_message_blocks = format_thread_message(runtime_paper_dict, run_mode, run_value)
        
        # Send the main message first
        success, main_message_ts = send_slack_message(main_message_blocks)
        
        if success and main_message_ts:
            logger.info("Main Slack message sent successfully")
            
            # Send the single thread message
            thread_success, _ = send_slack_message(thread_message_blocks, thread_ts=main_message_ts)
            if thread_success:
                logger.info("Thread message sent successfully")
            else:
                logger.warning("Failed to send thread message")
            
            logger.info("All Slack notifications sent successfully")
        else:
            logger.warning("Failed to send main Slack message")
            
    except Exception as e:
        logger.error(f"Error in Slack notification module: {e}")
        raise


if __name__ == "__main__":
    # This module is designed to be imported and used as part of the pipeline
    print("Slack notification module - designed to be used as part of the main pipeline")
    print("Run from the src directory: python main.py --date YYYY-MM-DD")
