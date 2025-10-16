# Validatus2 Test Suite

Comprehensive test suite for the Validatus2 platform.

## Test Structure

```
tests/
├── api/                    # API endpoint tests
│   ├── test_api_endpoints.py     # Comprehensive API endpoint tests
│   └── test_topic_crud.py        # Topic CRUD operations
├── integration/            # Integration tests
│   ├── test_complete_topic_workflow.py      # Complete topic lifecycle
│   ├── test_cross_tab_functionality.py      # Cross-tab functionality
│   ├── test_strategic_analysis_workflow.py  # Strategic analysis workflow
│   └── test_websearch_functionality.py      # Web search and URL collection
├── e2e/                    # End-to-end tests
│   ├── test_persistence.py         # Data persistence tests
│   └── test_topic_integration.py   # Complete topic integration
├── unit/                   # Unit tests
│   ├── test_content_quality_analyzer.py  # Content quality analysis
│   └── test_database_connection.py       # Database connectivity
├── performance/            # Performance tests
│   └── test_load_testing.py        # Load testing
└── utils/                  # Test utilities
    ├── __init__.py
    └── cleanup_test_data.py        # Test data cleanup utility
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test category
```bash
# API tests
pytest tests/api/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/

# Unit tests
pytest tests/unit/
```

### Run specific test file
```bash
pytest tests/api/test_topic_crud.py
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=backend/app --cov-report=html
```

## Test Categories

### API Tests (`tests/api/`)
Tests individual API endpoints in isolation.

- **test_api_endpoints.py**: Comprehensive API endpoint testing
- **test_topic_crud.py**: Topic creation, retrieval, update, deletion

### Integration Tests (`tests/integration/`)
Tests multiple components working together.

- **test_complete_topic_workflow.py**: Full topic lifecycle from creation to completion
- **test_cross_tab_functionality.py**: Cross-tab data persistence and consistency
- **test_strategic_analysis_workflow.py**: Strategic analysis components integration
- **test_websearch_functionality.py**: Web search and URL collection workflow

### E2E Tests (`tests/e2e/`)
Tests complete user workflows from frontend to backend.

- **test_persistence.py**: Data persistence across sessions and restarts
- **test_topic_integration.py**: Complete topic integration workflow

### Unit Tests (`tests/unit/`)
Tests individual components in isolation.

- **test_content_quality_analyzer.py**: Content quality analysis algorithms
- **test_database_connection.py**: Database connectivity and configuration

### Performance Tests (`tests/performance/`)
Tests system performance and scalability.

- **test_load_testing.py**: Load testing and performance benchmarks

## Test Utilities

### Cleanup Test Data
```bash
# Dry run (shows what would be deleted)
python tests/utils/cleanup_test_data.py --dry-run

# Cleanup local test data
python tests/utils/cleanup_test_data.py

# Cleanup production (use with caution!)
python tests/utils/cleanup_test_data.py --prod
```

## Test Configuration

### Environment Variables
```bash
# Local testing
export BASE_URL="http://localhost:8000"
export FRONTEND_URL="http://localhost:3000"

# Production testing
export BASE_URL="https://validatus-backend-ssivkqhvhq-uc.a.run.app"
export FRONTEND_URL="https://validatus2-frontend-ssivkqhvhq-uc.a.run.app"
```

### pytest.ini Configuration
See `backend/pytest.ini` for test configuration.

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestFeature:
    """Test feature description"""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        # Setup code
        yield data
        # Cleanup code
    
    def test_something(self, setup_data):
        """Test description"""
        # Test code
        assert result == expected
```

### Best Practices
1. **Isolation**: Each test should be independent
2. **Cleanup**: Always cleanup test data in fixtures or try/finally blocks
3. **Descriptive**: Use descriptive test names and docstrings
4. **Fast**: Keep unit tests fast (<1s per test)
5. **Fixtures**: Use fixtures for common setup code
6. **Mocking**: Mock external dependencies where appropriate

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to master
- Scheduled daily runs

See `.github/workflows/` for CI configuration.

## Troubleshooting

### Tests Failing Locally
1. Ensure backend is running: `python backend/start_local_backend.py`
2. Check database connection
3. Verify environment variables
4. Clean up old test data: `python tests/utils/cleanup_test_data.py`

### Tests Timing Out
- Increase timeout values in test requests
- Check network connectivity
- Verify backend is responding

### Import Errors
- Ensure virtual environment is activated
- Install test dependencies: `pip install -r backend/requirements-dev.txt`
- Check Python path configuration

## Test Coverage

Current coverage targets:
- **API endpoints**: 95%+
- **Core services**: 90%+
- **Business logic**: 85%+
- **Overall**: 80%+

View coverage report:
```bash
pytest tests/ --cov=backend/app --cov-report=html
open htmlcov/index.html
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass locally
3. Maintain or improve coverage
4. Update this README if adding new test categories

## Support

For test-related issues:
- Check existing test examples
- Review pytest documentation
- Consult the team documentation

