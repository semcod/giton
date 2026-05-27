# Basic Giton Example

This example demonstrates the basic usage of giton as a Python library.

## Setup

```bash
# Install giton
pip install giton

# Initialize giton in your repository
giton init
```

## Usage

The `main.py` script shows how to:
- Load git context (staged files, diff, recent commits)
- Run giton triggers programmatically
- Handle policy findings and plugin results

## Running the example

```bash
cd examples/basic

# Run directly
python main.py

# Or run with pytest for testing
pytest main.py -v
```

This will:
1. Collect git context from the current repository
2. Run the `pre-commit` trigger
3. Display any policy findings
4. Execute configured plugins
5. Show the results

## Testing with pytest

The example is structured to work with pytest for easy integration into CI/CD pipelines:

```bash
# Run the test
pytest examples/basic/main.py::test_basic_giton_usage -v

# Run with coverage
pytest examples/basic/main.py --cov=giton -v
```
