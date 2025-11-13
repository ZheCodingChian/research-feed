#!/usr/bin/env python3
"""
Test script to fetch raw XML response from arXiv API for a specific date.
"""

import urllib.request
import time
from datetime import datetime


def fetch_arxiv_xml(date_str, max_results=100):
    """
    Fetch XML response from arXiv API for a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format
        max_results: Maximum number of results to fetch (default: 100)

    Returns:
        Raw XML response string
    """
    # Convert date to arXiv API format
    target_date = datetime.strptime(date_str, '%Y-%m-%d')
    start_time = target_date.replace(hour=0, minute=0, second=0)
    end_time = target_date.replace(hour=23, minute=59, second=59)

    start_date = start_time.strftime('%Y%m%d%H%M%S')
    end_date = end_time.strftime('%Y%m%d%H%M%S')

    # Build query for cs.AI and cs.CV categories
    categories = '+OR+'.join(['cat:cs.AI', 'cat:cs.CV'])
    query = f"submittedDate:[{start_date}+TO+{end_date}]+AND+({categories})"

    # Build full URL with configurable max_results
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}"

    print(f"Fetching from arXiv API...")
    print(f"Date: {date_str}")
    print(f"Max results: {max_results}")
    print(f"URL: {url}")
    print(f"\nWaiting 5 seconds before request (to avoid rate limiting)...")

    # Wait 5 seconds to avoid rate limiting
    time.sleep(5)

    print("Sending request...\n")

    try:
        # Increase timeout to 120 seconds for large result sets
        with urllib.request.urlopen(url, timeout=120) as response:
            print("Reading response...")
            xml_data = response.read().decode('utf-8')
            return xml_data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def main():
    # Target date
    test_date = "2025-10-27"

    # Fetch XML (only 1 paper for testing)
    xml_response = fetch_arxiv_xml(test_date, max_results=1)

    if xml_response:
        print("=" * 80)
        print("XML Response Retrieved Successfully")
        print("=" * 80)
        print(f"\nResponse length: {len(xml_response)} characters\n")

        # Print first 2000 characters
        print("First 2000 characters of response:")
        print("-" * 80)
        print(xml_response[:2000])
        print("-" * 80)

        # Save to file
        output_file = f"arxiv_response_{test_date}.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_response)

        print(f"\n✓ Full XML response saved to: {output_file}")
    else:
        print("Failed to fetch XML response")


if __name__ == "__main__":
    main()