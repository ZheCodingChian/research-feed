"""
HTML Generator Module

Starting fresh with a clean implementation.
"""

import os
import logging
import re
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from paper import Paper

logger = logging.getLogger('HTML_GENERATOR')


class HTMLGenerator:
    """Clean implementation of HTML generator."""
    
    def __init__(self, config: dict):
        """Initialize the HTML generator."""
        self.config = config
        self.output_dir = config.get('output_dir', 'report')
        templates_dir = config.get('template_dir', 'templates')
        
        # Handle relative paths
        if not os.path.isabs(templates_dir):
            project_root = Path(__file__).parent.parent.parent
            self.templates_dir = str(project_root / templates_dir)
        else:
            self.templates_dir = templates_dir
            
        if not os.path.isabs(self.output_dir):
            project_root = Path(__file__).parent.parent.parent
            self.output_dir = str(project_root / self.output_dir)
        
        # Ensure directories exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.templates_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
    
    def generate_filename(self, run_mode: str, run_value: str) -> str:
        """Generate filename based on run mode and value."""
        if run_mode == 'date':
            # For date runs: "2025-01-15.html"
            return self.config['naming']['date_format'].format(date=run_value)
        else:  # test mode
            # For test runs: "test_papers.txt_2025-01-15_14-30.html"
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            # Extract just the filename without path for cleaner naming
            test_name = os.path.basename(run_value)
            return self.config['naming']['test_format'].format(
                test_name=test_name,
                timestamp=timestamp
            )
    
    def generate_title(self, run_mode: str, run_value: str) -> str:
        """Generate page title based on run mode and value."""
        if run_mode == 'date':
            return self.config['titles']['date_title'].format(date=run_value)
        else:  # test mode
            test_name = os.path.basename(run_value)
            return self.config['titles']['test_title'].format(test_name=test_name)
    
    def scan_existing_reports(self) -> List[dict]:
        """Scan the output directory for existing HTML reports."""
        reports = []
        
        if not os.path.exists(self.output_dir):
            return reports
        
        try:
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.html') and filename != 'index.html':
                    file_path = os.path.join(self.output_dir, filename)
                    paper_count = self._extract_paper_count(file_path)
                    
                    # Determine run type and create report data
                    if filename.startswith('test_'):
                        # Test run
                        # Parse: test_papers.txt_2025-01-15_14-30.html
                        parts = filename.replace('test_', '').replace('.html', '').split('_')
                        if len(parts) >= 3:
                            test_name = parts[0]
                            date_time = '_'.join(parts[-2:])  # Last two parts are date_time
                            title = f"Test Run: {test_name}"
                            subtitle = f"Run on {date_time.replace('_', ' ')}"
                        else:
                            title = "Test Run"
                            subtitle = "Experimental Run"
                        
                        reports.append({
                            'filename': filename,
                            'title': title,
                            'subtitle': subtitle,
                            'paper_count': paper_count,
                            'run_type': 'test',
                            'sort_key': filename  # Use filename for sorting test runs
                        })
                    else:
                        # Normal date run
                        # Parse: 2025-01-15.html
                        date_str = filename.replace('.html', '')
                        try:
                            # Validate date format
                            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                            title = f"Papers from {date_str}"
                            subtitle = parsed_date.strftime('%A, %B %d, %Y')
                            
                            reports.append({
                                'filename': filename,
                                'title': title,
                                'subtitle': subtitle,
                                'paper_count': paper_count,
                                'run_type': 'normal',
                                'sort_key': date_str
                            })
                        except ValueError:
                            # Invalid date format, skip
                            logger.warning(f"Skipping file with invalid date format: {filename}")
                            continue
            
            # Sort reports: normal date runs first (newest first), then test runs (newest first)
            normal_reports = [r for r in reports if r['run_type'] == 'normal']
            test_reports = [r for r in reports if r['run_type'] == 'test']
            
            normal_reports.sort(key=lambda x: x['sort_key'], reverse=True)
            test_reports.sort(key=lambda x: x['sort_key'], reverse=True)
            
            return normal_reports + test_reports
            
        except Exception as e:
            logger.error(f"Error scanning reports: {e}")
            return []
    
    def _extract_paper_count(self, html_file_path: str) -> int:
        """Extract paper count from HTML file."""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for various patterns that might indicate paper count
                patterns = [
                    r'(\d+)\s+papers?',
                    r'paper_count["\']?\s*:\s*(\d+)',
                    r'<.*?paper-count.*?>(\d+)<'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
                
                return 0
        except Exception as e:
            logger.warning(f"Could not extract paper count from {html_file_path}: {e}")
            return 0
    
    def generate_landing_page(self) -> str:
        """Generate the landing page index.html."""
        try:
            # Scan for existing reports
            reports = self.scan_existing_reports()
            
            # Prepare template data
            template_data = {
                'reports': reports,
                'current_year': datetime.now().year
            }
            
            # Load and render template
            template = self.env.get_template('landing.html')
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
            
    def generate_papers_page(self, papers_dict: Dict[str, Paper], run_mode: str, run_value: str) -> str:
        """Generate the papers analysis page."""
        try:
            # Filter papers to only include successfully scraped ones
            papers_list = []
            for paper in papers_dict.values():
                if paper.is_successfully_scraped():
                    # Calculate highest similarity score and topic
                    scores = {}
                    if paper.rlhf_score is not None:
                        scores['RLHF'] = paper.rlhf_score
                    if paper.weak_supervision_score is not None:
                        scores['Weak_supervision'] = paper.weak_supervision_score
                    if paper.diffusion_reasoning_score is not None:
                        scores['Diffusion_reasoning'] = paper.diffusion_reasoning_score
                    if paper.distributed_training_score is not None:
                        scores['Distributed_training'] = paper.distributed_training_score
                    
                    if scores:
                        highest_topic = max(scores, key=scores.get)
                        highest_score = scores[highest_topic]
                        paper.highest_similarity_topic = highest_topic
                        paper.highest_score = highest_score
                    
                    papers_list.append(paper)
            
            # Sort papers by recommendation score, then similarity, then h-index
            def get_sort_key(paper):
                # Primary: Recommendation score priority
                rec_score = paper.recommendation_score or ''
                rec_priority = {
                    'Must Read': 4, 
                    'Should Read': 3, 
                    'Can Skip': 2, 
                    'Ignore': 1
                }.get(rec_score, 0)
                
                # Secondary: Highest similarity score
                similarity_score = getattr(paper, 'highest_score', 0) or 0
                
                # Tertiary: H-index
                h_index = paper.highest_h_index or 0
                
                return (rec_priority, similarity_score, h_index)
            
            papers_list.sort(key=get_sort_key, reverse=True)
            
            # Generate filename and title
            filename = self.generate_filename(run_mode, run_value)
            page_title = self.generate_title(run_mode, run_value)
            
            # Prepare template data
            template_data = {
                'papers': papers_list,
                'paper_count': len(papers_list),
                'page_title': page_title,
                'run_mode': run_mode,
                'run_value': run_value
            }
            
            # Load and render template
            template = self.env.get_template('papers.html')
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
    logger.info(f"Run mode: {run_mode}, Run value: {run_value}")
    
    try:
        # Initialize HTML generator
        generator = HTMLGenerator(config)
        
        # Generate individual papers page
        papers_file = generator.generate_papers_page(papers, run_mode, run_value)
        
        # Generate/update landing page
        landing_file = generator.generate_landing_page()
        
        logger.info(f"HTML generation complete: {papers_file}, {landing_file}")
        
    except Exception as e:
        logger.error(f"HTML generation failed: {e}")
        raise
    
    return papers
