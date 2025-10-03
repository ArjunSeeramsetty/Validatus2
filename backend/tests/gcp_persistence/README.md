# GCP Persistence Test Suite

This directory contains comprehensive tests for the GCP Persistence integration in the Validatus platform.

## Test Structure

### Core Tests
- `test_gcp_persistence.py` - Main integration tests for the unified GCP persistence manager
- `test_individual_managers.py` - Individual tests for each GCP service manager
- `test_topic_service_integration.py` - Tests for the updated TopicService with GCP persistence
- `conftest.py` - Test configuration and fixtures

### Test Categories

#### 1. GCP Persistence Manager Tests
- Complete topic creation workflow with all GCP services
- Topic listing with Redis caching optimization
- Complete 5-task workflow execution
- Storage operations (Cloud Storage)
- Redis operations (caching, queues, activity tracking)
- Health checks for all services

#### 2. Individual Manager Tests

**GCP Storage Manager:**
- Store and retrieve scraped content
- Store embeddings data
- Store analysis reports
- Batch delete operations

**GCP SQL Manager:**
- Create and retrieve topics
- List topics with pagination
- Store and update URLs
- Workflow status tracking

**GCP Redis Manager:**
- Session data caching
- Workflow progress tracking
- URL queue operations
- User activity tracking
- Rate limiting
- Health checks

**GCP Vector Manager:**
- Create vector indexes
- Similarity search
- Health checks

**GCP Spanner Manager:**
- Store analysis results
- Get user analytics
- Get market intelligence
- Get cross-topic insights
- Health checks

#### 3. Topic Service Integration Tests
- Topic creation with GCP persistence
- Topic listing with caching
- Status updates with workflow tracking
- Topic search functionality
- Topic statistics
- Workflow progress tracking
- Topic deletion with cleanup

## Running Tests

### Prerequisites
1. Set up test environment variables in `conftest.py`
2. Ensure local development mode is enabled
3. Have test databases and services available (or mocked)

### Running Individual Test Files
```bash
# Run main integration tests
pytest tests/gcp_persistence/test_gcp_persistence.py -v

# Run individual manager tests
pytest tests/gcp_persistence/test_individual_managers.py -v

# Run TopicService integration tests
pytest tests/gcp_persistence/test_topic_service_integration.py -v

# Run all GCP persistence tests
pytest tests/gcp_persistence/ -v
```

### Running Specific Test Classes
```bash
# Test only storage operations
pytest tests/gcp_persistence/test_individual_managers.py::TestGCPStorageManager -v

# Test only Redis operations
pytest tests/gcp_persistence/test_individual_managers.py::TestGCPRedisManager -v

# Test only TopicService integration
pytest tests/gcp_persistence/test_topic_service_integration.py::TestTopicServiceGCPIntegration -v
```

### Running with Markers
```bash
# Run only integration tests
pytest -m integration -v

# Run only storage tests
pytest -m storage -v

# Run only SQL tests
pytest -m sql -v
```

## Test Configuration

### Environment Variables
Tests use the following environment variables (set in `conftest.py`):
- `LOCAL_DEVELOPMENT_MODE=true`
- `GCP_PROJECT_ID=test-project`
- `CONTENT_STORAGE_BUCKET=test-content-bucket`
- `EMBEDDINGS_STORAGE_BUCKET=test-embeddings-bucket`
- `REPORTS_STORAGE_BUCKET=test-reports-bucket`
- `REDIS_HOST=localhost`
- `REDIS_PORT=6379`
- `LOCAL_POSTGRES_URL=postgresql://postgres:password@localhost:5432/validatus_test`
- `LOCAL_REDIS_URL=redis://localhost:6379/1`

### Test Fixtures
- `persistence_manager` - Initialized GCP persistence manager
- `sample_topic_request` - Sample topic creation request
- `topic_service` - TopicService instance
- `test_settings` - Test configuration settings
- `sample_topic_data` - Sample topic data
- `sample_workflow_data` - Sample workflow data
- `sample_analysis_results` - Sample analysis results

## Expected Test Results

### Successful Test Run
- All GCP services initialize successfully
- Topics are created, retrieved, and deleted correctly
- Caching works properly
- Workflow progress is tracked
- Health checks pass
- Cleanup operations work correctly

### Test Environment Limitations
Some tests may be skipped in test environments due to:
- External GCP service dependencies
- Missing authentication credentials
- Network connectivity issues
- Resource limitations

These limitations are handled gracefully with appropriate skip messages.

## Debugging Tests

### Common Issues
1. **Service Initialization Failures**: Check environment variables and service availability
2. **Database Connection Issues**: Verify database configuration and connectivity
3. **Redis Connection Issues**: Ensure Redis is running and accessible
4. **Storage Access Issues**: Check GCS bucket permissions and configuration

### Debug Mode
Run tests with debug output:
```bash
pytest tests/gcp_persistence/ -v -s --log-cli-level=DEBUG
```

### Test Isolation
Each test is designed to be isolated and includes cleanup operations to prevent interference between tests.

## Coverage

The test suite covers:
- ✅ All GCP service managers
- ✅ Complete persistence workflows
- ✅ Error handling and edge cases
- ✅ Health checks and monitoring
- ✅ Performance optimizations (caching)
- ✅ Data consistency and integrity
- ✅ Cleanup and resource management

## Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Include appropriate fixtures and setup/teardown
3. Add proper error handling and cleanup
4. Update this README with new test descriptions
5. Ensure tests are isolated and don't interfere with each other
