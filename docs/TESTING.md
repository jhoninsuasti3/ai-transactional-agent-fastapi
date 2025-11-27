# Testing Guide

Complete guide for testing the AI Transactional Agent project, including unit tests, integration tests, and manual testing workflows.

## Quick Start

```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# View detailed coverage report
make test-cov
```

## Test Architecture

The project includes:
- **Unit Tests**: 200+ tests verifying individual components
- **Integration Tests**: 50+ tests verifying complete flows
- **Coverage Goal**: 70% (currently ~78%)

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── agents/            # Agent tests (LangGraph)
│   │   ├── nodes/        # Node tests (conversation, extractor, etc.)
│   │   ├── tools/        # Tool tests (validate, execute, etc.)
│   │   └── prompts/      # Prompt tests
│   └── orchestrator/      # Orchestrator tests (FastAPI)
│       ├── api/          # API tests (routers, middlewares)
│       ├── domain/       # Domain entity tests
│       └── infrastructure/ # Client and repository tests
└── integration/            # Integration tests
    ├── test_chat_integration.py
    ├── test_transaction_flows.py
    └── test_complete_flows.py
```

## Running Tests with Docker

### Option 1: Using Makefile (Recommended)

```bash
# View available commands
make help

# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run with detailed coverage report
make test-cov

# Run specific test file
make test-specific TEST=tests/unit/orchestrator/test_settings.py
```

### Option 2: Docker Compose Direct

```bash
# Build test image
docker compose -f docker-compose.yml -f docker-compose.test.yml build orchestrator-test

# Run all tests
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test

# Run unit tests only
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest tests/unit/ -v

# Run integration tests only
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest tests/integration/ -v

# Run specific test with filter
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest -k "test_chat" -v
```

## Running Tests Locally

If you have a local environment configured with `uv`:

```bash
# Install development dependencies
uv sync

# Run all tests
uv run pytest -v

# With coverage
uv run pytest --cov=apps --cov-report=term-missing --cov-report=html

# Run specific tests
uv run pytest tests/unit/orchestrator/ -v
uv run pytest tests/integration/test_chat_integration.py -v

# Filter by test name
uv run pytest -k "test_settings" -v
```

## Coverage Reports

### View Coverage in Terminal

```bash
make test-cov
```

Expected output:
```
tests/unit/orchestrator/test_settings.py::test_settings_loads_env_vars PASSED
tests/unit/orchestrator/test_settings.py::test_cors_origins_parsing PASSED
...
---------- coverage: platform linux, python 3.12.12 -----------
Name                                             Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
apps/orchestrator/core/config.py                    75      5    93%   46-49
apps/orchestrator/core/logging.py                   42      8    81%   15-22
...
-----------------------------------------------------------------------------
TOTAL                                              1974    432    78%
```

### View HTML Report

```bash
# Generate HTML coverage report
make test-cov

# Open report (created in ./htmlcov/)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Tests by Category

### Agent Unit Tests

```bash
# All agent tests
make test-specific TEST=tests/unit/agents/

# Specific node tests
make test-specific TEST=tests/unit/agents/nodes/test_conversation_node.py
make test-specific TEST=tests/unit/agents/nodes/test_extractor_node.py
make test-specific TEST=tests/unit/agents/nodes/test_validator_node.py

# Tool tests
make test-specific TEST=tests/unit/agents/tools/test_validate_transaction.py
make test-specific TEST=tests/unit/agents/tools/test_execute_transaction.py
```

### Orchestrator Unit Tests

```bash
# API tests
make test-specific TEST=tests/unit/orchestrator/api/

# Domain tests
make test-specific TEST=tests/unit/orchestrator/domain/

# Infrastructure tests
make test-specific TEST=tests/unit/orchestrator/infrastructure/
```

### Integration Tests

```bash
# Complete chat flow
make test-specific TEST=tests/integration/test_chat_integration.py

# Transaction flows
make test-specific TEST=tests/integration/test_transaction_flows.py

# End-to-end tests
make test-specific TEST=tests/integration/test_complete_flows.py
```

## Debugging Tests

### View Detailed Output

```bash
# With prints and logs
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest -v -s

# With DEBUG level logs
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest -v --log-cli-level=DEBUG
```

### Run Single Test

```bash
# By full test name
make test-specific TEST=tests/unit/orchestrator/test_settings.py::test_cors_origins_parsing

# By partial name match
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest -k "settings" -v
```

### Debug with pdb

```bash
# Add breakpoint in code
import pdb; pdb.set_trace()

# Run test in interactive mode
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
  .venv/bin/pytest tests/path/to/test.py -v -s
```

## Fast Testing Tips

For rapid development, run only tests you need:

```bash
# Only failed tests from last run
pytest --lf  # last-failed

# Only tests from specific module
pytest tests/unit/orchestrator/core/

# Skip slow tests
pytest -m "not slow"

# Set timeout for hanging tests
pytest --timeout=30
```

## Test Configuration

### pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=apps",
    "--cov-report=html",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=xml",
    "--cov-fail-under=70",
    "-v",
    "-ra",
]
```

### Available Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_complex_operation():
    ...

# Mark integration tests
@pytest.mark.integration
def test_full_flow():
    ...

# Mark E2E tests
@pytest.mark.e2e
def test_end_to_end():
    ...
```

## Manual Testing Workflows

### Prerequisites

```bash
# Start all services
docker compose up --build -d

# Verify all services are running
docker compose ps

# Should show: postgres (healthy), mock-api (healthy), orchestrator (healthy)
```

### Verify Health Checks

```bash
# Orchestrator health
curl http://localhost:8002/health

# Mock API health
curl http://localhost:8001/health

# Chat router health
curl http://localhost:8002/api/v1/chat/health
```

### Test Mock API (Isolated)

#### Validate Transaction

```bash
# Successful validation
curl -X POST http://localhost:8001/api/v1/transactions/validate \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_phone": "3001234567",
    "amount": 50000,
    "currency": "COP"
  }'

# Expected response:
# {
#   "is_valid": true,
#   "validation_id": "VAL-xxxxx",
#   "message": "Transaction can proceed"
# }
```

#### Execute Transaction

```bash
# Execute transaction
curl -X POST http://localhost:8001/api/v1/transactions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "validation_id": "VAL-12345",
    "recipient_phone": "3001234567",
    "amount": 50000,
    "currency": "COP"
  }'

# Expected response:
# {
#   "transaction_id": "TXN-xxxxx",
#   "status": "completed",
#   "message": "Transaction completed successfully"
# }
```

### Test Complete Flow (Orchestrator → Agent → Mock)

#### Scenario 1: Complete Transaction in One Message

```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quiero enviar 75000 pesos al número 3009876543",
    "user_id": "test-user-001"
  }' | jq

# Expected: Confirmation request
# {
#   "response": "¿Confirmas el envío de $75,000 COP al número 3009876543?",
#   "conversation_id": "conv-xxxxx",
#   "requires_confirmation": true
# }
```

#### Scenario 2: Multi-Step Conversation

```bash
# Step 1: Greeting
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, quiero enviar dinero",
    "user_id": "test-user-001"
  }' | jq

# Step 2: Provide phone
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Al 3001234567",
    "user_id": "test-user-001",
    "conversation_id": "conv-xxxxx"
  }' | jq

# Step 3: Provide amount
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "50000 pesos",
    "user_id": "test-user-001",
    "conversation_id": "conv-xxxxx"
  }' | jq

# Step 4: Confirm
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Sí, confirmo",
    "user_id": "test-user-001",
    "conversation_id": "conv-xxxxx"
  }' | jq
```

#### Scenario 3: Cancellation

```bash
# Start transaction
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Enviar 30000 al 3001111111",
    "user_id": "test-user-001"
  }' | jq

# Cancel when asked for confirmation
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "No, cancela",
    "user_id": "test-user-001",
    "conversation_id": "conv-xxxxx"
  }' | jq
```

### Test Resilience Patterns

#### Verify Retry Pattern

```bash
# Stop mock API to force retries
docker compose stop mock-api

# Attempt transaction (should retry 3 times and fail)
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Enviar 10000 al 3001234567 y confirmo",
    "user_id": "test-user-001"
  }' | jq

# Restart mock API
docker compose start mock-api

# Check logs for retry attempts
docker compose logs orchestrator | grep -i retry
```

#### Verify Circuit Breaker

```bash
# Stop mock API
docker compose stop mock-api

# Make 6+ requests to trigger circuit breaker
for i in {1..6}; do
  echo "=== Request $i ==="
  curl -X POST http://localhost:8002/api/v1/chat \
    -H "Content-Type: application/json" \
    -d '{
      "message": "Enviar 10000 al 3001234567",
      "user_id": "test-user-001"
    }'
  sleep 1
done

# After 5th failure, circuit breaker should open
# Subsequent requests should fail immediately (without retries)

docker compose start mock-api
```

### Verify Persistence

#### Check LangGraph Checkpoints

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U postgres -d transactional_agent

# View saved checkpoints
SELECT checkpoint_ns, thread_id, COUNT(*)
FROM checkpoints
GROUP BY thread_id, checkpoint_ns;

# Exit
\q
```

#### Check Domain Data

```bash
# View conversations
docker compose exec postgres psql -U postgres -d transactional_agent \
  -c "SELECT id, user_id, status, created_at FROM conversations LIMIT 10;"

# View transactions
docker compose exec postgres psql -U postgres -d transactional_agent \
  -c "SELECT id, conversation_id, recipient_phone, amount, status FROM transactions LIMIT 10;"

# View messages
docker compose exec postgres psql -U postgres -d transactional_agent \
  -c "SELECT conversation_id, role, LEFT(content, 50) as content, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10;"
```

## Monitoring and Logs

### View Real-Time Logs

```bash
# All services
docker compose logs -f

# Only orchestrator
docker compose logs -f orchestrator

# Only mock-api
docker compose logs -f mock-api

# Only postgres
docker compose logs -f postgres
```

### Filter Logs by Events

```bash
# Errors
docker compose logs orchestrator | grep ERROR

# Completed transactions
docker compose logs orchestrator | grep "transaction.*completed"

# Retries
docker compose logs orchestrator | grep -i retry

# Circuit breaker events
docker compose logs orchestrator | grep -i "circuit.*breaker"
```

## Troubleshooting

### Error: "No module named 'apps'"

**Solution**: Ensure you're running from project root
```bash
cd /path/to/ai-transactional-agent-fastapi
make test
```

### Error: "Database connection failed"

**Solution**: Ensure services are running
```bash
make ps  # View service status
make up  # Start services if down
```

### Error: "Coverage not reached"

**Solution**: Project requires 70% coverage
```bash
# See which files have low coverage
make test-cov

# Add tests for files with low coverage
# Or adjust threshold in pyproject.toml temporarily
```

### Slow Tests

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Show 10 slowest tests
pytest --durations=10
```

## Test Metrics

### Current Status

- **Total Tests**: 455
- **Passing Tests**: 455 (100%)
- **Coverage**: 78.19%
- **Execution Time**: ~45 seconds (unit tests)

### Goals

- ✅ Minimum coverage: 70%
- ✅ All tests passing
- ✅ No critical warnings
- ✅ Integration tests for main flows

## CI/CD Integration

Tests run automatically in CI/CD:

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: make test

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Best Practices

1. **Always run tests before commit**
   ```bash
   make test
   ```

2. **Use fixtures for common setup**
   ```python
   @pytest.fixture
   def client():
       return TestClient(app)
   ```

3. **Mock external services**
   ```python
   @pytest.mark.httpx_mock
   def test_external_api(httpx_mock):
       httpx_mock.add_response(json={"status": "ok"})
   ```

4. **Parametrize similar tests**
   ```python
   @pytest.mark.parametrize("input,expected", [
       ("3001234567", True),
       ("invalid", False),
   ])
   def test_phone_validation(input, expected):
       assert validate_phone(input) == expected
   ```

5. **Use async fixtures for async tests**
   ```python
   @pytest.fixture
   async def db_session():
       async with get_session() as session:
           yield session
   ```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing with LangChain](https://python.langchain.com/docs/contributing/testing/)
