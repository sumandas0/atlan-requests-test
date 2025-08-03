# Contributing to Atlan Requests Middleware

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for package management
- Docker or Podman for containerization
- kubectl for Kubernetes testing (optional)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-org/atlan-requests-test.git
cd atlan-requests-test
```

2. **Install dependencies**
```bash
uv sync --group dev
```

3. **Run tests**
```bash
# Set required environment variables
export AWS_ROLE_ARN="arn:aws:iam::123456789012:role/test-role"
export S3_BUCKET_NAME="test-bucket"

# Run tests
uv run pytest tests/ -v
```

4. **Start development server**
```bash
uv run uvicorn app.main:app --reload
```

5. **Test with container**
```bash
# Build and test
./test-podman.sh  # or use Docker equivalent
```

## Code Quality

### Before Submitting

Run these checks locally:

```bash
# Lint code
uv run ruff check app/ tests/

# Format code
uv run black app/ tests/

# Run tests
uv run pytest tests/ -v
```

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Testing

- Write tests for new features
- Maintain test coverage above 80%
- Test both positive and negative cases
- Include integration tests for new endpoints

## Contribution Workflow

### 1. Create an Issue

For bugs or features, create an issue first to discuss:
- Use appropriate issue templates
- Provide detailed description
- Include configuration details for bugs
- Discuss implementation approach for features

### 2. Fork and Branch

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/atlan-requests-test.git

# Create feature branch
git checkout -b feature/your-feature-name
```

### 3. Development

- Make your changes
- Add/update tests
- Update documentation
- Ensure all checks pass

### 4. Commit Guidelines

Use conventional commit format:

```
feat: add new endpoint matching pattern
fix: resolve S3 upload timeout issue
docs: update deployment instructions
test: add integration tests for selective logging
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

### 5. Pull Request

- Use the PR template
- Link related issues
- Include testing instructions
- Request appropriate reviews

## Security

### Reporting Vulnerabilities

**Do not** create public issues for security vulnerabilities.

Instead:
1. Email security@atlan.com
2. Include detailed description
3. Provide steps to reproduce
4. Allow time for fix before disclosure

### Security Guidelines

- No hardcoded credentials
- Use environment variables for secrets
- Validate all inputs
- Follow container security best practices
- Keep dependencies updated

## Documentation

### Types of Documentation

1. **Code Documentation**
   - Docstrings for functions/classes
   - Inline comments for complex logic
   - Type hints

2. **User Documentation**
   - README updates
   - Configuration examples
   - Deployment guides

3. **Developer Documentation**
   - Architecture decisions
   - API documentation
   - Troubleshooting guides

### Writing Guidelines

- Clear and concise language
- Include code examples
- Keep examples up to date
- Use proper markdown formatting

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH

### Release Workflow

1. **Prepare Release**
   - Update version in `pyproject.toml`
   - Update CHANGELOG.md
   - Test thoroughly

2. **Create Release**
   - Tag with `git tag v1.0.0`
   - Push tags `git push --tags`
   - GitHub Actions builds and publishes

3. **Container Images**
   - Automatically built on tag push
   - Published to GHCR
   - Multi-architecture support

## Community

### Communication

- GitHub Discussions for questions
- Issues for bugs and features
- Pull requests for code changes
- Email for security issues

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Getting Help

### Development Issues

1. Check existing issues and discussions
2. Review documentation
3. Ask in GitHub Discussions
4. Create detailed issue if needed

### Common Issues

**Container build fails:**
- Check Docker/Podman installation
- Verify uv.lock is up to date
- Review build logs

**Tests failing:**
- Set required environment variables
- Check Python version (3.11+)
- Update dependencies with `uv sync`

**Kubernetes deployment issues:**
- Verify kubectl access
- Check secret values are base64 encoded
- Review pod logs

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS SDK for Python](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Container Best Practices](https://docs.docker.com/develop/dev-best-practices/)

Thank you for contributing! 🚀