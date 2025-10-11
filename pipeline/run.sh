#!/bin/bash
set -e

echo "=== Pipeline Starting at $(date) ==="

# Use test mode with test_papers.txt
TEST_FILE="test_papers.txt"
echo "Processing papers from test file: $TEST_FILE"

# Step 1: Copy existing database to working copy
if [ -f /data/database.sqlite ]; then
    cp /data/database.sqlite /data/database.new.sqlite
    echo "✓ Created working copy: database.new.sqlite"
else
    echo "⚠ No existing database found, creating new one"
    touch /data/database.new.sqlite
fi

# Step 2: Run the pipeline (works on database.new.sqlite)
echo "=== Starting pipeline processing ==="
cd /app/src
python main.py --test "/app/$TEST_FILE"

# Step 3: Atomic swap
echo "=== Performing atomic database swap ==="
mv /data/database.new.sqlite /data/database.sqlite
echo "✓ Atomic swap complete"

echo "=== Pipeline Completed at $(date) ==="
