FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy giton source from parent directory (build context is project root)
COPY src/giton /app/src/giton
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

# Install giton and dependencies
RUN pip install --no-cache-dir -e .

# Install pytest and testing dependencies
RUN pip install --no-cache-dir pytest pytest-cov pytest-asyncio

# Copy test files (relative to build context)
COPY examples/testing/test_giton_integration.py /app/test_giton_integration.py
COPY examples/testing/sample_project /app/sample_project

# Set up sample project as a git repository
WORKDIR /app/sample_project
RUN git init && \
    git config user.email "test@example.com" && \
    git config user.name "Test User"

WORKDIR /app

# Create log directory
RUN mkdir -p /app/logs

# Default command - run tests and save logs
CMD bash -c "python -m pytest test_giton_integration.py -v 2>&1 | tee /app/logs/log.txt"
