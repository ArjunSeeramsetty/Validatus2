# Validatus2 Local Testing Plan - Pergola Case Study

## Overview

This testing plan validates the 5 core tasks of the Validatus2 platform using the Pergola market case study. The platform has been designed with a robust architecture that supports both GCP deployment and local development mode.

## 🏗️ Current Architecture

The Validatus2 platform implements the 5 core tasks through:

### **Task 1: Topic Creation** ✅
- **Service**: `EnhancedAnalysisSessionManager`
- **Endpoint**: `POST /api/v3/sequential-analysis/topics/{topic_id}/analysis/create`
- **Implementation**: Creates analysis sessions with unique topic IDs

### **Task 2: Web Search** ✅
- **Service**: `GCPURLOrchestrator` with `ResearchAgent`
- **Endpoint**: `POST /api/v3/sequential-analysis/analysis/{session_id}/stage1/start`
- **Implementation**: Stage 1 analysis includes web search and URL discovery

### **Task 3: Save URLs** ✅
- **Service**: Integrated within `GCPURLOrchestrator`
- **Implementation**: URLs are automatically saved during Stage 1 analysis
- **Storage**: Local file system in development mode

### **Task 4: Content Scraping** ✅
- **Service**: `ScrapedContentProcessor` within `GCPURLOrchestrator`
- **Implementation**: Content extraction and processing during Stage 1
- **Features**: HTML parsing, content extraction, quality scoring

### **Task 5: Vector DB Creation** ✅
- **Service**: `EnhancedTopicVectorStoreManager` with ChromaDB support
- **Endpoint**: `POST /api/v3/sequential-analysis/analysis/{session_id}/stage2/start`
- **Implementation**: Stage 2 analysis includes vector database creation and search

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
# Option 1: Use the startup script (recommended)
python start_local_backend.py

# Option 2: Manual startup
cd backend
export LOCAL_DEVELOPMENT_MODE=true
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run Complete Workflow Test

```bash
# Test all 5 tasks with Pergola case study
python test_pergola_workflow.py

# Test with custom backend URL
python test_pergola_workflow.py http://localhost:8001
```

### 3. Test Individual Tasks

```bash
# Test specific tasks
python test_individual_tasks.py task1          # Topic Creation only
python test_individual_tasks.py stage1         # Web Search + Content Processing
python test_individual_tasks.py stage2         # Vector DB + Search
python test_individual_tasks.py pergola        # Pergola Intelligence endpoints
python test_individual_tasks.py search         # Semantic Search
python test_individual_tasks.py workflow       # Complete workflow
```

## 📋 Test Scenarios

### **Scenario 1: Complete Workflow Test**

```bash
python test_pergola_workflow.py
```

**Expected Results:**
- ✅ Task 1: Topic created with unique session ID
- ✅ Task 2: Stage 1 analysis completes (web search + content processing)
- ✅ Task 3: URLs automatically saved during Stage 1
- ✅ Task 4: Content scraped and processed during Stage 1
- ✅ Task 5: Stage 2 analysis completes (vector DB + search)

**Success Rate Target:** 80%+ for production readiness

### **Scenario 2: Individual Task Testing**

```bash
# Test topic creation
python test_individual_tasks.py task1

# Test web search and content processing
python test_individual_tasks.py stage1
# Enter the session ID from task1

# Test vector database and search
python test_individual_tasks.py stage2
# Enter the session ID from task1
```

### **Scenario 3: Pergola Intelligence Testing**

```bash
python test_individual_tasks.py pergola
```

**Tests:**
- Market Intelligence endpoint
- Intelligence Dashboard
- Market Insights
- Competitive Landscape

### **Scenario 4: Semantic Search Testing**

```bash
python test_individual_tasks.py search
```

**Test Queries:**
- "What is the global pergola market size?"
- "What are the key trends in outdoor living?"
- "Which pergola materials are most popular?"

## 🔧 Configuration

### **Environment Variables**

The testing scripts automatically configure these settings:

```bash
LOCAL_DEVELOPMENT_MODE=true
ENVIRONMENT=development
GCP_PROJECT_ID=validatus-local
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
LOCAL_DATA_PATH=./local_data
MAX_CONCURRENT_REQUESTS=10
SCRAPING_DELAY=0.2
MIN_CONTENT_QUALITY=0.3
```

### **Local Storage Structure**

```
local_data/
├── vector_stores/          # ChromaDB collections
├── scraped_content/        # Processed web content
├── topics/                 # Topic metadata
└── sessions/              # Analysis sessions
```

## 📊 Expected Performance

### **Response Times**
- **Topic Creation**: < 2 seconds
- **Stage 1 Analysis**: 2-5 minutes (includes web search + content processing)
- **Stage 2 Analysis**: 1-3 minutes (includes vector DB creation)
- **Pergola Intelligence**: < 5 seconds
- **Semantic Search**: < 3 seconds

### **Success Criteria**
- **Task 1**: Topic created with valid session ID
- **Task 2**: Stage 1 completes with content processed
- **Task 3**: URLs saved to local storage
- **Task 4**: Content scraped with quality scores > 0.3
- **Task 5**: Vector DB created with searchable content

## 🐛 Troubleshooting

### **Common Issues**

1. **Backend Server Not Running**
   ```bash
   # Check if server is running
   curl http://localhost:8000/health
   
   # Start server
   python start_local_backend.py
   ```

2. **Import Errors**
   ```bash
   # Install dependencies
   cd backend
   pip install -r requirements.txt
   ```

3. **Stage 1 Timeout**
   - Increase timeout in test scripts
   - Check network connectivity
   - Verify web scraping is working

4. **Stage 2 Vector DB Issues**
   - Check ChromaDB installation
   - Verify local storage permissions
   - Check memory availability

### **Debug Mode**

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python start_local_backend.py
```

### **Health Checks**

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/api/v3/system/status

# Check specific endpoints
curl http://localhost:8000/api/v3/pergola/market-intelligence
```

## 📈 Monitoring and Logs

### **Log Files**
- Backend logs: Console output (configured in startup script)
- Test results: `pergola_workflow_test_results_YYYYMMDD_HHMMSS.json`

### **Key Metrics to Monitor**
- Response times for each task
- Success rates for individual components
- Memory usage during vector DB creation
- Network connectivity for web scraping

## 🎯 Success Criteria

### **Minimum Viable Product (MVP)**
- ✅ All 5 tasks complete successfully
- ✅ 80%+ success rate across all tests
- ✅ Response times within acceptable limits
- ✅ No critical errors or crashes

### **Production Ready**
- ✅ 95%+ success rate
- ✅ Consistent performance across multiple runs
- ✅ Proper error handling and recovery
- ✅ Comprehensive logging and monitoring

## 📚 Additional Resources

### **API Documentation**
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### **Service Architecture**
- `backend/app/services/` - Core business logic
- `backend/app/api/v3/` - API endpoints
- `backend/app/core/` - Configuration and utilities

### **Test Data**
- Pergola case study data available in `backend/migrated_data/`
- Sample URLs and content for testing

## 🚀 Next Steps

1. **Run Initial Tests**: Execute the complete workflow test
2. **Identify Issues**: Review any failed tests
3. **Debug Components**: Use individual task testing
4. **Optimize Performance**: Address any performance issues
5. **Prepare for Deployment**: Ensure all tests pass consistently

---

**Note**: This testing plan is designed for local development and testing. For production deployment to GCP, additional configuration and testing will be required.
