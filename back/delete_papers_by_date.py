#!/usr/bin/env python3
"""
Script to delete papers from the database by published date.
"""

import sqlite3
from datetime import datetime


def delete_papers_by_date(db_path, target_date):
    """
    Delete all papers with a specific published date.

    Args:
        db_path: Path to the SQLite database
        target_date: Date string in YYYY-MM-DD format
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count papers before deletion
    cursor.execute("""
        SELECT COUNT(*)
        FROM papers
        WHERE DATE(published_date) = ?
    """, (target_date,))

    count_before = cursor.fetchone()[0]

    if count_before == 0:
        print(f"No papers found with published date: {target_date}")
        conn.close()
        return

    print(f"Found {count_before} papers with published date: {target_date}")
    print(f"Deleting papers...")

    # Delete papers with the target date
    cursor.execute("""
        DELETE FROM papers
        WHERE DATE(published_date) = ?
    """, (target_date,))

    deleted_count = cursor.rowcount
    conn.commit()

    print(f"✓ Deleted {deleted_count} papers from {target_date}")

    # Verify deletion
    cursor.execute("""
        SELECT COUNT(*)
        FROM papers
        WHERE DATE(published_date) = ?
    """, (target_date,))

    count_after = cursor.fetchone()[0]

    if count_after == 0:
        print(f"✓ Confirmed: No papers remaining with published date {target_date}")
    else:
        print(f"⚠ Warning: {count_after} papers still remain with published date {target_date}")

    conn.close()


if __name__ == "__main__":
    db_path = "./database.sqlite"
    target_date = "2025-10-28"

    print(f"Database: {db_path}")
    print(f"Target date: {target_date}")
    print("=" * 60)

    delete_papers_by_date(db_path, target_date)

    print("=" * 60)
    print("Done!")