# Giton Testing Example with Docker

This example demonstrates how to use giton in a testing environment with Docker integration. It shows how giton can be integrated into CI/CD pipelines and local development workflows.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### Using Docker Compose (Recommended)

```bash
cd examples/testing
docker-compose up --build
```

This will:
1. Build a Docker image with giton installed
2. Initialize a git repository with giton hooks
3. Run giton policies and tests
4. Show the results

### Manual Testing

```bash
# Build the Docker image
docker build -t giton-test .

# Run the container
docker run -it --rm giton-test

# Or run with volume mount for local testing
docker run -it --rm -v $(pwd)/test-repo:/app/test-repo giton-test
```

## What This Example Demonstrates

### 1. Giton Integration with pytest
- Running giton policies before tests
- Failing tests when policy violations are found
- Generating test reports with policy findings

### 2. Docker-based Testing Environment
- Isolated testing environment
- Reproducible test runs
- Easy CI/CD integration

### 3. Git Hooks in Container
- Pre-commit hooks running in Docker
- Policy evaluation before commits
- Automated quality checks

## Project Structure

```
examples/testing/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── test_giton_integration.py  # pytest tests
├── sample_project/         # Sample Python project
│   ├── src/
│   │   └── example.py
│   └── tests/
│       └── test_example.py
└── README.md
```

## Running Tests

### With Docker Compose

```bash
# Run all tests
docker-compose run app pytest

# Run specific test
docker-compose run app pytest test_giton_integration.py::test_pre_commit_policy

# Run with coverage
docker-compose run app pytest --cov=src
```

### Without Docker

```bash
# Install giton
pip install -e ../../../

# Initialize giton in the sample project
cd sample_project
giton init

# Run tests with giton
giton hook pre-commit
pytest
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test with Giton

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    container: python:3.13
    steps:
      - uses: actions/checkout@v3
      - name: Install giton
        run: pip install giton
      - name: Initialize giton
        run: giton init
      - name: Run giton policies
        run: giton policy check pre-commit
      - name: Run tests
        run: pytest
```

### GitLab CI Example

```yaml
test:
  image: python:3.13
  before_script:
    - pip install giton
    - giton init
  script:
    - giton policy check pre-commit
    - pytest
```

## Policy Configuration

Create `.giton/config.yaml` in your repository:

```yaml
policies:
  commit_message:
    enabled: true
    pattern: "^(feat|fix|docs|style|refactor|test|chore):"
  
  test_coverage:
    enabled: true
    min_coverage: 80
  
  code_quality:
    enabled: true
    tools: ["ruff", "mypy"]
```

## Troubleshooting

### Git hooks not running in Docker
Make sure the `.git` directory is properly mounted and has correct permissions.

### Tests failing with import errors
Ensure giton is installed in the Docker image or add the source directory to PYTHONPATH.

### Policy checks not working
Verify that `.giton/config.yaml` exists and is properly formatted.
