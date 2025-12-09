# Contributing to Stroke Pass

Thank you for your interest in contributing to the Stroke Pass application! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Security Guidelines](#security-guidelines)

## Code of Conduct

This project follows professional software engineering practices. We expect all contributors to:

- Be respectful and constructive in communications
- Follow security best practices
- Write clean, documented, and tested code
- Review others' contributions thoughtfully

## Development Setup

### Prerequisites

- Python 3.10 or higher
- MongoDB 4.0 or higher
- Git

### Local Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122.git
   cd com7033-assignment-ahsanIqbal1122
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python -c "from database.db import init_db; init_db()"
   ```

6. **Run tests to verify setup:**
   ```bash
   pytest tests/ -v
   ```

## Branching Strategy

We follow the **Git Flow** branching model for organized and collaborative development.

### Branch Types

#### `main` Branch
- **Purpose:** Production-ready code
- **Protection:** Protected, requires pull request reviews
- **Deployment:** Automatically deployed to production
- **Direct commits:** ❌ Never commit directly

#### `develop` Branch
- **Purpose:** Integration branch for features
- **Protection:** Protected, requires pull request reviews
- **Integration:** All feature branches merge here first
- **Direct commits:** ❌ Use feature branches

#### Feature Branches
- **Naming:** `feature/<feature-name>`
- **Example:** `feature/add-rate-limiting`
- **Purpose:** Develop new features
- **Base:** `develop`
- **Merge to:** `develop`

#### Bugfix Branches
- **Naming:** `bugfix/<bug-description>`
- **Example:** `bugfix/fix-csrf-token-missing`
- **Purpose:** Fix bugs in development
- **Base:** `develop`
- **Merge to:** `develop`

#### Hotfix Branches
- **Naming:** `hotfix/<critical-issue>`
- **Example:** `hotfix/security-patch-sql-injection`
- **Purpose:** Emergency fixes for production
- **Base:** `main`
- **Merge to:** `main` AND `develop`

#### Release Branches
- **Naming:** `release/v<version>`
- **Example:** `release/v1.1.0`
- **Purpose:** Prepare for production release
- **Base:** `develop`
- **Merge to:** `main` AND `develop`

### Workflow Examples

#### Creating a New Feature

```bash
# 1. Update develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-password-reset

# 3. Make changes and commit
git add .
git commit -m "feat: Add password reset functionality"

# 4. Push feature branch
git push origin feature/add-password-reset

# 5. Create pull request on GitHub
# develop <- feature/add-password-reset
```

#### Creating a Hotfix

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/fix-login-vulnerability

# 2. Fix issue and commit
git add .
git commit -m "fix: Patch SQL injection vulnerability in login"

# 3. Push hotfix
git push origin hotfix/fix-login-vulnerability

# 4. Create TWO pull requests:
#    - main <- hotfix/fix-login-vulnerability
#    - develop <- hotfix/fix-login-vulnerability
```

## Commit Message Guidelines

We follow the **Conventional Commits** specification for clear and meaningful commit history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: Add user profile editing` |
| `fix` | Bug fix | `fix: Correct CSRF token validation` |
| `docs` | Documentation | `docs: Update API reference` |
| `style` | Code formatting | `style: Format code with Black` |
| `refactor` | Code restructuring | `refactor: Extract auth logic to service layer` |
| `test` | Add/update tests | `test: Add integration tests for login flow` |
| `chore` | Maintenance | `chore: Update dependencies` |
| `perf` | Performance improvement | `perf: Optimize database queries` |
| `security` | Security fix | `security: Add rate limiting to login endpoint` |

### Examples

#### Simple commit:
```bash
git commit -m "feat: Add password strength indicator"
```

#### Detailed commit:
```bash
git commit -m "feat: Add rate limiting to authentication endpoints

Implements Flask-Limiter to prevent brute force attacks:
- Login endpoint: 5 attempts per minute
- Registration endpoint: 3 attempts per hour
- Password reset: 3 attempts per hour

Security Impact: Prevents automated credential stuffing attacks"
```

#### Breaking change:
```bash
git commit -m "feat!: Change password hashing to Argon2

BREAKING CHANGE: Existing password hashes will need to be migrated.
Run 'python migrate_passwords.py' after deployment."
```

### Scope Examples

- `auth`: Authentication-related changes
- `patient`: Patient management features
- `database`: Database operations
- `security`: Security enhancements
- `ui`: User interface changes
- `api`: API endpoints

## Pull Request Process

### Creating a Pull Request

1. **Ensure branch is up to date:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout your-feature-branch
   git rebase develop
   ```

2. **Run tests locally:**
   ```bash
   pytest tests/ -v --cov
   ```

3. **Push changes:**
   ```bash
   git push origin your-feature-branch
   ```

4. **Create PR on GitHub with:**
   - Descriptive title (follows commit conventions)
   - Detailed description of changes
   - Link to related issues
   - Screenshots (if UI changes)
   - Test results

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that breaks existing functionality)
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Test coverage maintained/improved

## Security Checklist
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] CSRF protection in place
- [ ] Authentication/authorization checks added
- [ ] Sensitive data not logged

## Screenshots (if applicable)
Add screenshots here

## Reviewer Notes
Any specific areas to focus on during review
```

### Review Process

1. **Automated checks must pass:**
   - All tests pass
   - Code coverage meets threshold (>80%)
   - No security vulnerabilities detected

2. **Manual code review:**
   - At least one approval required
   - Address all reviewer comments
   - Update PR based on feedback

3. **Merge strategy:**
   - Squash and merge (for feature branches)
   - Merge commit (for release branches)

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some project-specific conventions.

#### Code Formatting

- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters**
- Use **Black** for automatic formatting:
  ```bash
  black app.py routes/ services/
  ```

#### Naming Conventions

```python
# Classes: PascalCase
class AuthService:
    pass

# Functions/methods: snake_case
def authenticate_user(username, password):
    pass

# Constants: UPPER_SNAKE_CASE
SECRET_KEY = "your-secret-key"

# Private methods: _leading_underscore
def _hash_password(password):
    pass
```

#### Documentation

All modules, classes, and functions must have docstrings:

```python
def create_patient_report(user_id: int, report_data: Dict) -> Tuple[bool, str]:
    """
    Create a new patient report in the database.
    
    Args:
        user_id (int): ID of the user creating the report
        report_data (Dict): Patient health data
        
    Returns:
        Tuple[bool, str]: (success, message/report_id)
        
    Raises:
        ValueError: If required fields are missing
        DatabaseError: If database operation fails
        
    Example:
        >>> success, report_id = create_patient_report(1, {...})
        >>> if success:
        ...     print(f"Report {report_id} created")
    """
    # Implementation
    pass
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, Dict, List, Tuple

def get_user_by_id(user_id: int) -> Optional[Dict[str, any]]:
    # Implementation
    pass
```

## Testing Requirements

### Test Coverage

- **Minimum coverage:** 80%
- **Target coverage:** 90%+
- **Critical paths:** 100% (authentication, authorization, data access)

### Test Types

1. **Unit Tests** (`tests/test_*.py`)
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution (<1ms per test)

2. **Integration Tests** (`tests/test_integration.py`)
   - Test component interactions
   - Use test database
   - Complete workflows

3. **Security Tests** (`tests/test_security.py`)
   - Authentication/authorization
   - Input validation
   - SQL injection prevention
   - CSRF protection

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=. --cov-report=html

# Specific test file
pytest tests/test_integration.py -v

# Specific test function
pytest tests/test_auth.py::test_login_success -v
```

### Writing Tests

```python
import pytest

class TestAuthService:
    """Test authentication service."""
    
    def test_authenticate_user_success(self, auth_service, test_user):
        """
        Test successful user authentication.
        
        Given: A registered and approved user
        When: Correct credentials provided
        Then: Authentication succeeds
        """
        success, user_data, error = auth_service.authenticate_user(
            test_user['username'],
            test_user['password']
        )
        
        assert success is True
        assert user_data['username'] == test_user['username']
        assert error == ""
```

## Security Guidelines

### Secure Coding Practices

1. **Input Validation:**
   ```python
   # ✅ Good
   age = int(request.form['age'])
   if age < 0 or age > 150:
       return "Invalid age", 400
   
   # ❌ Bad
   age = request.form['age']  # No validation
   ```

2. **SQL Injection Prevention:**
   ```python
   # ✅ Good (parameterized query)
   cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   
   # ❌ Bad (string formatting)
   cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
   ```

3. **Password Security:**
   ```python
   # ✅ Good (scrypt hashing)
   from werkzeug.security import generate_password_hash
   password_hash = generate_password_hash(password, method='scrypt')
   
   # ❌ Bad (plain text)
   password = request.form['password']
   ```

4. **CSRF Protection:**
   ```html
   <!-- ✅ Good -->
   <form method="post">
       <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
       <!-- form fields -->
   </form>
   
   <!-- ❌ Bad (no CSRF token) -->
   <form method="post">
       <!-- form fields -->
   </form>
   ```

### Security Review Checklist

Before submitting PR, verify:

- [ ] All user inputs are validated
- [ ] SQL queries use parameterized statements
- [ ] Passwords are hashed (never stored as plain text)
- [ ] CSRF tokens present on all forms
- [ ] Authentication required for protected routes
- [ ] Authorization checks verify user permissions
- [ ] Sensitive data not logged
- [ ] Error messages don't leak information
- [ ] Rate limiting on sensitive endpoints
- [ ] Session cookies are HTTP-only and secure

## Questions?

If you have questions about contributing, please:

1. Check existing documentation
2. Search GitHub issues
3. Open a new issue with the `question` label

## License

By contributing to this project, you agree that your contributions will be licensed under the project's existing license.

---

**Thank you for contributing to Stroke Pass!** 🎉
