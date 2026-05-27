FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy giton source from parent directory (build context is project root)
COPY ../../src/giton /app/src/giton
COPY ../../pyproject.toml /app/pyproject.toml
COPY ../../README.md /app/README.md

# Install giton and dependencies
RUN pip install --no-cache-dir -e .

# Install pytest and testing dependencies
RUN pip install --no-cache-dir pytest pytest-cov

# Copy example files
COPY examples/advanced/main.py /app/main.py

# Create log directory
RUN mkdir -p /app/logs

# Set up git repository
RUN git init && \
    git config user.email "test@example.com" && \
    git config user.name "Test User"

# Default command - run example and save logs
CMD bash -c "python main.py 2>&1 | tee /app/logs/log.txt"
