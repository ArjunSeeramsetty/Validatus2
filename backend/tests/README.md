# Validatus Test Suite

Comprehensive testing framework for the Validatus AI-powered strategic analysis platform.

## 🧪 Test Structure

```
backend/tests/
├── conftest.py                    # Shared fixtures and configuration
├── run_tests.py                   # Test runner script
├── README.md                      # This documentation
├── unit/                          # Unit tests for individual components
│   ├── test_phase_e_orchestrator.py
│   ├── test_multi_level_cache.py
│   ├── test_bayesian_blender.py
│   └── ...
├── integration/                   # Integration tests for workflows
│   ├── test_end_to_end_analysis.py
│   ├── test_phase_integration.py
│   └── test_gcp_services.py
├── performance/                   # Performance and load tests
│   ├── test_phase_e_performance.py
│   ├── test_load_testing.py
│   └── test_cache_performance.py
├── api/                          # API endpoint tests
│   ├── test_phase_e_endpoints.py
│   ├── test_all_endpoints.py
│   └── test_error_handling.py
└── reports/                      # Test reports and coverage
    ├── test_report.html
    ├── test_report.json
    └── coverage/
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
# Install all test dependencies
python backend/tests/run_tests.py --install-deps

# Or install manually
pip install -r backend/requirements.txt
```

### 2. Run All Tests

```bash
# Run all tests
python backend/tests/run_tests.py

# Run with coverage report
python backend/tests/run_tests.py --coverage

# Run with verbose output
python backend/tests/run_tests.py --verbose
```

### 3. Run Specific Test Types

```bash
# Unit tests only
python backend/tests/run_tests.py --type unit

# Integration tests only
python backend/tests/run_tests.py --type integration

# Performance tests only
python backend/tests/run_tests.py --type performance

# API tests only
python backend/tests/run_tests.py --type api
```

### 4. Run Tests by Phase

```bash
# Phase E tests only
python backend/tests/run_tests.py --phase e

# Phase C tests only
python backend/tests/run_tests.py --phase c

# All Phase B tests
python backend/tests/run_tests.py --phase b --type all
```

## 📊 Test Categories

### Unit Tests (`unit/`)
- **Purpose**: Test individual components in isolation
- **Coverage**: Classes, methods, functions
- **Mocking**: Heavy use of mocks for external dependencies
- **Speed**: Fast execution (< 1 second per test)

**Key Test Files:**
- `test_phase_e_orchestrator.py` - Advanced Orchestrator unit tests
- `test_multi_level_cache.py` - Multi-Level Cache Manager tests
- `test_bayesian_blender.py` - Bayesian Data Blender tests

### Integration Tests (`integration/`)
- **Purpose**: Test multi-component workflows
- **Coverage**: End-to-end analysis pipelines
- **Mocking**: Minimal mocking, focus on real interactions
- **Speed**: Moderate execution (1-10 seconds per test)

**Key Test Files:**
- `test_end_to_end_analysis.py` - Complete analysis workflows
- `test_phase_integration.py` - Cross-phase integration
- `test_gcp_services.py` - GCP service integration

### Performance Tests (`performance/`)
- **Purpose**: Test system performance under load
- **Coverage**: Response times, throughput, resource usage
- **Mocking**: Realistic delays and load simulation
- **Speed**: Longer execution (10-60 seconds per test)

**Key Test Files:**
- `test_phase_e_performance.py` - Phase E performance tests
- `test_load_testing.py` - Concurrent request testing
- `test_cache_performance.py` - Cache performance analysis

### API Tests (`api/`)
- **Purpose**: Test API endpoints and responses
- **Coverage**: HTTP endpoints, request/response validation
- **Mocking**: Mock external services, real HTTP handling
- **Speed**: Fast execution (< 5 seconds per test)

**Key Test Files:**
- `test_phase_e_endpoints.py` - Phase E API endpoints
- `test_all_endpoints.py` - Complete API coverage
- `test_error_handling.py` - Error response testing

## 🏷️ Test Markers

Tests are categorized using pytest markers:

### Phase Markers
- `@pytest.mark.phase_a` - Phase A (Stabilization) tests
- `@pytest.mark.phase_b` - Phase B (Enhanced Analytics) tests
- `@pytest.mark.phase_c` - Phase C (Data Pipeline) tests
- `@pytest.mark.phase_d` - Phase D (Frontend Enhancement) tests
- `@pytest.mark.phase_e` - Phase E (Advanced Orchestration) tests

### Category Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.api` - API tests

### Special Markers
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.gcp` - Tests requiring GCP services

## 🔧 Test Configuration

### Fixtures (`conftest.py`)
- `mock_gcp_settings` - Mock GCP configuration
- `mock_feature_flags` - Mock feature flag system
- `mock_gcp_clients` - Mock GCP service clients
- `sample_analysis_config` - Sample analysis configuration
- `performance_test_config` - Performance test configuration

### Test Data
- Sample factor analysis results
- Mock cache data
- Performance test scenarios
- Load test configurations

## 📈 Performance Benchmarks

### Response Time Targets
- **Unit Tests**: < 1 second per test
- **Integration Tests**: < 10 seconds per test
- **Performance Tests**: < 60 seconds per test
- **API Tests**: < 5 seconds per test

### Throughput Targets
- **Cache Operations**: > 1000 ops/sec
- **Analysis Requests**: > 50 requests/sec
- **Concurrent Operations**: > 100 concurrent operations

### Resource Usage Targets
- **Memory Usage**: < 500MB for full test suite
- **CPU Usage**: < 80% during performance tests
- **Cache Hit Rate**: > 80% for optimized scenarios

## 🚨 Error Handling

### Test Failure Scenarios
- **Circuit Breaker Opening**: Tests verify fallback behavior
- **Cache Failures**: Tests ensure graceful degradation
- **Service Unavailability**: Tests validate error handling
- **High Load Conditions**: Tests check resource limits

### Error Recovery Testing
- **Automatic Retry Logic**: Tests verify retry mechanisms
- **Fallback Services**: Tests ensure backup systems work
- **Graceful Degradation**: Tests validate reduced functionality
- **Resource Exhaustion**: Tests check limits and recovery

## 📊 Coverage Requirements

### Minimum Coverage Targets
- **Overall Code Coverage**: > 80%
- **Critical Components**: > 90%
- **Phase E Components**: > 85%
- **API Endpoints**: > 95%

### Coverage Reports
- **HTML Report**: `backend/tests/reports/coverage/index.html`
- **Terminal Report**: Coverage summary in test output
- **JSON Report**: Machine-readable coverage data

## 🔄 Continuous Integration

### Test Pipeline
1. **Install Dependencies**: Install test requirements
2. **Run Unit Tests**: Fast feedback on code changes
3. **Run Integration Tests**: Verify component interactions
4. **Run API Tests**: Validate endpoint functionality
5. **Run Performance Tests**: Check performance regressions
6. **Generate Reports**: Create coverage and performance reports

### Quality Gates
- **All Unit Tests Pass**: Required for all changes
- **Integration Tests Pass**: Required for feature branches
- **Performance Tests Pass**: Required for releases
- **Coverage Threshold Met**: Required for production deployment

## 🛠️ Development Workflow

### Writing New Tests
1. **Choose Test Category**: Unit, Integration, Performance, or API
2. **Add Appropriate Markers**: Phase and category markers
3. **Use Existing Fixtures**: Leverage shared test data
4. **Follow Naming Conventions**: `test_*` for test functions
5. **Add Documentation**: Document test purpose and scenarios

### Test Maintenance
- **Update Fixtures**: Keep test data current
- **Review Performance**: Monitor test execution times
- **Update Coverage**: Ensure new code is tested
- **Clean Up**: Remove obsolete tests and fixtures

## 📋 Test Checklist

### Before Committing
- [ ] All unit tests pass
- [ ] New code has test coverage
- [ ] Performance tests show no regressions
- [ ] API tests validate endpoint changes
- [ ] Integration tests verify workflows

### Before Release
- [ ] Full test suite passes
- [ ] Coverage targets met
- [ ] Performance benchmarks achieved
- [ ] Error handling scenarios tested
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure backend directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

#### Missing Dependencies
```bash
# Install missing test dependencies
pip install pytest pytest-asyncio pytest-cov
```

#### GCP Service Errors
```bash
# Run tests without GCP services
python backend/tests/run_tests.py --type unit
```

#### Performance Test Timeouts
```bash
# Run performance tests individually
python -m pytest backend/tests/performance/test_phase_e_performance.py -v
```

### Getting Help
- Check test output for specific error messages
- Review fixture configuration in `conftest.py`
- Verify test markers and categorization
- Consult component documentation for expected behavior

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Async Testing Best Practices](https://docs.pytest.org/en/stable/how-to/asyncio.html)
- [Performance Testing Guide](https://docs.pytest.org/en/stable/example/markers.html#custom-marker-and-command-line-option-to-control-test-runs)

---

**Validatus Test Suite** - Ensuring quality and reliability across all phases of the AI-powered strategic analysis platform.
