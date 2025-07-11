"""
Introduction Extraction Module

This module handles the extraction of paper introductions from LaTeX source files.
It implements a hierarchical approach to find and extract introductions.
"""

import logging
import re
import tempfile
import time
import random
import requests
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Optional
from paper import Paper

logger = logging.getLogger('INTRO_EXTRACTOR')

# We now use a more elegant semantic approach to find introduction sections
# instead of exhaustive pattern matching

def clean_latex_markup(text: str) -> str:
    """Clean LaTeX markup from extracted text while preserving meaningful content."""
    if not text:
        return text
        
    # Step 1: Protect escaped percent signs
    text = re.sub(r'\\%', '<!ESCAPED_PERCENT!>', text)
    
    # Step 2: Remove LaTeX comments
    text = re.sub(r'%.*?\n', '\n', text)
    
    # Step 3: Restore escaped percent signs
    text = re.sub(r'<!ESCAPED_PERCENT!>', '%', text)
    
    # Step 4: Remove citations and references
    text = re.sub(r'\\cite\{[^}]*\}', '', text)
    text = re.sub(r'\\ref\{[^}]*\}', '', text)
    text = re.sub(r'\\label\{[^}]*\}', '', text)
    
    # Step 5: Preserve content of formatting commands
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    
    # Step 6: Handle line breaks and spacing
    text = re.sub(r'\\newline\b', '\n', text)
    text = re.sub(r'\\\\', '\n', text)
    text = re.sub(r'\\noindent\b', '', text)
    text = re.sub(r'\\indent\b', '', text)
    
    # Step 7: Remove section commands but keep content
    text = re.sub(r'\\(sub)*section\*?\{([^}]*)\}', r'\2', text)
    
    # Step 8: Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' \n', '\n', text)
    
    # Step 9: Remove any remaining LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    
    return text.strip()

def is_latex_file(content: str) -> bool:
    """
    Determine if a file is a LaTeX source file by checking for common LaTeX structures.
    
    Args:
        content: The content of the file to check
        
    Returns:
        True if this appears to be a LaTeX file, False otherwise
    """
    # Look for common LaTeX document structures and commands
    latex_indicators = [
        r'\\document(class|style)',
        r'\\begin\{document\}',
        r'\\end\{document\}',
        r'\\section',
        r'\\chapter',
        r'\\title',
        r'\\author',
        r'\\maketitle',
        r'\\usepackage'
    ]
    
    # Check for at least two indicators to confirm it's a LaTeX file
    indicators_found = 0
    for indicator in latex_indicators:
        if re.search(indicator, content):
            indicators_found += 1
            if indicators_found >= 2:  # Requiring at least 2 indicators for higher confidence
                return True
    
    return False


def is_introduction_content(content: str) -> bool:
    """
    Verify if content appears to be introduction text by checking for LaTeX formatting
    and academic writing indicators.
    
    Args:
        content: The content to verify
        
    Returns:
        True if this appears to be introduction content, False otherwise
    """
    if not content or len(content.strip()) < 100:
        return False
    
    # Look for LaTeX formatting indicators
    latex_indicators = [
        r'\\cite\{',           # Citations
        r'\\ref\{',            # References
        r'\\label\{',          # Labels
        r'\\textbf\{',         # Bold text
        r'\\textit\{',         # Italic text
        r'\\emph\{',           # Emphasized text
        r'\\begin\{',          # Environment begins
        r'\\end\{',            # Environment ends
        r'~\\cite\{',          # Citation with non-breaking space
        r'\\footnote',         # Footnotes
        r'\\caption',          # Captions
    ]
    
    # Count LaTeX indicators present
    latex_count = 0
    for indicator in latex_indicators:
        if re.search(indicator, content):
            latex_count += 1
    
    # Look for academic writing patterns
    academic_patterns = [
        r'\b(research|study|investigation|analysis|approach|method|framework)\b',
        r'\b(propose|present|introduce|demonstrate|show|prove)\b',
        r'\b(however|moreover|furthermore|nevertheless|therefore)\b',
        r'\b(recent|previous|prior|existing|current)\s+(work|research|studies)\b',
        r'\b(contribution|novel|significant|important)\b'
    ]
    
    # Count academic patterns present
    academic_count = 0
    content_lower = content.lower()
    for pattern in academic_patterns:
        if re.search(pattern, content_lower):
            academic_count += 1
    
    # Content is likely introduction if it has:
    # - At least 2 LaTeX indicators OR
    # - At least 3 academic writing patterns OR
    # - At least 1 LaTeX indicator AND 2 academic patterns
    return (latex_count >= 2 or 
            academic_count >= 3 or 
            (latex_count >= 1 and academic_count >= 2))


def is_introduction_section(section_title: str) -> bool:
    """
    Check if a section title represents an introduction section.
    This checks for any form of the word 'introduction' after removing formatting commands.
    
    Args:
        section_title: The text inside \section{...} or \section*{...}
        
    Returns:
        True if this appears to be an introduction section, False otherwise
    """
    # Remove LaTeX formatting commands like \textbf{}, \emph{}, etc.
    # This regex matches commands with their arguments and replaces them with just the content
    clean_title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', section_title)
    
    # Case-insensitive check for "introduction" or "intro" in the cleaned title
    return bool(re.search(r'intro(duction)?', clean_title, re.IGNORECASE))

def extract_introduction(tex_content: str) -> Optional[tuple[str, str]]:
    """
    Extract introduction from LaTeX content using a semantic approach.
    Returns (extracted_text, method_used) or None if no introduction found.
    """
    # Match any \section or \section* command and capture its title
    section_pattern = r'\\section\*?\{([^}]+)\}'
    
    # Find all section commands in the document
    sections = re.finditer(section_pattern, tex_content)
    
    for section_match in sections:
        section_title = section_match.group(1)
        
        # Check if this is an introduction section
        if is_introduction_section(section_title):
            # Get the position where this section starts
            section_start = section_match.end()
            
            # Try to find the next section to determine where this section ends
            next_section = re.search(r'\\section', tex_content[section_start:], re.DOTALL)
            
            if next_section:
                # Extract content until the next section
                content = tex_content[section_start:section_start + next_section.start()]
                content = clean_latex_markup(content)
                if len(content) >= 100:  # Basic length validation
                    return content, "section_boundary"
            else:
                # No next section found, extract until end of document
                content = tex_content[section_start:]
                # Remove common trailing sections
                content = re.sub(r'\\bibliography\{.*?\}.*', '', content, flags=re.DOTALL)
                content = re.sub(r'\\appendix.*', '', content, flags=re.DOTALL)
                content = re.sub(r'\\end\{document\}.*', '', content, flags=re.DOTALL)
                content = clean_latex_markup(content)
                if len(content) >= 100:
                    return content, "document_end"

    # Also try chapter-level introductions
    chapter_pattern = r'\\chapter\*?\{([^}]+)\}'
    chapters = re.finditer(chapter_pattern, tex_content)
    
    for chapter_match in chapters:
        chapter_title = chapter_match.group(1)
        
        # Check if this is an introduction chapter
        if is_introduction_section(chapter_title):
            # Get the position where this chapter starts
            chapter_start = chapter_match.end()
            
            # Try to find the next chapter or section to determine where this chapter ends
            next_heading = re.search(r'\\(chapter|section)', tex_content[chapter_start:], re.DOTALL)
            
            if next_heading:
                # Extract content until the next heading
                content = tex_content[chapter_start:chapter_start + next_heading.start()]
                content = clean_latex_markup(content)
                if len(content) >= 100:  # Basic length validation
                    return content, "chapter_boundary"
            else:
                # No next heading found, extract until end of document
                content = tex_content[chapter_start:]
                # Remove common trailing sections
                content = re.sub(r'\\bibliography\{.*?\}.*', '', content, flags=re.DOTALL)
                content = re.sub(r'\\appendix.*', '', content, flags=re.DOTALL)
                content = re.sub(r'\\end\{document\}.*', '', content, flags=re.DOTALL)
                content = clean_latex_markup(content)
                if len(content) >= 100:
                    return content, "chapter_end"
    
    # Check for custom introduction commands
    intro_cmd_patterns = [
        r'\\introduction\{([^}]+)\}',
        r'\\Introduction\{([^}]+)\}',
        r'\\INTRODUCTION\{([^}]+)\}'
    ]
    
    for pattern in intro_cmd_patterns:
        match = re.search(pattern + r'(.*?)\\(section|chapter)', tex_content, re.DOTALL)
        if match:
            content = match.group(2)
            content = clean_latex_markup(content)
            if len(content) >= 100:  # Basic length validation
                return content, "custom_intro_command"
            
        # Also try until end of document
        match = re.search(pattern + r'(.*)', tex_content, re.DOTALL)
        if match:
            content = match.group(2)
            # Remove common trailing sections
            content = re.sub(r'\\bibliography\{.*?\}.*', '', content, flags=re.DOTALL)
            content = re.sub(r'\\appendix.*', '', content, flags=re.DOTALL)
            content = re.sub(r'\\end\{document\}.*', '', content, flags=re.DOTALL)
            content = clean_latex_markup(content)
            if len(content) >= 100:
                return content, "custom_intro_command_end"
    
    # Fallback: Try to find first section after abstract
    abstract_match = re.search(r'\\begin\{abstract\}.*?\\end\{abstract\}(.*?)\\section', 
                             tex_content, re.DOTALL)
    if abstract_match:
        first_section = abstract_match.group(1)
        first_section = clean_latex_markup(first_section)
        if len(first_section) >= 100:
            return first_section, "post_abstract"
    
    return None

def find_introduction_in_archive(tar_file, paper_id: str) -> Optional[tuple[str, str, str]]:
    """
    Find introduction using a hierarchical approach:
    1. Look for dedicated introduction files (any file with 'intro' or 'introduction' in name)
    2. Check the main (largest) tex file
    3. Search all tex files for introduction sections
    
    Returns (content, filename, method) or None if not found.
    """
    # Step 1: Look for dedicated introduction files with two-stage verification
    for member in tar_file.getmembers():
        if not member.isfile():
            continue
            
        filename_lower = member.name.lower()
        # Stage 1: Check if filename contains introduction-related keywords
        if "introduction" in filename_lower or "intro" in filename_lower:
            try:
                f = tar_file.extractfile(member)
                if f:
                    content = f.read().decode('utf-8', errors='ignore')
                    
                    # Stage 2: Verify content is actually introduction text
                    if is_introduction_content(content):
                        # Try structured extraction first
                        intro_result = extract_introduction(content)
                        if intro_result:
                            intro_text, _ = intro_result
                            return intro_text, member.name, "dedicated_intro_file"
                        
                        # If structured extraction fails, use cleaned content
                        cleaned_content = clean_latex_markup(content)
                        if len(cleaned_content) >= 100:
                            return cleaned_content, member.name, "dedicated_intro_file"
            except Exception as e:
                logger.debug(f"[{paper_id}] Error reading {member.name}: {e}")
                continue
    
    # Step 2: Try the main (largest) tex file
    tex_files = [(m, m.size) for m in tar_file.getmembers() 
                 if m.isfile() and m.name.endswith('.tex')]
    if tex_files:
        tex_files.sort(key=lambda x: x[1], reverse=True)
        main_tex = tex_files[0][0]
        try:
            f = tar_file.extractfile(main_tex)
            if f:
                content = f.read().decode('utf-8', errors='ignore')
                intro_result = extract_introduction(content)
                if intro_result:
                    intro_text, method = intro_result
                    return intro_text, main_tex.name, "main_tex_file"
        except Exception as e:
            logger.debug(f"[{paper_id}] Error reading main file {main_tex.name}: {e}")
    
    # Step 3: Search all remaining tex files
    for member, _ in tex_files[1:]:  # Skip main file we already checked
        try:
            f = tar_file.extractfile(member)
            if f:
                content = f.read().decode('utf-8', errors='ignore')
                intro_result = extract_introduction(content)
                if intro_result:
                    intro_text, method = intro_result
                    return intro_text, member.name, "scrape_entire_folder"
        except Exception as e:
            logger.debug(f"[{paper_id}] Error reading {member.name}: {e}")
            continue
    
    return None

def verify_latex_source(url: str, timeout: int, min_size: int, max_retries: int = 3) -> bool:
    """Verify that the LaTeX source exists and meets minimum requirements."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.head(url, timeout=timeout)
            content_type = response.headers.get('content-type', '')
            content_length = int(response.headers.get('content-length', 0))
            
            logger.info(f"HEAD {url} - Status: {response.status_code}, "
                       f"Type: {content_type}, Size: {content_length} bytes")
            
            if response.status_code != 200:
                logger.warning(f"LaTeX source not found: {url}")
                return False
            
            # Check content type (should be gzip)
            if 'gzip' not in content_type.lower():
                logger.warning(f"Invalid content type for {url}: {content_type}")
                return False
                
            # Check size
            if content_length < min_size:
                logger.warning(f"LaTeX source too small: {content_length} bytes")
                return False
                
            return True
            
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Retry {retry_count}/{max_retries} for {url}: {e}")
                time.sleep(2 ** retry_count)  # Exponential backoff
            else:
                logger.error(f"Error verifying LaTeX source after {max_retries} retries: {e}")
                return False

def check_latex_availability(paper: Paper, config: dict) -> bool:
    """Check if LaTeX source is available for a paper (header check only)."""
    try:
        # Skip if already processed or marked for skipping
        if paper.can_skip_intro_extraction():
            return False
            
        # Convert PDF URL to LaTeX URL
        if not paper.pdf_url:
            paper.update_intro_status("no_latex_source")
            paper.add_error("No PDF URL available")
            return False
            
        paper.latex_url = paper.pdf_url.replace('/pdf/', '/src/')
        
        # Verify LaTeX source (header check only)
        if verify_latex_source(paper.latex_url, config['timeout'], config['min_source_size']):
            return True
        else:
            paper.update_intro_status("no_latex_source")
            paper.add_error("LaTeX source verification failed")
            return False
    
    except Exception as e:
        paper.update_intro_status("no_latex_source")
        paper.add_error(f"LaTeX availability check failed: {str(e)}")
        logger.error(f"[{paper.id}] LaTeX availability check failed: {e}")
        return False

def download_and_extract_introduction(paper: Paper, config: dict) -> None:
    """Download LaTeX source and extract introduction text."""
    try:
        # Download the LaTeX source
        response = requests.get(paper.latex_url, timeout=config['timeout'])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract gzipped tar file
            tar_path = Path(temp_dir) / "source.tar.gz"
            tar_path.write_bytes(response.content)
            
            # Extract introduction using hierarchical approach
            with tarfile.open(tar_path, 'r:gz') as tar:
                result = find_introduction_in_archive(tar, paper.id)
                
                if result:
                    intro_text, tex_filename, method = result
                    
                    # Validate and truncate if needed
                    if len(intro_text) > config['max_introduction_length']:
                        intro_text = intro_text[:config['max_introduction_length']] + "..."
                    
                    paper.introduction_text = intro_text
                    paper.tex_file_name = tex_filename
                    paper.intro_extraction_method = method
                    paper.update_intro_status("intro_successful")
                else:
                    paper.update_intro_status("no_intro_found")
                    paper.add_error("Could not find introduction section")
                    logger.warning(f"[{paper.id}] No introduction found in any tex files")
    
    except Exception as e:
        paper.update_intro_status("extraction_failed")
        paper.add_error(f"Introduction extraction failed: {str(e)}")
        logger.error(f"[{paper.id}] Introduction extraction failed: {e}")

def run(papers: Dict[str, Paper], config: dict) -> Dict[str, Paper]:
    """
    Run the introduction extraction process on a batch of papers.
    
    This uses a proper two-phase approach:
    Phase 1: Check LaTeX availability using threading (header checks only)
    Phase 2: Download and extract introductions only from papers that passed Phase 1
    
    Args:
        papers: Dictionary of paper_id -> Paper objects
        config: Configuration dictionary with extraction parameters
    
    Returns:
        The updated papers dictionary
    """
    logger.info(f"Starting introduction extraction for {len(papers)} papers")
    
    # Phase 1: Check LaTeX availability using threading
    logger.info(f"\nPhase 1: Checking LaTeX source availability using {config['max_workers']} threads")
    papers_with_latex = {}
    papers_without_latex = {}
    
    # Submit all header check tasks
    with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        # Submit header check tasks for all papers
        future_to_paper = {
            executor.submit(check_latex_availability, paper, config): (paper_id, paper)
            for paper_id, paper in papers.items()
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_paper):
            paper_id, paper = future_to_paper[future]
            try:
                has_latex = future.result()
                if has_latex:
                    papers_with_latex[paper_id] = paper
                else:
                    papers_without_latex[paper_id] = paper
            except Exception as e:
                papers_without_latex[paper_id] = paper
                logger.error(f" {paper_id} - Header check failed: {e}")

    logger.info(f"Phase 1 complete: {len(papers_with_latex)}/{len(papers)} papers have LaTeX sources\n")
    
    # Phase 2: Extract introductions only from papers that passed Phase 1
    if papers_with_latex:
        logger.info(f"Phase 2: Extracting introductions from {len(papers_with_latex)} papers using {config['max_workers']} threads")
        
        # Submit download and extraction tasks for papers with LaTeX
        with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
            future_to_paper = {
                executor.submit(download_and_extract_introduction, paper, config): (paper_id, paper)
                for paper_id, paper in papers_with_latex.items()
            }
            
            # Track results by extraction outcome
            successful_extractions = 0
            failed_extractions = 0
            
            # Collect results as they complete
            for future in as_completed(future_to_paper):
                paper_id, paper = future_to_paper[future]
                try:
                    future.result()
                    if paper.is_intro_successful():
                        successful_extractions += 1
                        logger.info(f" {paper_id} - Introduction extraction SUCCESS - Method: {paper.intro_extraction_method}")
                    else:
                        failed_extractions += 1
                        logger.info(f" {paper_id} - Introduction extraction FAILED - Status: {paper.intro_status}")
                except Exception as e:
                    failed_extractions += 1
                    logger.error(f" {paper_id} - Introduction extraction FAILED: {e}")
            
            logger.info(f"Phase 2 complete: {successful_extractions} successful, {failed_extractions} failed")
    
    # Combine all papers back together
    all_papers = {**papers_with_latex, **papers_without_latex}
    
    # Log concise summary
    total_papers = len(all_papers)
    successful_count = sum(1 for p in all_papers.values() if p.is_intro_successful())
    no_latex_count = sum(1 for p in all_papers.values() if p.intro_status == "no_latex_source")
    failed_count = total_papers - successful_count - no_latex_count
    
    logger.info(f"Introduction extraction complete: {successful_count}/{total_papers} successful, {no_latex_count} no source, {failed_count} failed")
    
    return all_papers 