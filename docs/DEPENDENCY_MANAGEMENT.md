# Dependency Management Guide

## How Developers Track Dependencies

### 1. **Import Organization**
```python
# Standard library imports first
import os
import sys
from pathlib import Path

# Third-party imports
import numpy as np
import pandas as pd
from fastapi import FastAPI

# Local/project imports
from tools.chapter_emotion_arc import analyze
from examples.writing_analysis import writers_room
```

### 2. **Dependency Files**

#### `requirements.txt` (Production)
- Exact versions with `==` for reproducibility
- Only essential dependencies
- Generated with: `pip freeze > requirements.txt`

#### `requirements-dev.txt` (Development)
- Includes `-r requirements.txt` to inherit production deps
- Additional dev tools (pytest, black, mypy)

#### `pyproject.toml` (Modern Python)
```toml
[project]
dependencies = [
    "fastapi==0.116.1",
    "pandas==2.2.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
]
```

### 3. **Import Dependency Tools**

#### **pipdeptree** - Visualize dependency tree
```bash
pip install pipdeptree
pipdeptree --graph-output png > dependencies.png
```

#### **isort** - Organize imports
```bash
isort tools/  # Automatically sorts imports
```

#### **pylint/flake8** - Detect unused imports
```bash
flake8 --select=F401  # Find unused imports
```

### 4. **IDE Features**

Most IDEs track dependencies automatically:

- **VS Code**: 
  - Python extension shows import errors
  - "Go to Definition" (F12) to trace dependencies
  - Problems panel shows missing imports

- **PyCharm**:
  - Dependency graph visualization
  - Automatic import optimization
  - Refactoring tools update imports

### 5. **Circular Dependency Prevention**

```python
# Bad - circular import
# file1.py
from file2 import func2

# file2.py  
from file1 import func1  # Circular!

# Good - use import inside function
# file2.py
def my_function():
    from file1 import func1  # Import when needed
    return func1()
```

### 6. **Dependency Injection**

```python
# Instead of hard-coding dependencies
class Analyzer:
    def __init__(self):
        from tools.lexicon import LEXICON  # Hard-coded
        
# Use dependency injection
class Analyzer:
    def __init__(self, lexicon):
        self.lexicon = lexicon  # Injected
```

### 7. **Virtual Environments**

Keep dependencies isolated:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 8. **Docker for Complex Dependencies**

```dockerfile
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### 9. **Monitoring Tools**

- **pip-audit**: Security vulnerabilities
- **pip-check**: Version conflicts  
- **safety**: Known security issues
- **pip-licenses**: License compliance

### 10. **Documentation**

Always document:
- Why a dependency is needed
- Version constraints
- Known issues
- Alternative packages

## Best Practices

1. **Keep dependencies minimal** - Only add what you need
2. **Pin versions in production** - Avoid surprises
3. **Regular updates** - Security and bug fixes
4. **Use virtual environments** - Isolate projects
5. **Document unusual dependencies** - Help future developers
6. **Test dependency updates** - Before deploying
7. **Use dependabot** - Automated PR for updates
8. **Avoid relative imports** - Use absolute when possible
9. **Structure as packages** - Use __init__.py files
10. **CI/CD validation** - Test imports in pipeline