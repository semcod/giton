"""
Integration tests for giton with pytest.

This demonstrates how giton can be integrated into a testing workflow.
"""

import os
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo, check=True, capture_output=True
        )
        
        yield repo


def test_giton_installation():
    """Test that giton is installed."""
    result = subprocess.run(
        ["giton", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_giton_policy_check(temp_repo):
    """Test giton policy check command."""
    # Create a sample file
    (temp_repo / "test.py").write_text("print('hello')")
    
    # Stage the file
    subprocess.run(
        ["git", "add", "test.py"],
        cwd=temp_repo,
        check=True,
        capture_output=True
    )
    
    # Run giton policy check
    result = subprocess.run(
        ["giton", "policy", "check", "--trigger", "pre-commit"],
        cwd=temp_repo,
        capture_output=True,
        text=True
    )
    
    # Should not fail (no policies configured)
    assert result.returncode == 0


def test_giton_policy_init(temp_repo):
    """Test giton policy init command."""
    result = subprocess.run(
        ["giton", "policy", "init"],
        cwd=temp_repo,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert (temp_repo / ".giton" / "config.yaml").exists()


def test_giton_plugin_list():
    """Test giton plugin list command."""
    result = subprocess.run(
        ["giton", "plugin", "list"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0


def test_sample_project_tests():
    """Run tests on the sample project."""
    sample_project = Path(__file__).parent / "sample_project"
    
    if not sample_project.exists():
        pytest.skip("Sample project not found")
    
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"],
        cwd=sample_project,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    print(result.stderr)
    
    # All tests should pass
    assert result.returncode == 0


def test_giton_with_pytest_integration(temp_repo):
    """Test giton integration with pytest workflow."""
    # Create a sample Python file
    (temp_repo / "src").mkdir()
    (temp_repo / "src" / "__init__.py").write_text("")
    (temp_repo / "src" / "module.py").write_text("""
def hello():
    return "world"
""")
    
    # Create a test file
    (temp_repo / "tests").mkdir()
    (temp_repo / "tests" / "__init__.py").write_text("")
    (temp_repo / "tests" / "test_module.py").write_text("""
from src.module import hello

def test_hello():
    assert hello() == "world"
""")
    
    # Initialize giton
    subprocess.run(
        ["giton", "policy", "init"],
        cwd=temp_repo,
        check=True,
        capture_output=True
    )
    
    # Stage files
    subprocess.run(
        ["git", "add", "."],
        cwd=temp_repo,
        check=True,
        capture_output=True
    )
    
    # Run policy check
    policy_result = subprocess.run(
        ["giton", "policy", "check", "--trigger", "pre-commit"],
        cwd=temp_repo,
        capture_output=True,
        text=True
    )
    
    print("Policy check output:")
    print(policy_result.stdout)
    assert policy_result.returncode == 0
    
    # Run tests
    test_result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"],
        cwd=temp_repo,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(temp_repo)}
    )
    
    print("Test output:")
    print(test_result.stdout)
    
    assert test_result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
