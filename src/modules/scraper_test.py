import time
import random
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

import config
from paper import Paper
from database import PaperDatabase

logger = logging.getLogger('SCRAPER_TEST')


class ArxivTestScraper:
    """
    Test scraper for ID-based paper fetching from arXiv API.
    
    This implementation reads paper IDs from a text file, loads cached papers,
    and fetches metadata only for missing or failed papers.
    """
    
    # ArXiv category mapping to descriptive names
    ARXIV_CATEGORY_MAPPING = {
        # Computer Science (cs)
        'cs.AI': 'cs.AI (Artificial Intelligence)',
        'cs.AR': 'cs.AR (Hardware Architecture)',
        'cs.CC': 'cs.CC (Computational Complexity)',
        'cs.CE': 'cs.CE (Computational Engineering, Finance, and Science)',
        'cs.CG': 'cs.CG (Computational Geometry)',
        'cs.CL': 'cs.CL (Computation and Language)',
        'cs.CR': 'cs.CR (Cryptography and Security)',
        'cs.CV': 'cs.CV (Computer Vision and Pattern Recognition)',
        'cs.CY': 'cs.CY (Computers and Society)',
        'cs.DB': 'cs.DB (Databases)',
        'cs.DC': 'cs.DC (Distributed, Parallel, and Cluster Computing)',
        'cs.DL': 'cs.DL (Digital Libraries)',
        'cs.DM': 'cs.DM (Discrete Mathematics)',
        'cs.DS': 'cs.DS (Data Structures and Algorithms)',
        'cs.ET': 'cs.ET (Emerging Technologies)',
        'cs.FL': 'cs.FL (Formal Languages and Automata Theory)',
        'cs.GL': 'cs.GL (General Literature)',
        'cs.GR': 'cs.GR (Graphics)',
        'cs.GT': 'cs.GT (Computer Science and Game Theory)',
        'cs.HC': 'cs.HC (Human-Computer Interaction)',
        'cs.IR': 'cs.IR (Information Retrieval)',
        'cs.IT': 'cs.IT (Information Theory)',
        'cs.LG': 'cs.LG (Machine Learning)',
        'cs.LO': 'cs.LO (Logic in Computer Science)',
        'cs.MA': 'cs.MA (Multiagent Systems)',
        'cs.MM': 'cs.MM (Multimedia)',
        'cs.MS': 'cs.MS (Mathematical Software)',
        'cs.NA': 'cs.NA (Numerical Analysis)',
        'cs.NE': 'cs.NE (Neural and Evolutionary Computing)',
        'cs.NI': 'cs.NI (Networking and Internet Architecture)',
        'cs.OH': 'cs.OH (Other Computer Science)',
        'cs.OS': 'cs.OS (Operating Systems)',
        'cs.PF': 'cs.PF (Performance)',
        'cs.PL': 'cs.PL (Programming Languages)',
        'cs.RO': 'cs.RO (Robotics)',
        'cs.SC': 'cs.SC (Symbolic Computation)',
        'cs.SD': 'cs.SD (Sound)',
        'cs.SE': 'cs.SE (Software Engineering)',
        'cs.SI': 'cs.SI (Social and Information Networks)',
        'cs.SY': 'cs.SY (Systems and Control)',
        
        # Economics (econ)
        'econ.EM': 'econ.EM (Econometrics)',
        'econ.GN': 'econ.GN (General Economics)',
        'econ.TH': 'econ.TH (Theoretical Economics)',
        
        # Electrical Engineering and Systems Science (eess)
        'eess.AS': 'eess.AS (Audio and Speech Processing)',
        'eess.IV': 'eess.IV (Image and Video Processing)',
        'eess.SP': 'eess.SP (Signal Processing)',
        'eess.SY': 'eess.SY (Systems and Control)',
        
        # Mathematics (math)
        'math.AC': 'math.AC (Commutative Algebra)',
        'math.AG': 'math.AG (Algebraic Geometry)',
        'math.AP': 'math.AP (Analysis of PDEs)',
        'math.AT': 'math.AT (Algebraic Topology)',
        'math.CA': 'math.CA (Classical Analysis and ODEs)',
        'math.CO': 'math.CO (Combinatorics)',
        'math.CT': 'math.CT (Category Theory)',
        'math.CV': 'math.CV (Complex Variables)',
        'math.DG': 'math.DG (Differential Geometry)',
        'math.DS': 'math.DS (Dynamical Systems)',
        'math.FA': 'math.FA (Functional Analysis)',
        'math.GM': 'math.GM (General Mathematics)',
        'math.GN': 'math.GN (General Topology)',
        'math.GR': 'math.GR (Group Theory)',
        'math.GT': 'math.GT (Geometric Topology)',
        'math.HO': 'math.HO (History and Overview)',
        'math.IT': 'math.IT (Information Theory)',
        'math.KT': 'math.KT (K-Theory and Homology)',
        'math.LO': 'math.LO (Logic)',
        'math.MG': 'math.MG (Metric Geometry)',
        'math.MP': 'math.MP (Mathematical Physics)',
        'math.NA': 'math.NA (Numerical Analysis)',
        'math.NT': 'math.NT (Number Theory)',
        'math.OA': 'math.OA (Operator Algebras)',
        'math.OC': 'math.OC (Optimization and Control)',
        'math.PR': 'math.PR (Probability)',
        'math.QA': 'math.QA (Quantum Algebra)',
        'math.RA': 'math.RA (Rings and Algebras)',
        'math.RT': 'math.RT (Representation Theory)',
        'math.SG': 'math.SG (Symplectic Geometry)',
        'math.SP': 'math.SP (Spectral Theory)',
        'math.ST': 'math.ST (Statistics Theory)',
        
        # Physics (and related fields)
        'astro-ph.CO': 'astro-ph.CO (Cosmology and Nongalactic Astrophysics)',
        'astro-ph.EP': 'astro-ph.EP (Earth and Planetary Astrophysics)',
        'astro-ph.GA': 'astro-ph.GA (Astrophysics of Galaxies)',
        'astro-ph.HE': 'astro-ph.HE (High Energy Astrophysical Phenomena)',
        'astro-ph.IM': 'astro-ph.IM (Instrumentation and Methods for Astrophysics)',
        'astro-ph.SR': 'astro-ph.SR (Solar and Stellar Astrophysics)',
        'cond-mat.dis-nn': 'cond-mat.dis-nn (Disordered Systems and Neural Networks)',
        'cond-mat.mes-hall': 'cond-mat.mes-hall (Mesoscale and Nanoscale Physics)',
        'cond-mat.mtrl-sci': 'cond-mat.mtrl-sci (Materials Science)',
        'cond-mat.other': 'cond-mat.other (Other Condensed Matter)',
        'cond-mat.quant-gas': 'cond-mat.quant-gas (Quantum Gases)',
        'cond-mat.soft': 'cond-mat.soft (Soft Condensed Matter)',
        'cond-mat.stat-mech': 'cond-mat.stat-mech (Statistical Mechanics)',
        'cond-mat.str-el': 'cond-mat.str-el (Strongly Correlated Electrons)',
        'cond-mat.supr-con': 'cond-mat.supr-con (Superconductivity)',
        'gr-qc': 'gr-qc (General Relativity and Quantum Cosmology)',
        'hep-ex': 'hep-ex (High Energy Physics - Experiment)',
        'hep-lat': 'hep-lat (High Energy Physics - Lattice)',
        'hep-ph': 'hep-ph (High Energy Physics - Phenomenology)',
        'hep-th': 'hep-th (High Energy Physics - Theory)',
        'math-ph': 'math-ph (Mathematical Physics)',
        'nlin.AO': 'nlin.AO (Adaptation and Self-Organizing Systems)',
        'nlin.CD': 'nlin.CD (Chaotic Dynamics)',
        'nlin.CG': 'nlin.CG (Cellular Automata and Lattice Gases)',
        'nlin.PS': 'nlin.PS (Pattern Formation and Solitons)',
        'nlin.SI': 'nlin.SI (Exactly Solvable and Integrable Systems)',
        'nucl-ex': 'nucl-ex (Nuclear Experiment)',
        'nucl-th': 'nucl-th (Nuclear Theory)',
        'physics.acc-ph': 'physics.acc-ph (Accelerator Physics)',
        'physics.ao-ph': 'physics.ao-ph (Atmospheric and Oceanic Physics)',
        'physics.app-ph': 'physics.app-ph (Applied Physics)',
        'physics.atm-clus': 'physics.atm-clus (Atomic and Molecular Clusters)',
        'physics.atom-ph': 'physics.atom-ph (Atomic Physics)',
        'physics.bio-ph': 'physics.bio-ph (Biological Physics)',
        'physics.chem-ph': 'physics.chem-ph (Chemical Physics)',
        'physics.class-ph': 'physics.class-ph (Classical Physics)',
        'physics.comp-ph': 'physics.comp-ph (Computational Physics)',
        'physics.data-an': 'physics.data-an (Data Analysis, Statistics and Probability)',
        'physics.ed-ph': 'physics.ed-ph (Physics Education)',
        'physics.flu-dyn': 'physics.flu-dyn (Fluid Dynamics)',
        'physics.gen-ph': 'physics.gen-ph (General Physics)',
        'physics.geo-ph': 'physics.geo-ph (Geophysics)',
        'physics.hist-ph': 'physics.hist-ph (History and Philosophy of Physics)',
        'physics.ins-det': 'physics.ins-det (Instrumentation and Detectors)',
        'physics.med-ph': 'physics.med-ph (Medical Physics)',
        'physics.optics': 'physics.optics (Optics)',
        'physics.plasm-ph': 'physics.plasm-ph (Plasma Physics)',
        'physics.pop-ph': 'physics.pop-ph (Popular Physics)',
        'physics.soc-ph': 'physics.soc-ph (Physics and Society)',
        'physics.space-ph': 'physics.space-ph (Space Physics)',
        'quant-ph': 'quant-ph (Quantum Physics)',
        
        # Quantitative Biology (q-bio)
        'q-bio.BM': 'q-bio.BM (Biomolecules)',
        'q-bio.CB': 'q-bio.CB (Cell Behavior)',
        'q-bio.GN': 'q-bio.GN (Genomics)',
        'q-bio.MN': 'q-bio.MN (Molecular Networks)',
        'q-bio.NC': 'q-bio.NC (Neurons and Cognition)',
        'q-bio.OT': 'q-bio.OT (Other Quantitative Biology)',
        'q-bio.PE': 'q-bio.PE (Populations and Evolution)',
        'q-bio.QM': 'q-bio.QM (Quantitative Methods)',
        'q-bio.SC': 'q-bio.SC (Subcellular Processes)',
        'q-bio.TO': 'q-bio.TO (Tissues and Organs)',
        
        # Quantitative Finance (q-fin)
        'q-fin.CP': 'q-fin.CP (Computational Finance)',
        'q-fin.EC': 'q-fin.EC (Economics)',
        'q-fin.GN': 'q-fin.GN (General Finance)',
        'q-fin.MF': 'q-fin.MF (Mathematical Finance)',
        'q-fin.PM': 'q-fin.PM (Portfolio Management)',
        'q-fin.PR': 'q-fin.PR (Pricing of Securities)',
        'q-fin.RM': 'q-fin.RM (Risk Management)',
        'q-fin.ST': 'q-fin.ST (Statistical Finance)',
        'q-fin.TR': 'q-fin.TR (Trading and Market Microstructure)',
        
        # Statistics (stat)
        'stat.AP': 'stat.AP (Applications)',
        'stat.CO': 'stat.CO (Computation)',
        'stat.ME': 'stat.ME (Methodology)',
        'stat.ML': 'stat.ML (Machine Learning)',
        'stat.OT': 'stat.OT (Other Statistics)',
        'stat.TH': 'stat.TH (Statistics Theory)',
    }
    
    def __init__(self):
        self.config = config.ARXIV
        self.db = PaperDatabase()
        self.session_stats = {
            'successfully_scraped': 0,
            'scraping_failed': 0,
            'api_calls': 0,
            'retries': 0
        }

    def run(self, run_mode: str, run_value: str) -> Dict[str, Paper]:
        """
        Main entry point for the test scraper.
        
        Args:
            run_mode: Must be 'test'
            run_value: Path to text file containing paper IDs
            
        Returns:
            Dictionary of paper_id -> Paper objects
            
        Raises:
            ValueError: If run_mode is not 'test'
            FileNotFoundError: If test file doesn't exist
        """
        if run_mode != 'test':
            raise ValueError(f"Test scraper only supports 'test' mode, got '{run_mode}'")
        
        logger.info(f"Starting test scraping from file {run_value}")
        
        # Step 1: Read paper IDs from file
        paper_ids = self._read_paper_ids_from_file(run_value)
        logger.info(f"Loaded {len(paper_ids)} paper IDs from test file")
        self._check_paper_limit(len(paper_ids))
        
        # Step 2: Load cached papers and build runtime dict
        runtime_dict = self._load_cached_papers(paper_ids)
        
        # Step 3: Fetch metadata for missing papers
        complete_dict = self._fetch_missing_papers_metadata(runtime_dict)
        
        # Step 4: Clean up categories to keep only arXiv format
        complete_dict = self._clean_arxiv_categories(complete_dict)
        
        # Log final statistics
        self._log_session_summary()
        
        return complete_dict

    def _read_paper_ids_from_file(self, file_path: str) -> List[str]:
        """
        Read paper IDs from text file.
        
        Args:
            file_path: Path to text file containing one paper ID per line
            
        Returns:
            List of paper IDs
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(file_path, 'r') as f:
                paper_ids = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Read {len(paper_ids)} paper IDs from {file_path}")
            return paper_ids
            
        except FileNotFoundError:
            logger.error(f"Test file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading test file {file_path}: {e}")
            raise

    def _check_paper_limit(self, paper_count: int) -> None:
        """
        Check if paper count exceeds configured limit.
        
        Args:
            paper_count: Number of papers found
            
        Raises:
            RuntimeError: If count exceeds limit
        """
        max_limit = self.config['max_paper_limit']
        if paper_count > max_limit:
            error_msg = f"Paper count ({paper_count}) exceeds maximum limit ({max_limit})"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _load_cached_papers(self, paper_ids: List[str]) -> Dict[str, Optional[Paper]]:
        """
        Load cached papers and build initial runtime dictionary.
        
        Args:
            paper_ids: List of paper IDs to check
            
        Returns:
            Dictionary with Paper objects for successfully scraped papers,
            None for papers that need processing
        """
        logger.info(f"Loading cached papers for {len(paper_ids)} IDs")
        
        # Query database for existing papers
        cached_papers = self.db.load_papers(paper_ids)
        logger.info(f"Found {len(cached_papers)} papers in cache")
        
        runtime_dict = {}
        cache_hits = 0
        cache_misses = 0
        
        for paper_id in paper_ids:
            if paper_id in cached_papers and cached_papers[paper_id].is_successfully_scraped():
                # Keep successfully scraped paper - skip metadata extraction
                runtime_dict[paper_id] = cached_papers[paper_id]
                cache_hits += 1
            else:
                # Either not in cache or failed status - mark for processing
                runtime_dict[paper_id] = None
                cache_misses += 1
        
        logger.info(f"Cache analysis: {cache_hits} hits, {cache_misses} misses")
        return runtime_dict

    def _fetch_missing_papers_metadata(self, runtime_dict: Dict[str, Optional[Paper]]) -> Dict[str, Paper]:
        """
        Fetch metadata for papers that need processing.
        
        Args:
            runtime_dict: Dictionary with None values for papers to process
            
        Returns:
            Complete dictionary with all Paper objects
        """
        papers_to_process = [paper_id for paper_id, paper in runtime_dict.items() if paper is None]
        logger.info(f"Fetching metadata for {len(papers_to_process)} papers")
        
        if not papers_to_process:
            logger.info("No papers need metadata fetching")
            return runtime_dict
        
        # Build arXiv API query for missing papers
        xml_response = self._fetch_papers_by_ids(papers_to_process)
        
        # Extract metadata from response
        return self._extract_metadata_from_response(xml_response, runtime_dict, papers_to_process)

    def _fetch_papers_by_ids(self, paper_ids: List[str]) -> str:
        """
        Fetch papers by their IDs from arXiv API.
        
        Args:
            paper_ids: List of paper IDs to fetch
            
        Returns:
            Raw XML response from arXiv API
            
        Raises:
            Exception: If all retry attempts fail
        """
        # Build search query with OR conditions
        id_conditions = [f"id:{paper_id}" for paper_id in paper_ids]
        search_query = "+OR+".join(id_conditions)
        url = f"http://export.arxiv.org/api/query?search_query={search_query}&max_results={len(paper_ids)}"
        
        logger.info(f"Fetching metadata for {len(paper_ids)} papers")
        return self._make_api_request(url)

    def _make_api_request(self, url: str) -> str:
        """
        Make API request with exponential backoff retry logic.
        
        Args:
            url: Complete URL to request
            
        Returns:
            Response content as string
            
        Raises:
            Exception: If all retry attempts fail
        """
        max_retries = self.config['rate_limiting']['max_retries']
        base_wait = self.config['rate_limiting']['wait_time']
        backoff_factor = self.config['rate_limiting']['backoff_factor']
        jitter = self.config['rate_limiting']['jitter']
        
        for attempt in range(max_retries + 1):
            try:
                self.session_stats['api_calls'] += 1
                logger.debug(f"API request attempt {attempt + 1}/{max_retries + 1}: {url}")
                
                with urllib.request.urlopen(url, timeout=30) as response:
                    return response.read().decode('utf-8')
                    
            except Exception as e:
                if attempt < max_retries:
                    self.session_stats['retries'] += 1
                    wait_time = base_wait * (backoff_factor ** attempt)
                    actual_wait = wait_time + random.uniform(-jitter, jitter)
                    actual_wait = max(0, actual_wait)
                    
                    logger.warning(f"API request failed (attempt {attempt + 1}), retrying in {actual_wait:.1f}s: {e}")
                    time.sleep(actual_wait)
                else:
                    logger.error(f"API request failed after {max_retries + 1} attempts: {e}")
                    raise

    def _extract_metadata_from_response(self, xml_response: str, runtime_dict: Dict[str, Optional[Paper]], papers_to_process: List[str]) -> Dict[str, Paper]:
        """
        Extract metadata from XML response for papers that need processing.
        
        Args:
            xml_response: Raw XML from arXiv API
            runtime_dict: Dictionary with None values for papers to process
            papers_to_process: List of paper IDs we're trying to process
            
        Returns:
            Complete dictionary with all Paper objects
        """
        logger.info(f"Extracting metadata from XML response")
        
        try:
            root = ET.fromstring(xml_response)
            processed_count = 0
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                try:
                    paper = self._parse_single_paper(entry)
                    if paper and paper.id in papers_to_process:
                        runtime_dict[paper.id] = paper
                        processed_count += 1
                        self.session_stats['successfully_scraped'] += 1
                        
                except Exception as e:
                    # Try to extract paper ID for error logging
                    paper_id = "unknown"
                    try:
                        id_element = entry.find('{http://www.w3.org/2005/Atom}id')
                        if id_element is not None:
                            paper_id = id_element.text.split('/')[-1].split('v')[0]
                    except:
                        pass
                    
                    logger.error(f"Failed to parse paper {paper_id}: {e}")
                    
                    # Create failed paper object if we can identify the ID
                    if paper_id != "unknown" and paper_id in papers_to_process:
                        failed_paper = Paper(
                            id=paper_id,
                            title="",
                            authors=[],
                            categories=[],
                            abstract="",
                            published_date=datetime.now(),
                            arxiv_url=None,
                            pdf_url=None
                        )
                        failed_paper.update_scraper_status("scraping_failed")
                        failed_paper.add_error(f"Metadata extraction failed: {str(e)}")
                        runtime_dict[paper_id] = failed_paper
                        self.session_stats['scraping_failed'] += 1
            
            # Handle any papers that weren't found in the XML
            for paper_id, paper in runtime_dict.items():
                if paper is None:
                    logger.warning(f"Paper {paper_id} not found in arXiv API response")
                    failed_paper = Paper(
                        id=paper_id,
                        title="",
                        authors=[],
                        categories=[],
                        abstract="",
                        published_date=datetime.now(),
                        arxiv_url=None,
                        pdf_url=None
                    )
                    failed_paper.update_scraper_status("scraping_failed")
                    failed_paper.add_error("Paper not found in arXiv API response")
                    runtime_dict[paper_id] = failed_paper
                    self.session_stats['scraping_failed'] += 1
            
            logger.info(f"Successfully processed {processed_count} papers")
            return runtime_dict
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML response for metadata extraction: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during metadata extraction: {e}")
            raise

    def _parse_single_paper(self, entry) -> Optional[Paper]:
        """
        Parse a single paper entry from XML.
        
        Args:
            entry: XML entry element
            
        Returns:
            Paper object or None if parsing fails
        """
        try:
            # Extract paper ID
            id_element = entry.find('{http://www.w3.org/2005/Atom}id')
            if id_element is None:
                return None
            
            arxiv_id = id_element.text.split('/')[-1]
            if 'v' in arxiv_id:
                arxiv_id = arxiv_id.split('v')[0]
            
            # Extract title
            title_element = entry.find('{http://www.w3.org/2005/Atom}title')
            title = title_element.text.strip() if title_element is not None else ""
            
            # Extract authors
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name_element = author.find('{http://www.w3.org/2005/Atom}name')
                if name_element is not None:
                    authors.append(name_element.text.strip())
            
            # Extract categories
            categories = []
            for category in entry.findall('{http://www.w3.org/2005/Atom}category'):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # Extract abstract
            summary_element = entry.find('{http://www.w3.org/2005/Atom}summary')
            abstract = summary_element.text.strip() if summary_element is not None else ""
            
            # Extract published date
            published_element = entry.find('{http://www.w3.org/2005/Atom}published')
            if published_element is not None:
                published_date = datetime.fromisoformat(published_element.text.replace('Z', '+00:00'))
            else:
                published_date = datetime.now()
            
            # Extract URLs from link elements
            arxiv_url = None
            pdf_url = None
            
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                rel = link.get('rel')
                href = link.get('href')
                type_attr = link.get('type')
                
                if rel == 'alternate' and type_attr == 'text/html':
                    arxiv_url = href
                elif rel == 'related' and type_attr == 'application/pdf':
                    pdf_url = href
            
            # Log missing URLs for debugging
            missing_urls = []
            if arxiv_url is None:
                missing_urls.append('arxiv_url')
            if pdf_url is None:
                missing_urls.append('pdf_url')
            
            if missing_urls:
                logger.warning(f"Paper {arxiv_id} missing URLs: {', '.join(missing_urls)}")
            
            # Create paper object
            paper = Paper(
                id=arxiv_id,
                title=title,
                authors=authors,
                categories=categories,
                abstract=abstract,
                published_date=published_date,
                arxiv_url=arxiv_url,
                pdf_url=pdf_url
            )
            paper.update_scraper_status("successfully_scraped")
            
            return paper
            
        except Exception as e:
            logger.error(f"Error parsing individual paper: {e}")
            return None

    def _clean_arxiv_categories(self, runtime_dict: Dict[str, Paper]) -> Dict[str, Paper]:
        """
        Clean up categories to keep only properly formatted arXiv categories and enhance with descriptive names.
        
        Keeps categories matching pattern: [a-z]{2,}\\.[A-Z]{2} or other valid arXiv patterns
        Examples: cs.AI -> cs.AI (Artificial Intelligence), stat.ML -> stat.ML (Machine Learning)
        Discards: ACM classifications, MSC codes, etc.
        
        Args:
            runtime_dict: Dictionary of paper_id -> Paper objects
            
        Returns:
            Dictionary with cleaned Paper objects having enhanced category descriptions
        """
        import re
        # Enhanced pattern to match more arXiv categories including physics categories
        arxiv_pattern = re.compile(r'^([a-z]{2,}(-[a-z]{2,})*\.[A-Z]{2}|[a-z]+-[a-z]+|quant-ph|gr-qc|math-ph|nucl-ex|nucl-th|hep-ex|hep-lat|hep-ph|hep-th)$')
        
        cleaned_count = 0
        total_enhanced_count = 0
        
        for paper_id, paper in runtime_dict.items():
            if paper and paper.categories:
                original_categories = paper.categories.copy()
                # Filter to keep only arXiv-formatted categories
                valid_categories = [cat for cat in paper.categories if arxiv_pattern.match(cat)]
                
                # Enhance valid categories with descriptive names
                enhanced_categories = []
                paper_enhanced_count = 0
                for cat in valid_categories:
                    if cat in self.ARXIV_CATEGORY_MAPPING:
                        enhanced_categories.append(self.ARXIV_CATEGORY_MAPPING[cat])
                        paper_enhanced_count += 1
                        total_enhanced_count += 1
                    else:
                        # Keep original if not in mapping (fallback for new/unknown categories)
                        enhanced_categories.append(cat)
                        logger.debug(f"Category {cat} not found in mapping, keeping original format")
                
                # Update paper categories
                paper.categories = enhanced_categories
                
                # Track changes for logging
                if len(enhanced_categories) < len(original_categories):
                    removed_categories = [cat for cat in original_categories if not arxiv_pattern.match(cat)]
                    cleaned_count += 1
                    
                    logger.info(f"Processed categories for paper {paper_id}: "
                               f"enhanced {paper_enhanced_count} valid categories, "
                               f"removed {len(removed_categories)} invalid categories: {removed_categories}")
                elif paper_enhanced_count > 0:
                    logger.debug(f"Enhanced categories for paper {paper_id}: {enhanced_categories}")
        
        # Log summary
        if cleaned_count > 0:
            logger.info(f"Category processing completed: {cleaned_count} papers had invalid categories removed, "
                       f"{total_enhanced_count} categories enhanced with descriptions")
        elif total_enhanced_count > 0:
            logger.info(f"Category processing completed: {total_enhanced_count} categories enhanced with descriptions")
        else:
            logger.info("Category processing completed: no changes needed")
        
        return runtime_dict

    def _log_session_summary(self) -> None:
        """Log summary of scraping session."""
        logger.info(f"Test scraping session completed:")
        logger.info(f"  Successfully scraped: {self.session_stats['successfully_scraped']}")
        logger.info(f"  Scraping failed: {self.session_stats['scraping_failed']}")
        logger.info(f"  API calls made: {self.session_stats['api_calls']}")
        logger.info(f"  Retries: {self.session_stats['retries']}")


def run(run_mode: str, run_value: str) -> Dict[str, Paper]:
    """
    Main entry point for the test scraper module.
    
    Args:
        run_mode: Must be 'test'
        run_value: Path to text file containing paper IDs
        
    Returns:
        Dictionary of paper_id -> Paper objects
    """
    scraper = ArxivTestScraper()
    return scraper.run(run_mode, run_value)
