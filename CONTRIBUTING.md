# Contributing to Amazon PA-API 5.0 Python SDK

Thank you for your interest in contributing to the **Amazon PA-API 5.0 Python SDK**! This library helps developers interact with Amazon’s Product Advertising API (PA-API) 5.0, and your contributions can make it even better. Whether you’re a beginner or an experienced coder, we welcome your help with bug fixes, new features, documentation improvements, or tests. This guide will walk you through the process step-by-step, making it easy to get started.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Setting Up Your Development Environment](#setting-up-your-development-environment)
3. [Code Structure](#code-structure)
4. [Writing Code](#writing-code)
5. [Running Tests](#running-tests)
6. [Submitting a Pull Request](#submitting-a-pull-request)
7. [Code Style and Guidelines](#code-style-and-guidelines)
8. [Reporting Bugs](#reporting-bugs)
9. [Suggesting Features](#suggesting-features)
10. [Community and Support](#community-and-support)

## Getting Started

Before you contribute, take a moment to understand the project:
- **What is this SDK?** It’s a Python library for Amazon’s PA-API 5.0, allowing developers to search for products, fetch details, get variations, and explore categories on Amazon.
- **Who can contribute?** Anyone! Whether you’re fixing a typo in the README, adding a test, or implementing a new feature, all contributions are valuable.
- **Where is the code?** The project is hosted on GitHub at [rajpurohithitesh/amazon-paapi5-python-sdk](https://github.com/rajpurohithitesh/amazon-paapi5-python-sdk).

To contribute, you’ll:
1. Fork the repository.
2. Set up your local development environment.
3. Make changes (code, tests, docs, etc.).
4. Test your changes.
5. Submit a pull request (PR).

Don’t worry if you’re new to open-source—this guide will explain everything!

## Setting Up Your Development Environment

Follow these steps to set up the project on your computer:

### 1. Prerequisites
You need:
- **Python 3.9 or higher**: Download from [python.org](https://www.python.org/downloads/).
- **Git**: Install from [git-scm.com](https://git-scm.com/downloads).
- A **GitHub account**: Sign up at [github.com](https://github.com).

Verify Python and Git are installed:
```bash
python --version  # Should output Python 3.9 or higher
git --version     # Should output git version
```

### 2. Fork the Repository
1. Go to [rajpurohithitesh/amazon-paapi5-python-sdk](https://github.com/rajpurohithitesh/amazon-paapi5-python-sdk).
2. Click the **Fork** button (top-right) to create a copy of the repository under your GitHub account.
3. Clone your forked repository to your computer:
   ```bash
   git clone https://github.com/YOUR_USERNAME/amazon-paapi5-python-sdk.git
   cd amazon-paapi5-python-sdk
   ```
   Replace `YOUR_USERNAME` with your GitHub username.

### 3. Create a Virtual Environment
A virtual environment keeps your project’s dependencies separate from your system’s Python. Create one:
```bash
python -m venv venv
```
Activate it:
- On Windows: `venv\Scripts\activate`
- On macOS/Linux: `source venv/bin/activate`

Your terminal should now show `(venv)`.

### 4. Install Dependencies
Install the project’s dependencies, including development tools:
```bash
pip install -r requirements.txt
```

This installs:
- `requests`, `aiohttp`, `cachetools` (core dependencies).
- `redis` (optional, for caching).
- `pytest`, `pytest-asyncio` (for testing).

### 5. Verify Setup
Run the tests to ensure everything is set up correctly:
```bash
pytest tests/
```
If all tests pass, you’re ready to start coding!

## Code Structure

The project is organized to be easy to navigate. Here’s what each part does:

- **`src/amazon_paapi5/`**: The main library code.
  - `__init__.py`: Sets the library version (`1.0.6`).
  - `client.py`: The `Client` class that makes API calls, handles throttling, caching, and authentication.
  - `config.py`: Stores configuration (credentials, marketplace, etc.) and supports 18 Amazon marketplaces.
  - `signature.py`: Generates AWS V4 signatures for secure API requests.
  - `resources.py`: Lists valid API resources (e.g., `ItemInfo.Title`) and validates them.
  - `models/`: Defines request and response objects for each API operation (e.g., `SearchItemsRequest`).
  - `utils/`: Helper classes for throttling, caching, and async operations.
  - `exceptions.py`: Defines custom errors (`AmazonAPIException`).

- **`tests/`**: Unit tests to verify the library works.
- **`examples/`**: Example scripts showing how to use the library.
- **`setup.py`**: Configures the library for `pip` installation.
- **`requirements.txt`**: Lists dependencies.
- **`.gitignore`**: Ignores temporary files (e.g., `__pycache__`).
- **`README.md`**: Main documentation (you’re reading it!).
- **`CONTRIBUTING.md`**: This file.
- **`LICENSE`**: Apache-2.0 License.

## Writing Code

When you’re ready to make changes, follow these steps:

### 1. Create a Branch
Create a new branch for your changes:
```bash
git checkout -b my-feature-branch
```
Use a descriptive name, like `fix-bug-in-cache` or `add-new-resource`.

### 2. Make Changes
Edit the files in your editor (e.g., VS Code, PyCharm). Here are common tasks:

- **Fix a Bug**: Find the relevant file (e.g., `client.py` for API issues) and make the fix. Add a test in `tests/` to prevent the bug from recurring.
- **Add a Feature**: For example, to add a new resource, update `resources.py` and the relevant model (e.g., `search_items.py`). Add a test and an example.
- **Improve Documentation**: Edit `README.md` to clarify instructions or add examples.
- **Add Tests**: Write new tests in `tests/` to cover your changes.

### 3. Test Your Changes
Run the tests to ensure your changes didn’t break anything:
```bash
pytest tests/
```
If a test fails, debug the issue and fix it before proceeding.

### 4. Commit Your Changes
Stage and commit your changes with a clear message:
```bash
git add .
git commit -m "Fixed bug in cache expiration logic"
```
Use a descriptive message that explains what you did.

## Running Tests

The SDK uses `pytest` for testing. Tests are located in the `tests/` folder and cover:
- Client initialization (`test_client.py`).
- API operations (`test_search_items.py`, `test_get_items.py`, etc.).
- Caching (`test_cache.py`).
- Configuration (`test_config.py`).

To run all tests:
```bash
pytest tests/
```

To run a specific test file:
```bash
pytest tests/test_client.py
```

To add a new test:
1. Create or edit a file in `tests/` (e.g., `test_new_feature.py`).
2. Write test functions using `pytest` assertions.
3. Use the `@pytest.mark.asyncio` decorator for async tests.

Example test:
```python
import pytest
from amazon_paapi5.models.search_items import SearchItemsRequest

def test_search_items_request():
    request = SearchItemsRequest(keywords="Laptop", search_index="Electronics")
    assert request.keywords == "Laptop"
```

## Submitting a Pull Request

Once your changes are ready, submit a pull request (PR):

1. **Push Your Branch**:
   ```bash
   git push origin my-feature-branch
   ```

2. **Create a Pull Request**:
   - Go to your forked repository on GitHub.
   - You’ll see a prompt to create a PR for your branch. Click **Compare & pull request**.
   - Write a clear title and description:
     - **Title**: E.g., “Fix cache expiration bug”.
     - **Description**: Explain what you changed, why, and any relevant details (e.g., “Fixed a bug where cache entries weren’t expiring. Added test in `test_cache.py`. Closes #123”).
   - Select the `main` branch of `rajpurohithitesh/amazon-paapi5-python-sdk` as the base.

3. **Wait for Review**:
   - The maintainer (Hitesh Rajpurohit) will review your PR.
   - You may be asked to make changes. Update your branch and push again; the PR will update automatically.
   - Once approved, your changes will be merged!

## Code Style and Guidelines

To keep the codebase consistent and readable:

- **Follow PEP 8**: Use Python’s style guide ([PEP 8](https://www.python.org/dev/peps/pep-0008/)).
  - 4 spaces for indentation.
  - Maximum line length: 79 characters.
  - Use descriptive variable names (e.g., `access_key` instead of `ak`).
- **Type Hints**: Use type hints (e.g., `def get(self, key: str) -> Optional[Any]`) for better code clarity.
- **Docstrings**: Add docstrings to all classes, methods, and functions:
  ```python
  def set_marketplace(self, marketplace: str) -> None:
      """Set the marketplace and update region and host accordingly."""
  ```
- **Tests**: Every change should include a test. Aim for 100% test coverage.
- **Commit Messages**: Use clear, concise messages in the format:
  - `Fix: Description of the fix`
  - `Feature: Description of the new feature`
  - `Docs: Description of documentation update`
- **No Unnecessary Dependencies**: Avoid adding new dependencies unless absolutely necessary.

## Reporting Bugs

If you find a bug:
1. Check the [GitHub Issues](https://github.com/rajpurohithitesh/amazon-paapi5-python-sdk/issues) to see if it’s already reported.
2. If not, open a new issue:
   - **Title**: E.g., “Cache does not expire after TTL”.
   - **Description**: Include:
     - What happened (e.g., “Cache entries persist beyond 3600 seconds”).
     - Steps to reproduce (e.g., “Run `search_items` twice within 1 hour”).
     - Expected behavior (e.g., “Cache should expire”).
     - Environment (e.g., Python 3.9, Windows 10).
   - **Labels**: Add the `bug` label.

## Suggesting Features

To propose a new feature:
1. Open a GitHub issue with the `enhancement` label.
2. Describe the feature:
   - What it does (e.g., “Add support for Memcached caching”).
   - Why it’s useful (e.g., “Improves performance for distributed systems”).
   - How it could be implemented (e.g., “Add a `MemcachedCache` class in `utils/cache.py`”).
3. Discuss with the community before starting work to ensure it aligns with the project’s goals.

## Community and Support

We’re here to help you succeed as a contributor:
- **GitHub Issues**: For bugs, features, or questions, use [GitHub Issues](https://github.com/rajpurohithitesh/amazon-paapi5-python-sdk/issues).
- **Maintainer**: Contact Hitesh Rajpurohit via GitHub for guidance.
- **Community**: Engage with other contributors in issue discussions or PRs.

If you’re new to open-source, don’t be afraid to ask questions! We value your enthusiasm and are happy to guide you through the process.

Thank you for helping make the Amazon PA-API 5.0 Python SDK better for everyone!
