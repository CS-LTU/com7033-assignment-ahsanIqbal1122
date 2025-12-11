# Contributing to Stroke Prediction System

Thank you for your interest in contributing to this project. This guide will help you get started.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Security](#security)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Flask and SQLite
- Familiarity with HTML/CSS/JavaScript

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/com7033-assignment-ahsanIqbal1122.git
   cd com7033-assignment-ahsanIqbal1122
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122.git
   ```

## Development Environment

### Initial Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python -c "from database.db import init_db; init_db()"
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application at `http://localhost:5000`

### Default Credentials

- **Admin:** username: `admin`, password: `Admin123!`

## Project Structure

```
stroke_pass_app/
├── app.py                  # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── database/
│   ├── db.py             # SQLite database operations
│   └── mongo.py          # MongoDB operations (optional)
├── routes/
│   ├── auth_routes.py    # Authentication endpoints
│   ├── dashboard_routes.py  # Dashboard endpoints
│   └── patient_routes.py    # Patient management endpoints
├── services/
│   ├── auth_service.py   # Authentication business logic
│   └── logger_service.py # Logging utilities
├── templates/            # HTML templates
└── static/              # CSS, JS, images

```

## Coding Standards

### Python Code Style

- Follow PEP 8 style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules

### Documentation

- Add docstrings to all public functions and classes
- Include parameter types and return values
- Document security considerations where applicable
- Update API_DOCUMENTATION.md for API changes

### Example Docstring

```python
def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Args:
        password (str): The password to validate
        
    Returns:
        Tuple[bool, str]: 
            - True if password is valid, False otherwise
            - Error message if invalid, empty string if valid
    
    Security Requirements:
    - Minimum 8 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one digit (0-9)
    - At least one special character (@$!%*?&#)
    """
    # Implementation
```

### HTML/CSS

- Use semantic HTML5 elements
- Follow Bootstrap conventions for styling
- Keep inline styles to a minimum
- Use meaningful class and ID names

### Security Guidelines

- Never commit sensitive data (passwords, API keys, secrets)
- Use parameterized queries to prevent SQL injection
- Validate and sanitize all user input
- Use CSRF protection on all forms
- Hash passwords with scrypt before storage
- Follow OWASP security best practices

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Writing Tests

- Write tests for all new features
- Include both positive and negative test cases
- Test edge cases and error conditions
- Maintain test coverage above 80%

### Test Example

```python
def test_password_validation():
    """Test password strength validation"""
    # Valid password
    is_valid, error = validate_password_strength("Pass123!")
    assert is_valid == True
    assert error == ""
    
    # Invalid password (too short)
    is_valid, error = validate_password_strength("Pass1!")
    assert is_valid == False
    assert "8 characters" in error
```

## Submitting Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-patient-search`
- `bugfix/fix-login-redirect`
- `security/update-password-validation`
- `docs/update-readme`

### Commit Messages

Write clear, concise commit messages:

```
Short summary (50 chars or less)

Detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues: "Fixes #123" or "Related to #456"
```

### Pull Request Process

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference any related issues
   - Screenshots for UI changes
   - List of testing performed

5. Respond to review feedback promptly

6. Once approved, your PR will be merged

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts with main branch
- [ ] Commit messages are clear and descriptive

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Description:** Clear summary of the issue
2. **Steps to Reproduce:**
   - Step 1
   - Step 2
   - Step 3
3. **Expected Behavior:** What should happen
4. **Actual Behavior:** What actually happens
5. **Environment:**
   - OS: (e.g., Windows 11, Ubuntu 22.04)
   - Python version: (e.g., 3.10.5)
   - Browser: (e.g., Chrome 120)
6. **Screenshots:** If applicable
7. **Error Messages:** Complete error logs

### Feature Requests

For feature requests, include:

1. **Problem:** What problem does this solve?
2. **Proposed Solution:** How should it work?
3. **Alternatives:** Other solutions considered
4. **Additional Context:** Any other relevant information

## Security

### Reporting Vulnerabilities

**Do not** report security vulnerabilities through public GitHub issues.

Instead:
1. Email the course instructor directly
2. Include detailed steps to reproduce
3. Describe the potential impact
4. Wait for confirmation before public disclosure

### Security Best Practices

When contributing code:
- Never hardcode credentials or secrets
- Use environment variables for sensitive data
- Validate all user input
- Use parameterized SQL queries
- Follow principle of least privilege
- Keep dependencies up to date

## Code Review

All contributions go through code review. Reviewers will check:

- Code quality and style
- Test coverage
- Security considerations
- Documentation completeness
- Performance implications

Be open to feedback and willing to make changes.

## Community Guidelines

- Be respectful and professional
- Help others when you can
- Give constructive feedback
- Follow the code of conduct
- Focus on what is best for the project

## Getting Help

If you need help:
- Check existing documentation
- Search closed issues
- Open a new issue with the "question" label
- Contact the project maintainer

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Author:** Just Ahsan  
**Course:** COM7033 - Secure Programming  
**Institution:** Leeds Trinity University
