# 📚 Validatus API Documentation

## Overview

The Validatus API provides comprehensive endpoints for AI-powered strategic analysis, content processing, and knowledge management. This documentation covers all Phase 1 and Phase 2 endpoints with detailed examples and usage guidelines.

## Base URL

```
Production: https://validatus-api.run.app
Development: http://localhost:8000
```

## Authentication

Currently, the API operates without authentication for development purposes. Future versions will implement OAuth 2.0 with Google Cloud Identity.

## API Versioning

All endpoints use version 3 (`/api/v3/`) and follow semantic versioning principles.

## Rate Limits

- **Standard endpoints**: 100 requests/minute
- **Analysis endpoints**: 10 requests/minute
- **Bulk operations**: 5 requests/minute

## Error Handling

The API uses standard HTTP status codes and returns detailed error information:

```json
{
  "error": "ValidationError",
  "message": "Invalid request data",
  "details": {
    "field": "topic",
    "issue": "Topic name cannot be empty"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## 🏥 Health & Monitoring

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "validatus-backend",
  "version": "3.0.0",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 📊 Phase 1 - Basic Topic Management

### List All Topics

```http
GET /api/v3/topics
```

**Response:**
```json
{
  "success": true,
  "topics": ["artificial-intelligence", "machine-learning", "data-science"],
  "total_count": 3,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Create Topic Store

```http
POST /api/v3/topics/create
```

**Request Body:**
```json
{
  "topic": "artificial intelligence",
  "urls": [
    "https://example.com/ai-article1",
    "https://example.com/ai-article2"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "topic_id": "topic_ai_123456",
  "topic": "artificial intelligence",
  "url_count": 2,
  "message": "Topic store created successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Collect URLs for Topic

```http
POST /api/v3/topics/{topic}/collect-urls
```

**Request Body:**
```json
{
  "search_query": "artificial intelligence trends 2024",
  "max_urls": 50,
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "urls": [
    "https://example.com/ai-trends-2024",
    "https://example.com/ai-market-analysis"
  ],
  "total_collected": 2,
  "collection_metadata": {
    "search_engine": "google",
    "collection_time": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Get Evidence by Layer

```http
GET /api/v3/topics/{topic}/evidence/{layer}
```

**Parameters:**
- `topic` - Topic identifier
- `layer` - Strategic layer (consumer, market, product, etc.)

**Response:**
```json
{
  "success": true,
  "evidence": [
    {
      "content": "Consumer adoption of AI tools increased by 40%",
      "url": "https://example.com/consumer-study",
      "relevance_score": 0.92,
      "quality_score": 0.88
    }
  ],
  "layer": "consumer",
  "total_count": 1,
  "retrieval_metadata": {
    "search_time": 0.15,
    "vector_similarity_threshold": 0.8
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 🚀 Phase 2 - Enhanced Features

### Enhanced Topic Management

#### Create Enhanced Topic Store

```http
POST /api/v3/enhanced/topics/create
```

**Request Body:**
```json
{
  "topic": "artificial intelligence",
  "urls": [
    "https://example.com/ai-article1",
    "https://example.com/ai-article2"
  ],
  "quality_threshold": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "topic_id": "enhanced_topic_ai_123456",
  "topic": "artificial intelligence",
  "quality_threshold": 0.7,
  "url_count": 2,
  "processing_metadata": {
    "quality_filtered_documents": 15,
    "classification_accuracy": 0.92,
    "processing_time": 45.2
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Get Enhanced Topic Knowledge

```http
GET /api/v3/enhanced/topics/{topic}/knowledge
```

**Response:**
```json
{
  "success": true,
  "topic": "artificial intelligence",
  "knowledge": {
    "topic_overview": "Comprehensive analysis of AI technologies",
    "key_concepts": ["machine learning", "deep learning", "neural networks"],
    "quality_distribution": {
      "high_quality": 85,
      "medium_quality": 12,
      "low_quality": 3
    },
    "semantic_clusters": [
      {
        "cluster_name": "AI Applications",
        "concepts": ["automation", "robotics", "computer vision"],
        "document_count": 45
      }
    ]
  },
  "knowledge_metadata": {
    "total_documents": 100,
    "average_quality": 0.87,
    "last_updated": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Update Enhanced Topic

```http
PUT /api/v3/enhanced/topics/{topic}/update
```

**Request Body:**
```json
{
  "new_urls": [
    "https://example.com/new-ai-article"
  ],
  "quality_threshold": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "topic": "artificial intelligence",
  "update_result": {
    "new_documents_added": 1,
    "quality_improvement": 0.05,
    "total_documents": 101,
    "updated_quality_distribution": {
      "high_quality": 86,
      "medium_quality": 12,
      "low_quality": 3
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Analyze Topic Performance

```http
GET /api/v3/enhanced/topics/{topic}/performance
```

**Response:**
```json
{
  "success": true,
  "topic": "artificial intelligence",
  "performance_analysis": {
    "performance_metrics": {
      "query_response_time": 0.25,
      "accuracy_score": 0.94,
      "throughput": 150,
      "cache_hit_rate": 0.78
    },
    "quality_metrics": {
      "average_content_quality": 0.87,
      "topic_relevance": 0.92,
      "content_freshness": 0.85
    },
    "recommendations": [
      "Increase cache size for better performance",
      "Update low-quality documents",
      "Consider adding more recent content"
    ]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Strategic Analysis

#### Create Analysis Session

```http
POST /api/v3/analysis/sessions/create
```

**Request Body:**
```json
{
  "topic": "artificial intelligence",
  "user_id": "user_12345",
  "analysis_parameters": {
    "quality_threshold": 0.7,
    "include_competitive_analysis": true,
    "analysis_depth": "comprehensive"
  }
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_ai_analysis_123456",
  "topic": "artificial intelligence",
  "user_id": "user_12345",
  "message": "Analysis session created successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Execute Strategic Analysis

```http
POST /api/v3/analysis/sessions/{session_id}/execute
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_ai_analysis_123456",
  "message": "Strategic analysis started in background",
  "status": "processing",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Get Analysis Status

```http
GET /api/v3/analysis/sessions/{session_id}/status
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_ai_analysis_123456",
  "status": {
    "current_status": "analyzing",
    "progress_percentage": 65.0,
    "current_stage": "layer_scoring",
    "completed_layers": ["consumer", "market", "product"],
    "remaining_layers": ["brand", "experience", "technology", "operations", "financial", "competitive", "regulatory"],
    "estimated_completion": "2024-01-01T12:05:00Z",
    "error_messages": []
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Get Analysis Results

```http
GET /api/v3/analysis/sessions/{session_id}/results
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_ai_analysis_123456",
  "results": {
    "analysis_summary": {
      "overall_score": 0.82,
      "confidence_level": 0.89,
      "analysis_completion_time": "2024-01-01T12:05:30Z",
      "total_evidence_sources": 150
    },
    "layer_scores": [
      {
        "layer_name": "consumer",
        "score": 0.85,
        "confidence": 0.92,
        "key_insights": ["High consumer adoption", "Growing trust in AI"],
        "evidence_count": 25
      }
    ],
    "factor_calculations": [
      {
        "factor_name": "market_attractiveness",
        "calculated_value": 0.78,
        "calculation_method": "weighted_average",
        "confidence_score": 0.88
      }
    ],
    "segment_scores": [
      {
        "segment_name": "growth_potential",
        "score": 0.84,
        "supporting_evidence": 45
      }
    ],
    "strategic_recommendations": [
      "Focus on consumer education and trust building",
      "Invest in product differentiation",
      "Monitor competitive landscape closely"
    ]
  },
  "timestamp": "2024-01-01T12:05:30Z"
}
```

### Content Processing

#### Analyze Content Quality

```http
POST /api/v3/content/analyze-quality
```

**Request Body:**
```json
{
  "content": "This article discusses the latest trends in artificial intelligence and machine learning...",
  "url": "https://example.com/ai-article",
  "topic": "artificial intelligence"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/ai-article",
  "topic": "artificial intelligence",
  "quality_scores": {
    "overall_score": 0.87,
    "topic_relevance": 0.92,
    "readability": 0.84,
    "domain_authority": 0.89,
    "content_freshness": 0.78,
    "factual_accuracy": 0.85,
    "completeness": 0.91,
    "uniqueness": 0.82,
    "engagement_potential": 0.79
  },
  "quality_metadata": {
    "content_length": 2500,
    "word_count": 420,
    "sentence_count": 28,
    "paragraph_count": 8,
    "analysis_timestamp": "2024-01-01T12:00:00Z",
    "url_domain": "example.com",
    "topic_analyzed": "artificial intelligence"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Deduplicate Content

```http
POST /api/v3/content/deduplicate
```

**Request Body:**
```json
{
  "documents": [
    {
      "content": "AI is transforming healthcare...",
      "url": "https://example.com/doc1",
      "title": "AI in Healthcare"
    },
    {
      "content": "Artificial intelligence is revolutionizing medical care...",
      "url": "https://example.com/doc2",
      "title": "AI Medical Revolution"
    }
  ],
  "similarity_threshold": 0.85
}
```

**Response:**
```json
{
  "success": true,
  "original_count": 2,
  "deduplicated_count": 1,
  "duplicates_removed": 1,
  "deduplication_stats": {
    "exact_duplicates": 0,
    "near_exact_duplicates": 0,
    "semantic_duplicates": 1,
    "partial_duplicates": 0,
    "processing_time": 2.3
  },
  "documents": [
    {
      "content": "AI is transforming healthcare...",
      "url": "https://example.com/doc1",
      "title": "AI in Healthcare",
      "deduplication_info": {
        "is_duplicate": false,
        "duplicate_type": null,
        "similarity_score": 1.0
      }
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Optimization

#### Optimize Parallel Processing

```http
POST /api/v3/optimization/parallel-processing
```

**Request Body:**
```json
{
  "analysis_tasks": [
    {
      "id": "task_1",
      "type": "layer_scoring",
      "complexity": "medium",
      "layer": "consumer"
    },
    {
      "id": "task_2",
      "type": "factor_calculation",
      "complexity": "light",
      "factor": "market_attractiveness"
    }
  ],
  "max_concurrent": 10
}
```

**Response:**
```json
{
  "success": true,
  "original_task_count": 2,
  "processed_task_count": 2,
  "optimization_results": [
    {
      "task_id": "task_1",
      "result": {
        "layer_score": 0.85,
        "confidence": 0.92,
        "processing_time": 1.2
      },
      "status": "success",
      "optimization_applied": true
    },
    {
      "task_id": "task_2",
      "result": {
        "factor_value": 0.78,
        "calculation_time": 0.8
      },
      "status": "success",
      "optimization_applied": true
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 📋 Request/Response Examples

### Python Examples

#### Basic Topic Creation

```python
import requests

# Create a topic
response = requests.post(
    "https://validatus-api.run.app/api/v3/topics/create",
    json={
        "topic": "machine learning",
        "urls": [
            "https://example.com/ml-article1",
            "https://example.com/ml-article2"
        ]
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Topic created: {result['topic_id']}")
else:
    print(f"Error: {response.json()}")
```

#### Enhanced Analysis

```python
import requests
import time

# Create analysis session
session_response = requests.post(
    "https://validatus-api.run.app/api/v3/analysis/sessions/create",
    json={
        "topic": "artificial intelligence",
        "user_id": "user_123",
        "analysis_parameters": {"quality_threshold": 0.7}
    }
)

session_id = session_response.json()["session_id"]

# Execute analysis
requests.post(
    f"https://validatus-api.run.app/api/v3/analysis/sessions/{session_id}/execute"
)

# Poll for completion
while True:
    status_response = requests.get(
        f"https://validatus-api.run.app/api/v3/analysis/sessions/{session_id}/status"
    )
    status = status_response.json()["status"]
    
    if status["current_status"] == "completed":
        break
    
    time.sleep(10)  # Wait 10 seconds

# Get results
results_response = requests.get(
    f"https://validatus-api.run.app/api/v3/analysis/sessions/{session_id}/results"
)

results = results_response.json()["results"]
print(f"Analysis completed with score: {results['analysis_summary']['overall_score']}")
```

### JavaScript Examples

#### Content Quality Analysis

```javascript
async function analyzeContentQuality(content, url, topic) {
    const response = await fetch('/api/v3/content/analyze-quality', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content,
            url: url,
            topic: topic
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        return result.quality_scores;
    } else {
        throw new Error('Quality analysis failed');
    }
}

// Usage
const qualityScores = await analyzeContentQuality(
    "This is an article about AI...",
    "https://example.com/article",
    "artificial intelligence"
);

console.log(`Overall quality: ${qualityScores.overall_score}`);
```

#### Content Deduplication

```javascript
async function deduplicateContent(documents) {
    const response = await fetch('/api/v3/content/deduplicate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            documents: documents,
            similarity_threshold: 0.85
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        return {
            documents: result.documents,
            duplicatesRemoved: result.duplicates_removed
        };
    } else {
        throw new Error('Deduplication failed');
    }
}

// Usage
const documents = [
    { content: "AI article content...", url: "https://example.com/1" },
    { content: "Similar AI content...", url: "https://example.com/2" }
];

const { documents: deduplicatedDocs, duplicatesRemoved } = 
    await deduplicateContent(documents);

console.log(`Removed ${duplicatesRemoved} duplicates`);
```

---

## 🔧 Development & Testing

### Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your GCP credentials
   ```

3. **Run the development server:**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Testing

Run the comprehensive test suite:

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v

# Performance tests
pytest tests/performance/ -v

# All tests
pytest tests/ -v --cov=backend
```

### API Testing with curl

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# List topics
curl -X GET "http://localhost:8000/api/v3/topics"

# Create topic
curl -X POST "http://localhost:8000/api/v3/topics/create" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "test topic",
    "urls": ["https://example.com"]
  }'

# Analyze content quality
curl -X POST "http://localhost:8000/api/v3/content/analyze-quality" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test content",
    "url": "https://example.com",
    "topic": "test"
  }'
```

---

## 📈 Performance Considerations

### Response Times

- **Health check**: < 100ms
- **Topic listing**: < 200ms
- **Content analysis**: 1-5 seconds
- **Strategic analysis**: 2-10 minutes (background processing)

### Rate Limits

- **Standard endpoints**: 100 requests/minute per IP
- **Analysis endpoints**: 10 requests/minute per user
- **Bulk operations**: 5 requests/minute per user

### Best Practices

1. **Use pagination** for large result sets
2. **Implement caching** for frequently accessed data
3. **Use background processing** for long-running operations
4. **Monitor rate limits** and implement exponential backoff
5. **Handle errors gracefully** with retry logic

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service Not Initialized Error

**Error:** `Service not initialized`

**Solution:** Ensure all required environment variables are set and services are properly configured.

#### 2. Validation Errors

**Error:** `422 Unprocessable Entity`

**Solution:** Check request body format and required fields.

#### 3. Timeout Errors

**Error:** `Request timeout`

**Solution:** Increase timeout values or use background processing for long operations.

#### 4. Rate Limit Exceeded

**Error:** `429 Too Many Requests`

**Solution:** Implement exponential backoff and respect rate limits.

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

### Support

For technical support and bug reports:

- **GitHub Issues**: [https://github.com/ArjunSeeramsetty/Validatus2/issues](https://github.com/ArjunSeeramsetty/Validatus2/issues)
- **Documentation**: [https://github.com/ArjunSeeramsetty/Validatus2/blob/main/docs/](https://github.com/ArjunSeeramsetty/Validatus2/blob/main/docs/)

---

## 🔄 Changelog

### Version 3.0.0 (Current)
- ✅ Complete Phase 2 implementation
- ✅ Enhanced topic management
- ✅ Strategic analysis engine
- ✅ Advanced content processing
- ✅ Performance optimization
- ✅ Comprehensive API documentation

### Version 2.0.0
- ✅ Phase 1 implementation
- ✅ Basic topic management
- ✅ URL orchestration
- ✅ Vector store management

### Version 1.0.0
- ✅ Initial architecture
- ✅ Basic API structure
