FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed for your pipeline)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline source code
COPY src/ ./src/
COPY run.sh .

# Make run.sh executable
RUN chmod +x run.sh

# Set entrypoint to the wrapper script
ENTRYPOINT ["/app/run.sh"]
