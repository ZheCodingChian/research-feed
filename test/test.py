#!/usr/bin/env python3
"""
Test script to download arXiv source files from export URLs.
Downloads and extracts content to the test directory.
"""

import os
import requests
import tarfile
import gzip
import zipfile
import tempfile
from pathlib import Path
from urllib.parse import urlparse
import time

class ArxivSourceDownloader:
    def __init__(self, download_dir="downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Setup session with headers to mimic a browser
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_paper_id(self, url):
        """Extract paper ID from arXiv URL"""
        try:
            # Extract the paper ID from the URL
            # e.g., "http://export.arxiv.org/src/2012.01839v2" -> "2012.01839v2"
            return url.split('/')[-1]
        except:
            return "unknown"
    
    def download_file(self, url, filename):
        """Download a file from URL with proper error handling"""
        try:
            print(f"Downloading: {url}")
            
            # Add delay to be respectful to the server
            time.sleep(1)
            
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Downloaded successfully: {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def extract_archive(self, archive_path, extract_dir):
        """Extract various types of archives"""
        try:
            extract_dir = Path(extract_dir)
            extract_dir.mkdir(exist_ok=True)
            
            # Check if it's a tar.gz file (most common for arXiv)
            if tarfile.is_tarfile(archive_path):
                print(f"Extracting tar.gz archive: {archive_path}")
                with tarfile.open(archive_path, 'r:*') as tar:
                    # List the contents first
                    members = tar.getmembers()
                    print(f"Archive contains {len(members)} files:")
                    for member in members[:10]:  # Show first 10 files
                        file_type = "directory" if member.isdir() else "file"
                        print(f"  - {member.name} ({file_type}, {member.size} bytes)")
                    if len(members) > 10:
                        print(f"  ... and {len(members) - 10} more files")
                    
                    # Extract all files
                    tar.extractall(extract_dir)
                    
            elif zipfile.is_zipfile(archive_path):
                print(f"Extracting zip archive: {archive_path}")
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    print(f"Archive contains {len(file_list)} files:")
                    for filename in file_list[:10]:
                        print(f"  - {filename}")
                    if len(file_list) > 10:
                        print(f"  ... and {len(file_list) - 10} more files")
                    zip_ref.extractall(extract_dir)
                    
            else:
                # Try to handle as gzip (single file)
                try:
                    print(f"Trying to extract as gzip: {archive_path}")
                    with gzip.open(archive_path, 'rb') as gz_file:
                        content = gz_file.read()
                        output_file = extract_dir / f"{archive_path.stem}.txt"
                        with open(output_file, 'wb') as out:
                            out.write(content)
                        print(f"Extracted single gzipped file: {output_file}")
                except:
                    print(f"Unknown archive format for {archive_path}, copying as-is")
                    # Copy the file as-is if we can't determine the format
                    output_file = extract_dir / archive_path.name
                    import shutil
                    shutil.copy2(archive_path, output_file)
            
            print(f"Extracted to: {extract_dir}")
            return True
            
        except Exception as e:
            print(f"Error extracting {archive_path}: {e}")
            return False
    
    def download_and_extract(self, url):
        """Download and extract a single arXiv source"""
        paper_id = self.extract_paper_id(url)
        print(f"\n{'='*50}")
        print(f"Processing: {paper_id}")
        print(f"URL: {url}")
        
        # Create directory for this paper
        paper_dir = self.download_dir / paper_id
        paper_dir.mkdir(exist_ok=True)
        
        # Download the file
        archive_path = paper_dir / f"{paper_id}_source"
        
        if self.download_file(url, archive_path):
            # Try to extract the archive
            extract_dir = paper_dir / "extracted"
            if self.extract_archive(archive_path, extract_dir):
                print(f"Successfully processed {paper_id}")
                
                # List extracted contents
                if extract_dir.exists():
                    files = list(extract_dir.rglob('*'))
                    if files:
                        print(f"\nExtracted contents ({len(files)} items):")
                        
                        # Separate directories and files
                        dirs = [f for f in files if f.is_dir()]
                        file_items = [f for f in files if f.is_file()]
                        
                        if dirs:
                            print(f"Directories ({len(dirs)}):")
                            for dir_path in sorted(dirs)[:5]:
                                print(f"  📁 {dir_path.relative_to(extract_dir)}")
                            if len(dirs) > 5:
                                print(f"  ... and {len(dirs) - 5} more directories")
                        
                        if file_items:
                            print(f"Files ({len(file_items)}):")
                            for file_path in sorted(file_items)[:15]:
                                try:
                                    size = file_path.stat().st_size
                                    rel_path = file_path.relative_to(extract_dir)
                                    # Show file extension to understand content type
                                    ext = file_path.suffix.lower()
                                    icon = "📄"
                                    if ext in ['.tex', '.latex']:
                                        icon = "📝"
                                    elif ext in ['.py', '.js', '.cpp', '.c', '.h']:
                                        icon = "💾"
                                    elif ext in ['.pdf']:
                                        icon = "📋"
                                    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.eps']:
                                        icon = "🖼️"
                                    elif ext in ['.bib']:
                                        icon = "📚"
                                    
                                    print(f"  {icon} {rel_path} ({size:,} bytes)")
                                except:
                                    print(f"  📄 {file_path.name} (size unknown)")
                            if len(file_items) > 15:
                                print(f"  ... and {len(file_items) - 15} more files")
                    else:
                        print("No files found in extracted directory")
            else:
                print(f"Failed to extract archive for {paper_id}")
        else:
            print(f"Failed to download {paper_id}")

def main():
    """Main function to test downloading from the specified URLs"""
    
    # URLs to test
    test_urls = [
        "http://export.arxiv.org/src/2012.01839v2",
        "http://export.arxiv.org/src/2402.07754v3", 
        "http://export.arxiv.org/src/2502.13417v2"
    ]
    
    print("ArXiv Source Downloader Test")
    print("="*50)
    print(f"Testing {len(test_urls)} URLs")
    
    # Initialize downloader
    current_dir = Path(__file__).parent
    downloader = ArxivSourceDownloader(download_dir=current_dir / "downloads")
    
    # Download each URL
    success_count = 0
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Processing URL: {url}")
        try:
            downloader.download_and_extract(url)
            success_count += 1
        except Exception as e:
            print(f"Unexpected error processing {url}: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total URLs processed: {len(test_urls)}")
    print(f"Successful downloads: {success_count}")
    print(f"Failed downloads: {len(test_urls) - success_count}")
    
    # Show directory structure
    downloads_dir = current_dir / "downloads"
    if downloads_dir.exists():
        print(f"\nDownloads saved to: {downloads_dir.absolute()}")
        subdirs = [d for d in downloads_dir.iterdir() if d.is_dir()]
        if subdirs:
            print(f"Created {len(subdirs)} paper directories:")
            for subdir in sorted(subdirs):
                print(f"  - {subdir.name}")

if __name__ == "__main__":
    main()
