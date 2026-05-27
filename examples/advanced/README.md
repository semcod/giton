# Advanced Giton Example

This example demonstrates advanced giton usage including:
- Custom policy configuration
- Plugin management
- Programmatic hook installation
- Interactive usage patterns

## Setup

```bash
# Install giton with dev dependencies
pip install giton[dev]

# Initialize giton
giton init
```

## Features Demonstrated

The `main.py` script shows:
- Loading and managing plugins
- Custom policy evaluation
- Installing/uninstalling git hooks
- Running multiple triggers in sequence
- Handling errors and edge cases

## Running the example

```bash
cd examples/advanced
python main.py
```

## Advanced Concepts

### Policy Configuration
Giton uses YAML-based policy files to define rules for:
- Commit message conventions
- Code quality standards
- Security checks
- Test coverage requirements

### Plugin System
Plugins can be:
- CLI tools (exec type)
- MCP servers
- REST APIs
- gRPC services

### Hook Integration
Giton installs git hooks that delegate to `giton hook <name>`:
- `pre-commit`: Run checks before committing
- `post-commit`: Analyze after commit
- `pre-push`: Final validation before pushing
