# Contributing to A2AFlow

Thank you for considering contributing to A2AFlow! We welcome contributions from the community to help improve and evolve the project.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## How to Contribute

### Reporting Bugs

- Ensure the bug was not already reported by searching on GitHub under Issues.
- If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements

- Check the existing issues for similar suggestions.
- Open a new issue with a clear description of the enhancement.
- Provide specific examples to help us understand the context.

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/A2AFlow.git
cd A2AFlow
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
pytest
```

## Style Guidelines

- Follow PEP 8 style guidelines.
- Use type hints for all public functions and classes.
- Write docstrings for all public functions, classes, and modules.
- Keep lines under 88 characters.
- Use black for code formatting.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
