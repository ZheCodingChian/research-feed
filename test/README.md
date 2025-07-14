# Test Directory

This directory contains test scripts for downloading and processing arXiv papers.

## test.py

A test script that downloads arXiv source files from export URLs and extracts them locally.

### What it does:
- Downloads source archives from arXiv export URLs
- Automatically detects and extracts different archive formats (tar.gz, gzip, zip)
- Organizes downloads into separate directories by paper ID
- Provides detailed logging of the download and extraction process

### Test URLs:
- `http://export.arxiv.org/src/2012.01839v2`
- `http://export.arxiv.org/src/2402.07754v3` 
- `http://export.arxiv.org/src/2502.13417v2`

### Usage:
```bash
python test.py
```

### Output:
Downloads are saved to a `downloads/` subdirectory with the following structure:
```
downloads/
├── 2012.01839v2/
│   ├── 2012.01839v2_source (original downloaded file)
│   └── extracted/ (extracted contents)
├── 2402.07754v3/
│   ├── 2402.07754v3_source
│   └── extracted/
└── 2502.13417v2/
    ├── 2502.13417v2_source
    └── extracted/
```

### Features:
- Respectful downloading with delays between requests
- Proper error handling and logging
- Support for multiple archive formats
- Browser-like User-Agent headers
- Detailed progress reporting
