import os
import xml.etree.ElementTree as ET
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
import html

class HTMLGenerator:
    """Generator for HTML reports from paper data."""
    
    def __init__(self, config):
        """Initialize the HTML generator with config."""
        self.config = config
        self.template_dir = config.template_dir
        self.output_dir = config.html_dir

        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.max_files = 7  # Maximum number of HTML files to keep (7 days)
        self.papers_per_page = 20  # Number of papers per page
    
    def _extract_paper_count_from_html(self, html_file_path):
        """Extract paper count from HTML file."""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for the stats element with id="paper-count"
                stats_element = soup.find(id='paper-count')
                if stats_element:
                    stats_text = stats_element.get_text().strip()
                    # Parse number
                    match = re.search(r'(\d+)', stats_text)
                    if match:
                        return int(match.group(1))
                
                logging.warning(f"Could not extract paper count from {html_file_path}")
                return 0
                
        except Exception as e:
            logging.error(f"Error extracting paper count from {html_file_path}: {e}")
            return 0

    def _get_available_date_reports(self):
        """Get list of available date reports by scanning HTML files in the output directory."""
        date_reports = []
        date_files = {}
        test_files = []
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            logging.warning(f"Output directory {self.output_dir} does not exist")
            return date_reports
        
        # Scan all HTML files in the output directory
        try:
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.html') and filename != 'index.html':
                    file_path = os.path.join(self.output_dir, filename)
                    count = self._extract_paper_count_from_html(file_path)
                    
                    # Check if it's a test file
                    if filename.startswith('test_'):
                        test_files.append({
                            'filename': filename,
                            'display_name': f"Test Run ({filename.replace('test_', '').replace('.html', '').replace('_', ' ')})",
                            'count': count,
                            'is_test': True
                        })
                    else:
                        # Extract date from filename (e.g., "2025-06-12.html")
                        base_name = filename.replace('.html', '')
                        if base_name.count('-') == 2:
                            # Validate date format (YYYY-MM-DD)
                            try:
                                datetime.strptime(base_name, '%Y-%m-%d')
                                
                                date_files[base_name] = {
                                    'filename': filename,
                                    'count': count,
                                    'is_test': False
                                }
                                            
                            except ValueError:
                                # Invalid date format, treat as test file
                                test_files.append({
                                    'filename': filename,
                                    'display_name': f"Other ({base_name})",
                                    'count': count,
                                    'is_test': True
                                })
            
            # Convert regular date files to the expected format and sort by date (newest first)
            for date_str in sorted(date_files.keys(), reverse=True):
                data = date_files[date_str]
                
                report = {
                    'date': date_str,
                    'filename': data['filename'],
                    'count': data['count'],
                    'is_test': False
                }
                
                date_reports.append(report)
            
            # Add test files at the end, sorted by filename
            for test_file in sorted(test_files, key=lambda x: x['filename'], reverse=True):
                date_reports.append({
                    'date': test_file['display_name'],
                    'filename': test_file['filename'],
                    'count': test_file['count'],
                    'is_test': True
                })
                    
        except Exception as e:
            logging.error(f"Error scanning HTML files in {self.output_dir}: {e}")
        
        regular_count = len(date_files)
        test_count = len(test_files)
        logging.info(f"Found {regular_count} regular reports and {test_count} test reports")
        
        return date_reports

    def generate_landing_page(self):
        """Generate the main landing page index.html."""
        try:
            # Get available date reports
            date_reports = self._get_available_date_reports()
            
            # Prepare template data
            template_data = {
                'date_reports': date_reports,
                'current_year': datetime.now().year
            }
            
            # Load and render template
            template = self.env.get_template('landing_page_template.html')
            html_content = template.render(**template_data)
            
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Save landing page as index.html
            index_file = os.path.join(self.output_dir, 'index.html')
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"Generated landing page: {index_file} with {len(date_reports)} date reports")
            
            return index_file
            
        except Exception as e:
            logging.error(f"Error generating landing page: {e}")
            raise

    def _cleanup_old_files(self):
        """Remove oldest files if we have more than max_files."""
        try:
            # Get all HTML files except index.html and sort by modification time
            html_files = []
            for file in os.listdir(self.output_dir):
                if file.endswith('.html') and file != 'index.html':
                    file_path = os.path.join(self.output_dir, file)
                    html_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (oldest first)
            html_files.sort(key=lambda x: x[1])
            
            # Remove oldest files if we have more than max_files
            while len(html_files) >= self.max_files:
                oldest_file = html_files.pop(0)[0]
                try:
                    os.remove(oldest_file)
                    logging.info(f"Removed old file: {oldest_file}")
                except Exception as e:
                    logging.error(f"Error removing old file {oldest_file}: {e}")
        except Exception as e:
            logging.error(f"Error during file cleanup: {e}")

    def generate_papers_report(self, papers, date_str, is_test_mode=False):
        """Generate HTML report from paper data with sorting and filtering capabilities.
        
        Args:
            papers: List of paper dictionaries with similarity scores
            date_str: Date string for the report (or test identifier)
            is_test_mode: Whether this is a test mode report
        """
        try:
            # Sort papers with priority: overall_priority > highest_score > h_index
            def get_sort_key(paper):
                # Primary: Overall priority score (0 if not available)
                overall_priority = paper.get('scores_data', {}).get('overall_priority', 0)
                # Ensure it's a float
                try:
                    overall_priority = float(overall_priority) if overall_priority else 0
                except (ValueError, TypeError):
                    overall_priority = 0
                
                # Secondary: Similarity score
                similarity_score = paper.get('highest_score', 0)
                try:
                    similarity_score = float(similarity_score) if similarity_score else 0
                except (ValueError, TypeError):
                    similarity_score = 0
                
                # Tertiary: H-index
                h_indices = paper.get('author_h_indices', {})
                h_index = 0
                if isinstance(h_indices, dict):
                    h_index = h_indices.get('highest_h_index') or 0
                    if h_index is None:
                        h_index = 0
                    try:
                        h_index = float(h_index) if h_index else 0
                    except (ValueError, TypeError):
                        h_index = 0
                
                return (overall_priority, similarity_score, h_index)
            
            sorted_papers = sorted(papers, key=get_sort_key, reverse=True)
            
            # Transform data for template
            for paper in sorted_papers:
                # Escape HTML entities for security while preserving LaTeX math delimiters
                paper['title'] = html.escape(paper.get('title', ''))
                paper['abstract'] = html.escape(paper.get('abstract', ''))
            
            # Get research topics from config
            topics = ['RLHF', 'Weak_supervision', 'Diffusion_reasoning', 'Distributed_training']
            
            # Extract model information from papers (should be consistent across all papers)
            embedding_model = "unknown"
            llm_model = "unknown"
            scoring_model = "unknown"
            
            if sorted_papers:
                # Try to get model info from cache or paper data
                first_paper = sorted_papers[0]
                embedding_model = first_paper.get('embedding_model', 'unknown')
                
                # Check if we have LLM validation data to infer LLM model
                llm_validation = first_paper.get('llm_validation', {})
                if llm_validation:
                    # LLM validation exists, so we can infer LLM model from config
                    llm_model = self.config.llm_model if hasattr(self.config, 'llm_model') else 'unknown'
                
                # Check if we have scoring data to infer scoring model
                scores_data = first_paper.get('scores_data', {})
                if scores_data and scores_data.get('overall_priority', 0) > 0:
                    # Scoring exists, get scoring model from config
                    scoring_model = getattr(self.config, 'scoring_model_name', 'unknown')
                
                # Validate model consistency across papers
                for paper in sorted_papers[:5]:  # Check first 5 papers for consistency
                    paper_embedding_model = paper.get('embedding_model', 'unknown')
                    if paper_embedding_model != embedding_model and paper_embedding_model != 'unknown':
                        raise ValueError(f"Inconsistent embedding models detected: {embedding_model} vs {paper_embedding_model}")
            
            # Determine display title and metadata based on mode
            if is_test_mode:
                display_title = "Test Papers"
                display_date = f"Test Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                # For test mode, collect actual publication dates from papers
                paper_dates = set()
                for paper in sorted_papers:
                    if 'published' in paper:
                        try:
                            pub_date = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
                            paper_dates.add(pub_date.strftime('%Y-%m-%d'))
                        except:
                            pass
                if paper_dates:
                    date_range_info = f"Paper dates: {', '.join(sorted(paper_dates))}"
                else:
                    date_range_info = "Various dates"
            else:
                display_title = f"Papers - {date_str}"
                display_date = date_str
                date_range_info = f"Submitted on {date_str}"
            
            # Prepare template data
            template_data = {
                'papers': sorted_papers,
                'date': date_str,
                'display_title': display_title,
                'display_date': display_date,
                'date_range_info': date_range_info,
                'paper_count': len(sorted_papers),
                'topics': topics,
                'current_year': datetime.now().year,
                'is_test_mode': is_test_mode,
                'embedding_model': embedding_model,
                'llm_model': llm_model,
                'scoring_model': scoring_model,
                'models_used': {
                    'embedding': embedding_model,
                    'llm': llm_model,
                    'scoring': scoring_model
                }
            }
            
            # Load and render template
            template = self.env.get_template('papers_template.html')
            html_content = template.render(**template_data)
            
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Save report
            output_file = os.path.join(self.output_dir, f'{date_str}.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"Generated papers report: {output_file} with {len(sorted_papers)} papers")
            
            # Only clean up old files in regular mode (not test mode)
            if not is_test_mode:
                self._cleanup_old_files()
            
            return output_file
            
        except Exception as e:
            logging.error(f"Error generating papers report: {e}")
            raise





 