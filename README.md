# FreeSummarizer API

A professional-grade FastAPI-based text summarization service that uses advanced extractive summarization algorithms including LexRank and LSA. Optimized for production deployment on platforms like Render.

## 🚀 Features

- **Advanced Summarization**: Uses LexRank algorithm with LSA fallback for high-quality text summarization
- **Intelligent Chunking**: Handles large documents by splitting into manageable chunks
- **Configurable Length**: Specify target word count for summaries (30-800 words)
- **Production Ready**: Built with FastAPI, includes health checks, CORS support, and comprehensive error handling
- **Comprehensive Testing**: 15+ test cases covering all functionality
- **Cloud Deployment**: Optimized for Render free tier deployment
- **Interactive Documentation**: Automatic OpenAPI/Swagger documentation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🛠 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Summarizer
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (automatic on first run):
   The application will automatically download the required NLTK punkt tokenizer data on first use.

## 🚀 Quick Start

### Start the Server

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Basic summarization
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your long text to summarize goes here. This should be a substantial piece of text with multiple sentences to see the summarization in action.",
       "max_words": 50
     }'
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for the interactive Swagger UI documentation.

## 📡 API Endpoints

### GET `/`
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "FreeSummarizer API is running",
  "version": "1.0.0",
  "endpoints": {
    "summarize": "POST /summarize - Summarize text",
    "health": "GET /health - Health check",
    "docs": "GET /docs - API documentation"
  }
}
```

### GET `/health`
Health check endpoint for monitoring and deployment.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "nltk_status": "available",
  "limits": {
    "max_input_chars": 200000,
    "chunk_target_chars": 45000,
    "max_sentence_count": 200
  }
}
```

### POST `/summarize`
Main summarization endpoint.

**Request Body:**
```json
{
  "text": "Your text to summarize...",
  "max_words": 100
}
```

**Parameters:**
- `text` (required): The text to summarize
- `max_words` (optional): Target word count (default: 200, range: 30-800)

**Response:**
```json
{
  "summary": "The summarized text containing the most important information...",
  "word_count": 95,
  "method": "chunked-lexrank"
}
```

**Methods:**
- `original`: Text was short enough to return as-is
- `chunked-lexrank`: Used LexRank algorithm with chunking
- `fallback-first-sents`: Fallback method using first sentences

## 🧪 Testing

### Quick Test

Run the basic test script:
```bash
python test_api.py
```

### Comprehensive Test Suite

Run the full test suite with 15+ test cases:
```bash
python comprehensive_tests.py
```

**Test Coverage:**
1. Server Connectivity
2. Root Endpoint
3. Basic Summarization
4. Short Text Handling
5. Empty Text Validation
6. Whitespace-Only Text
7. Word Count Limits
8. Large Text Processing
9. Extremely Large Text Rejection
10. Special Characters Handling
11. Multilingual Text
12. Technical Document Summarization
13. Response Time Performance
14. Concurrent Requests
15. API Documentation Endpoints

### Test with Custom URL

```bash
python comprehensive_tests.py --url https://your-deployed-api.onrender.com
```

## 🌐 Deployment

### Render Deployment (Free Tier)

1. **Push to GitHub**: Ensure your code is in a GitHub repository

2. **Create Render Service**:
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Deploy**: Render will automatically build and deploy your service

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Other Platforms

The API is compatible with:
- **Heroku**: Use `Procfile` with `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Direct deployment from GitHub
- **DigitalOcean App Platform**: Use the same build/start commands
- **AWS/GCP/Azure**: Deploy as containerized application

## ⚙️ Configuration

### Environment Variables

Configure the API using environment variables:

```bash
# Maximum input size (characters)
MAX_INPUT_CHARS=200000

# Target characters per chunk for large texts
CHUNK_CHAR_TARGET=45000

# Maximum sentences in any summary
MAX_SENTENCE_COUNT=200
```

### Production Settings

For production deployment:
- Set specific CORS origins instead of `["*"]`
- Add rate limiting middleware
- Implement authentication if needed
- Configure logging levels
- Set up monitoring and alerting

## 💡 Examples

### Python Client

```python
import requests

def summarize_text(text, max_words=100, api_url="http://localhost:8000"):
    response = requests.post(
        f"{api_url}/summarize",
        json={"text": text, "max_words": max_words}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["summary"]
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

# Example usage
long_text = """
Artificial intelligence (AI) is intelligence demonstrated by machines, 
in contrast to the natural intelligence displayed by humans and animals...
"""

summary = summarize_text(long_text, max_words=50)
print(summary)
```

### JavaScript/Node.js Client

```javascript
async function summarizeText(text, maxWords = 100) {
    const response = await fetch('http://localhost:8000/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            max_words: maxWords
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        return result.summary;
    } else {
        throw new Error(`API Error: ${response.status} - ${await response.text()}`);
    }
}

// Example usage
const longText = "Your long text here...";
summarizeText(longText, 50)
    .then(summary => console.log(summary))
    .catch(error => console.error(error));
```

### cURL Examples

```bash
# Basic summarization
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Climate change refers to long-term shifts in global climate patterns...",
       "max_words": 75
     }'

# Large document summarization
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Very long document content here...",
       "max_words": 200
     }'
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|sumy|nltk)"
```

**2. NLTK Data Issues**
```bash
# Manually download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

**3. Port Already in Use**
```bash
# Use different port
uvicorn main:app --reload --port 8001
```

**4. Memory Issues with Large Texts**
- Reduce `MAX_INPUT_CHARS` environment variable
- Use smaller `max_words` values
- Consider upgrading server resources

### Error Codes

- **400 Bad Request**: Invalid input (empty text, malformed JSON)
- **413 Payload Too Large**: Input text exceeds size limits
- **422 Unprocessable Entity**: Invalid request format
- **500 Internal Server Error**: Server-side processing error

### Performance Tips

- **Cold Starts**: First request may be slow due to model loading
- **Large Texts**: Processing time increases with text size
- **Concurrent Requests**: API handles multiple requests efficiently
- **Caching**: Consider implementing client-side caching for repeated requests

## 📊 Algorithm Details

### LexRank Algorithm
1. **Sentence Similarity**: Computes similarity between all sentence pairs
2. **Graph Construction**: Creates a graph where sentences are nodes
3. **PageRank**: Applies PageRank algorithm to rank sentences
4. **Selection**: Selects top-ranked sentences for summary
5. **Ordering**: Maintains original sentence order in output

### Chunking Strategy
For large documents:
1. **Sentence Tokenization**: Splits text into sentences
2. **Chunk Formation**: Groups sentences up to target character limit
3. **Parallel Processing**: Summarizes each chunk independently
4. **Combination**: Merges chunk summaries
5. **Final Pass**: Applies final summarization to combined result

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check `/docs` endpoint when running
- **Health Check**: Use `/health` endpoint for status monitoring

---

**Ready to deploy?** Check out [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions!