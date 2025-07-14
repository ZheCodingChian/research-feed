"""
HTML Generator Module

This module generates HTML reports from processed paper data. It creates both
landing pages and detailed paper analysis pages using Jinja2 templates.
"""

import os
import logging
import html
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from paper import Paper

logger = logging.getLogger('HTML_GENERATOR')

class HTMLGenerator:
    """Generator for HTML reports from paper data."""
    
    def __init__(self, config: dict):
        """Initialize the HTML generator with configuration."""
        self.config = config
        self.output_dir = config.get('output_dir', 'report')
        templates_dir = config.get('template_dir', 'templates')
        
        # Handle relative paths - templates should be relative to project root
        if not os.path.isabs(templates_dir):
            # Get project root (parent of src directory)
            project_root = Path(__file__).parent.parent.parent
            self.templates_dir = str(project_root / templates_dir)
        else:
            self.templates_dir = templates_dir
            
        if not os.path.isabs(self.output_dir):
            # Get project root (parent of src directory)  
            project_root = Path(__file__).parent.parent.parent
            self.output_dir = str(project_root / self.output_dir)
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        
        # Research topics from your system
        self.topics = ['RLHF', 'Weak_supervision', 'Diffusion_reasoning', 'Distributed_training']
    
    def generate_filename(self, run_mode: str, run_value: str) -> str:
        """Generate HTML filename based on run mode and value."""
        if run_mode == 'date':
            return f"{run_value}.html"
        else:  # test mode
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            return f"test_{timestamp}.html"
    
    def transform_paper_data(self, paper: Paper) -> dict:
        """Transform Paper object to template-compatible dictionary."""
        # Get similarity scores
        scores = {}
        if paper.rlhf_score is not None:
            scores['RLHF'] = paper.rlhf_score
        if paper.weak_supervision_score is not None:
            scores['Weak_supervision'] = paper.weak_supervision_score
        if paper.diffusion_reasoning_score is not None:
            scores['Diffusion_reasoning'] = paper.diffusion_reasoning_score
        if paper.distributed_training_score is not None:
            scores['Distributed_training'] = paper.distributed_training_score
        
        # Get highest scoring topic
        highest_score = 0
        highest_topic = None
        if scores:
            highest_topic = max(scores, key=scores.get)
            highest_score = scores[highest_topic]
        
        # Transform LLM validation data
        llm_validation = {}
        if paper.llm_validation_status == "completed":
            for topic in self.topics:
                topic_key = topic.lower().replace('_', '_')
                validation_data = {
                    'validated': True,
                    'llm_relevant': 'unknown',
                    'justification': 'No justification available'
                }
                
                # Map topic to paper fields
                if topic == 'RLHF':
                    validation_data['llm_relevant'] = paper.rlhf_relevance
                    validation_data['justification'] = paper.rlhf_justification
                elif topic == 'Weak_supervision':
                    validation_data['llm_relevant'] = paper.weak_supervision_relevance
                    validation_data['justification'] = paper.weak_supervision_justification
                elif topic == 'Diffusion_reasoning':
                    validation_data['llm_relevant'] = paper.diffusion_reasoning_relevance
                    validation_data['justification'] = paper.diffusion_reasoning_justification
                elif topic == 'Distributed_training':
                    validation_data['llm_relevant'] = paper.distributed_training_relevance
                    validation_data['justification'] = paper.distributed_training_justification
                
                llm_validation[topic] = validation_data
        
        # Transform LLM scoring data
        scores_data = {}
        if paper.llm_score_status == "completed":
            scores_data = {
                'recommendation': paper.recommendation_score,
                'recommendation_justification': paper.recommendation_justification,
                'novelty': paper.novelty_score,
                'novelty_justification': paper.novelty_justification,
                'impact': paper.impact_score,
                'impact_justification': paper.impact_justification,
                'summary': paper.summary
            }
        
        # Transform H-index data
        author_h_indices = {}
        if paper.h_index_status == "completed":
            author_h_indices = {
                'success': True,
                'total_authors': paper.total_authors or 0,
                'authors_with_h_index_count': paper.authors_found or 0,
                'highest_h_index': paper.highest_h_index,
                'average_h_index': paper.average_h_index,
                'notable_authors_count': paper.notable_authors_count or 0,
                'h_index_fetch_method': paper.h_index_fetch_method,
                'author_h_indexes': []
            }
            
            # Add individual author data if available
            if hasattr(paper, 'author_h_indexes') and paper.author_h_indexes:
                for author in paper.author_h_indexes:
                    author_data = {
                        'name': getattr(author, 'name', 'Unknown'),
                        'h_index': getattr(author, 'h_index', None),
                        'semantic_scholar_url': getattr(author, 'semantic_scholar_url', None)
                    }
                    author_h_indices['author_h_indexes'].append(author_data)
        else:
            author_h_indices = {
                'success': False,
                'total_authors': 0,
                'authors_with_h_index_count': 0,
                'highest_h_index': None,
                'average_h_index': None,
                'notable_authors_count': 0
            }
        
        return {
            'id': paper.id,
            'title': html.escape(paper.title or ''),
            'arxiv_id': paper.id,  # Use id for arxiv_id
            'arxiv_url': f"http://arxiv.org/abs/{paper.id}" if paper.id else "#",
            'abstract': html.escape(paper.abstract or ''),
            'authors': paper.authors or [],
            'published': paper.published_date.isoformat() if paper.published_date else None,  # Convert to string
            'categories': paper.categories or [],
            'scores': scores,
            'highest_score': highest_score,
            'highest_similarity_topic': highest_topic,
            'llm_validation': llm_validation,
            'scores_data': scores_data,
            'author_h_indices': author_h_indices,
            # Processing status flags
            'embedding_completed': paper.is_embedding_completed(),
            'llm_validation_completed': paper.is_llm_validation_completed(),
            'llm_scoring_completed': paper.is_llm_score_completed(),
            'h_index_completed': paper.is_h_index_completed()
        }
    
    def get_paper_count_from_html(self, html_file_path: str) -> int:
        """Extract paper count from existing HTML file."""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for paper count in the content
                import re
                match = re.search(r'(\d+)\s+papers?', content, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            return 0
        except Exception as e:
            logger.warning(f"Could not extract paper count from {html_file_path}: {e}")
            return 0
    
    def get_available_reports(self) -> List[dict]:
        """Get list of available reports by scanning HTML files."""
        reports = []
        
        if not os.path.exists(self.output_dir):
            return reports
        
        try:
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.html') and filename != 'index.html':
                    file_path = os.path.join(self.output_dir, filename)
                    count = self.get_paper_count_from_html(file_path)
                    
                    # Determine if it's a test file
                    if filename.startswith('test_'):
                        display_name = filename.replace('test_', '').replace('.html', '').replace('_', ' ')
                        reports.append({
                            'filename': filename,
                            'display_name': f"Test Run ({display_name})",
                            'paper_count': count,
                            'is_test': True,
                            'date': display_name
                        })
                    else:
                        # Regular date file
                        date_str = filename.replace('.html', '')
                        try:
                            # Validate date format
                            datetime.strptime(date_str, '%Y-%m-%d')
                            reports.append({
                                'filename': filename,
                                'display_name': date_str,
                                'paper_count': count,
                                'is_test': False,
                                'date': date_str
                            })
                        except ValueError:
                            # Invalid date format, treat as test
                            reports.append({
                                'filename': filename,
                                'display_name': f"Other ({date_str})",
                                'paper_count': count,
                                'is_test': True,
                                'date': date_str
                            })
            
            # Sort reports: regular dates first (newest first), then test files
            regular_reports = [r for r in reports if not r['is_test']]
            test_reports = [r for r in reports if r['is_test']]
            
            regular_reports.sort(key=lambda x: x['date'], reverse=True)
            test_reports.sort(key=lambda x: x['filename'], reverse=True)
            
            return regular_reports + test_reports
            
        except Exception as e:
            logger.error(f"Error scanning HTML files: {e}")
            return []
    
    def generate_papers_page(self, papers_dict: Dict[str, Paper], run_mode: str, run_value: str) -> str:
        """Generate the main papers analysis page."""
        try:
            # Transform papers to template format
            papers_list = []
            for paper in papers_dict.values():
                if paper.is_successfully_scraped():  # Only include successfully scraped papers
                    papers_list.append(self.transform_paper_data(paper))
            
            # Sort papers by overall priority score, then similarity, then h-index
            def get_sort_key(paper_data):
                # Primary: Recommendation score priority
                rec_score = paper_data.get('scores_data', {}).get('recommendation', '')
                rec_priority = {'Must Read': 4, 'Should Read': 3, 'Can Skip': 2, 'Ignore': 1}.get(rec_score, 0)
                
                # Secondary: Highest similarity score
                similarity_score = paper_data.get('highest_score', 0) or 0
                
                # Tertiary: H-index
                h_index = paper_data.get('author_h_indices', {}).get('highest_h_index') or 0
                
                return (rec_priority, similarity_score, h_index)
            
            papers_list.sort(key=get_sort_key, reverse=True)
            
            # Generate filename
            filename = self.generate_filename(run_mode, run_value)
            
            # Determine display information
            if run_mode == 'test':
                display_title = "Test Papers"
                display_mode = "Test Mode - Specific Papers Analysis"
                # Extract unique publication dates from papers
                paper_dates = set()
                for paper_data in papers_list:
                    if paper_data.get('published'):
                        try:
                            # published_date is already a datetime object
                            pub_date = paper_data['published']
                            if hasattr(pub_date, 'strftime'):
                                paper_dates.add(pub_date.strftime('%Y-%m-%d'))
                            else:
                                # If it's a string, try to parse it
                                pub_date = datetime.fromisoformat(str(pub_date).replace('Z', '+00:00'))
                                paper_dates.add(pub_date.strftime('%Y-%m-%d'))
                        except:
                            pass
                date_info = f"Paper dates: {', '.join(sorted(paper_dates))}" if paper_dates else "Various dates"
            else:
                display_title = f"Papers - {run_value}"
                display_mode = "Daily Report"
                date_info = f"Submitted on {run_value}"
            
            # Extract model information (should be consistent across papers)
            models_info = {
                'embedding': 'unknown',
                'llm_validation': 'unknown', 
                'llm_scoring': 'unknown'
            }
            
            if papers_list:
                # Try to extract model info from config or first paper
                models_info['embedding'] = self.config.get('embedding_model', 'openai-large')
                models_info['llm_validation'] = self.config.get('llm_model', 'x-ai/grok-3-mini')
                models_info['llm_scoring'] = self.config.get('scoring_model', 'gemini-flash')
            
            # Prepare template data
            template_data = {
                'papers': papers_list,
                'paper_count': len(papers_list),
                'display_title': display_title,
                'display_mode': display_mode,
                'date_info': date_info,
                'filename': filename,
                'topics': self.topics,
                'models_info': models_info,
                'is_test_mode': run_mode == 'test',
                'current_year': datetime.now().year
            }
            
            # Load and render template
            template = self.env.get_template('papers_template.html')
            html_content = template.render(**template_data)
            
            # Save file
            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated papers page: {output_path} with {len(papers_list)} papers")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating papers page: {e}")
            raise
    
    def generate_landing_page(self) -> str:
        """Generate or update the landing page index.html."""
        try:
            # Get available reports
            reports = self.get_available_reports()
            
            # Prepare template data
            template_data = {
                'reports': reports,
                'current_year': datetime.now().year,
                'total_reports': len(reports)
            }
            
            # Load and render template
            template = self.env.get_template('landing_template.html')
            html_content = template.render(**template_data)
            
            # Save landing page
            index_path = os.path.join(self.output_dir, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated landing page: {index_path} with {len(reports)} reports")
            return index_path
            
        except Exception as e:
            logger.error(f"Error generating landing page: {e}")
            raise


def run(papers: Dict[str, Paper], run_mode: str, run_value: str, config: dict) -> Dict[str, Paper]:
    """
    Run HTML generation for the processed papers.
    
    Args:
        papers: Dictionary of paper_id -> Paper objects
        run_mode: 'date' or 'test'
        run_value: Date string or test file name
        config: HTML generation configuration
        
    Returns:
        The unchanged papers dictionary
    """
    logger.info(f"Starting HTML generation for {len(papers)} papers")
    
    try:
        # Initialize HTML generator
        generator = HTMLGenerator(config)
        
        # Generate papers page
        papers_file = generator.generate_papers_page(papers, run_mode, run_value)
        
        # Generate/update landing page
        landing_file = generator.generate_landing_page()
        
        logger.info(f"HTML generation complete: {papers_file}, {landing_file}")
        
    except Exception as e:
        logger.error(f"HTML generation failed: {e}")
        raise
    
    return papers
