# Documentation Index

Welcome to the AI Transactional Agent documentation. This directory contains comprehensive guides for developers, operators, and contributors.

## Quick Start Documents

For getting started quickly with the project:

### 🚀 [DOCKER.md](DOCKER.md)
Complete Docker setup guide including:
- Quick start (build and run)
- Docker architecture overview
- Troubleshooting common issues
- Database management
- Backup and monitoring

**Read this first** if you want to run the project in Docker.

### 🧪 [TESTING.md](TESTING.md)
Complete testing guide covering:
- Running tests with Docker (`make test`)
- Unit and integration tests
- Coverage reports
- Manual testing workflows
- Debugging tests

## Core Documentation

### 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md)
System architecture documentation including:
- High-level system design
- Layered architecture (Clean Architecture)
- LangGraph agent architecture
- Data persistence strategy
- API endpoints
- Complete transaction flows

**Essential reading** for understanding how the system works.

### 💻 [DEVELOPMENT.md](DEVELOPMENT.md)
Development guide containing:
- Project structure and organization
- Development roadmap and current status
- Local development setup (without Docker)
- Best practices and patterns

### 🎨 [CODE_QUALITY.md](CODE_QUALITY.md)
Code quality standards and tools:
- Ruff (linter and formatter)
- MyPy (type checking)
- Bandit (security scanning)
- Pre-commit hooks setup
- Editor configuration (VS Code, PyCharm)

### 🔄 [CI_CD.md](CI_CD.md)
CI/CD pipeline documentation:
- GitHub Actions workflows
- Automated testing
- Deployment process
- Quality gates

## Reference Documentation

Additional technical references:

### 📚 [reference/](reference/)
Deep-dive technical documents:
- **CHECKPOINTING.md**: LangGraph checkpointing explained
- **LANGGRAPH_STUDIO.md**: LangGraph Studio usage guide

### 📦 [_archive/](_archive/)
Historical documents for reference:
- Project context and requirements
- Audit reports
- Original specifications

## Documentation by Use Case

### "I want to run the project"
1. Read [DOCKER.md](DOCKER.md) - Quick Start section
2. Run `make quick-start` or `docker compose up -d --build`
3. Verify with `make health`

### "I want to understand the architecture"
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - System Architecture section
2. Review the LangGraph agent flow
3. Check API endpoints documentation

### "I want to run tests"
1. Read [TESTING.md](TESTING.md) - Quick Start section
2. Run `make test` or specific test commands
3. View coverage with `make test-cov`

### "I want to contribute code"
1. Read [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup
2. Read [CODE_QUALITY.md](CODE_QUALITY.md) - Code standards
3. Install pre-commit hooks: `make install-hooks`
4. Run tests before committing: `make test`

### "I want to deploy to production"
1. Read [CI_CD.md](CI_CD.md) - Deployment process
2. Read [DOCKER.md](DOCKER.md) - Production considerations
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) - Resilience patterns

## Project Structure

```
docs/
├── README.md              # This file - documentation index
├── ARCHITECTURE.md        # System architecture
├── TESTING.md             # Testing guide
├── DOCKER.md              # Docker setup and operations
├── DEVELOPMENT.md         # Development guide
├── CODE_QUALITY.md        # Code quality standards
├── CI_CD.md               # CI/CD pipeline
├── reference/             # Technical deep-dives
│   ├── CHECKPOINTING.md
│   └── LANGGRAPH_STUDIO.md
└── _archive/              # Historical documents
    ├── CONTEXTO.md
    ├── AUDIT_REPORT.md
    ├── PROJECT_SUMMARY.md
    └── PRUEBA_TECNICA_AI_AGENT.md
```

## Contributing to Documentation

When updating documentation:

1. **Keep docs/ organized**: Main guides in root, technical details in reference/
2. **Update this index**: Add new documents to the appropriate section
3. **Link between docs**: Cross-reference related documents
4. **Keep code examples up-to-date**: Test code snippets before committing
5. **Follow markdown conventions**: Use clear headings, code blocks, and formatting

## Need Help?

- **Issues**: https://github.com/anthropics/claude-code/issues
- **Questions**: Check docs first, then ask the team
- **Architecture questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Setup issues**: See [DOCKER.md](DOCKER.md) troubleshooting section
