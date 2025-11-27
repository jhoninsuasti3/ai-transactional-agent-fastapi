# GitHub Actions CI/CD

## 🚀 Quick Start

### Prerequisites

1. **GitHub Secrets** configurados (ver [CI_CD_SETUP.md](../docs/CI_CD_SETUP.md))
2. **AWS Account** con permisos necesarios
3. **OpenAI API Key**

### Configurar Secrets

```bash
# En GitHub: Settings → Secrets → Actions

Required secrets:
- OPENAI_API_KEY
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- PROD_POSTGRES_HOST
- PROD_POSTGRES_USER
- PROD_POSTGRES_PASSWORD
- PROD_POSTGRES_DB
- SECRET_KEY
```

## 📋 Workflows

### ✅ CI - Continuous Integration

**File:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**What it does:**
1. ✅ Runs linting (ruff)
2. ✅ Runs all tests (unit + integration)
3. ✅ Checks code coverage (≥70%)
4. ✅ Runs security scans
5. ✅ Builds Docker image

**Status Badge:**
```markdown
![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)
```

### 🚀 CD - Deploy to AWS ECS

**File:** `.github/workflows/cd-aws.yml`

**Triggers:**
- Push to `main` branch
- Manual dispatch

**What it does:**
1. ✅ Runs tests (blocks deploy if tests fail)
2. ✅ Builds Docker image
3. ✅ Pushes to ECR
4. ✅ Deploys to ECS Fargate
5. ✅ Runs smoke tests
6. ✅ Sends notifications

**Manual Deploy:**
```bash
# Via GitHub UI:
Actions → CD - Deploy to AWS → Run workflow → Select environment
```

### 🖥️ CD - Deploy to EC2

**File:** `.github/workflows/cd-ec2.yml`

**Triggers:**
- Push to `main` branch

**What it does:**
1. ✅ Runs tests
2. ✅ Creates backup
3. ✅ Deploys via SSH
4. ✅ Restarts service
5. ✅ Auto-rollback on failure

## 📊 Monitoring

### View Workflow Runs

```bash
# Via GitHub CLI
gh run list --workflow=ci.yml
gh run watch
```

### Check Logs

```bash
# Latest run
gh run view

# Specific job
gh run view --log
```

## 🔧 Local Testing

Test workflows locally before pushing:

```bash
# Install act (GitHub Actions locally)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow
act push

# Run specific job
act -j test
```

## 🐛 Troubleshooting

### Tests fail in CI but pass locally

```bash
# Use exact same environment as CI
docker run --rm -it \
  -v $(pwd):/app \
  -w /app \
  -e DATABASE_URL=postgresql://... \
  python:3.12 \
  bash -c "pip install uv && uv venv && source .venv/bin/activate && uv pip install -r requirements.txt -r requirements-dev.txt && pytest tests/"
```

### Deploy fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check ECS service
aws ecs describe-services \
  --cluster ai-transactional-agent-cluster \
  --services ai-transactional-agent-service
```

### Secrets not working

```bash
# Test secret access (locally)
echo ${{ secrets.OPENAI_API_KEY }} | base64

# Verify secret exists in GitHub
gh secret list
```

## 📚 Documentation

Full documentation: [docs/CI_CD_SETUP.md](../docs/CI_CD_SETUP.md)

## 🎯 Best Practices

1. **Never commit secrets** - Use GitHub Secrets
2. **Always run tests** before deploy
3. **Use staging environment** for testing deploys
4. **Monitor CloudWatch** logs after deploy
5. **Keep backup** before production deploys
6. **Use manual approval** for production deploys

## 🔒 Security

- All secrets encrypted at rest
- Secrets only accessible during workflow runs
- Secrets never exposed in logs
- AWS credentials rotated regularly
- Least privilege IAM policies

## 📈 Status Badges

Add to your README.md:

```markdown
[![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
[![CD - AWS](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/cd-aws.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/cd-aws.yml)
[![Coverage](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)
```

## 🆘 Support

- GitHub Actions Docs: https://docs.github.com/en/actions
- AWS ECS Docs: https://docs.aws.amazon.com/ecs/
- Project Issues: https://github.com/YOUR_USERNAME/YOUR_REPO/issues
