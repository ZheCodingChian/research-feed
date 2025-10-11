#!/bin/bash
set -e

echo "=== Pipeline Starting at $(date) ==="

# Calculate date from 15 days ago
TARGET_DATE=$(date -d "15 days ago" +%Y-%m-%d)
echo "Processing papers from: $TARGET_DATE"

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
python main.py --date "$TARGET_DATE"

# Step 3: Atomic swap
echo "=== Performing atomic database swap ==="
mv /data/database.new.sqlite /data/database.sqlite
echo "✓ Atomic swap complete"

echo "=== Pipeline Completed at $(date) ==="
