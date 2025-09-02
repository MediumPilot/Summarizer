# FreeSummarizer - Render Deployment Guide

This guide provides step-by-step instructions for deploying the FreeSummarizer API to Render's free tier.

## Prerequisites

- GitHub account
- Render account (free tier available)
- Your code pushed to a GitHub repository

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository contains these files:
- `main.py` - Main FastAPI application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration (optional but recommended)
- `README.md` - Project documentation

### 2. Create Render Service

1. **Login to Render**: Go to [render.com](https://render.com) and sign in
2. **Connect GitHub**: Link your GitHub account if not already connected
3. **Create New Web Service**: Click "New" → "Web Service"
4. **Select Repository**: Choose your FreeSummarizer repository
5. **Configure Service**:
   - **Name**: `freesummarizer-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables (Optional)

Set these environment variables in Render dashboard:
- `MAX_INPUT_CHARS`: `200000` (maximum input size)
- `CHUNK_CHAR_TARGET`: `45000` (chunk size for processing)
- `MAX_SENTENCE_COUNT`: `200` (maximum sentences in summary)

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
   - Provide a public URL

### 5. Verify Deployment

Once deployed, test your API:
- Visit your Render URL (e.g., `https://your-service.onrender.com`)
- Check `/health` endpoint for status
- Test `/docs` for interactive API documentation

## Free Tier Limitations

Render's free tier has these limitations:
- **Sleep after inactivity**: Service sleeps after 15 minutes of inactivity
- **Cold start**: First request after sleep takes 30-60 seconds
- **Monthly hours**: 750 hours per month (sufficient for most use cases)
- **Memory**: 512MB RAM
- **Build time**: 15 minutes maximum

## Optimization for Free Tier

### 1. Keep Service Warm (Optional)
Create a simple monitoring script to ping your service every 10 minutes:

```python
# keep_warm.py
import requests
import time
import schedule

def ping_service():
    try:
        response = requests.get("https://your-service.onrender.com/health", timeout=30)
        print(f"Ping successful: {response.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")

schedule.every(10).minutes.do(ping_service)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### 2. Optimize Dependencies
The current `requirements.txt` is already optimized for fast installation:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sumy==0.11.0
nltk==3.8.1
pydantic==2.5.0
requests==2.31.0
python-multipart==0.0.6
```

### 3. Handle Cold Starts
The API includes proper error handling and logging to manage cold start delays.

## Monitoring and Maintenance

### Health Check
Use the `/health` endpoint to monitor service status:
```bash
curl https://your-service.onrender.com/health
```

### Logs
View logs in Render dashboard:
1. Go to your service dashboard
2. Click "Logs" tab
3. Monitor for errors or performance issues

### Updates
To update your deployment:
1. Push changes to your GitHub repository
2. Render automatically redeploys
3. Monitor logs during deployment

## Troubleshooting

### Common Issues

1. **Build Timeout**
   - Reduce dependencies if possible
   - Use specific versions in requirements.txt

2. **Memory Issues**
   - Reduce `MAX_INPUT_CHARS` if needed
   - Monitor memory usage in logs

3. **Cold Start Delays**
   - Expected behavior on free tier
   - Consider paid tier for production use

4. **NLTK Data Download**
   - First request may be slow due to punkt download
   - Subsequent requests will be faster

### Error Responses

- **503 Service Unavailable**: Service is starting up (cold start)
- **413 Payload Too Large**: Input text exceeds size limits
- **400 Bad Request**: Invalid input format
- **500 Internal Server Error**: Check logs for details

## Production Considerations

For production use, consider upgrading to Render's paid tier:
- **No sleep**: Service stays active
- **Faster cold starts**: Reduced latency
- **More resources**: Higher memory and CPU limits
- **Custom domains**: Use your own domain
- **SSL certificates**: Automatic HTTPS

## API Usage Examples

### Basic Summarization
```bash
curl -X POST "https://your-service.onrender.com/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your long text here...",
       "max_words": 100
     }'
```

### Health Check
```bash
curl "https://your-service.onrender.com/health"
```

### Interactive Documentation
Visit: `https://your-service.onrender.com/docs`

## Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **API Issues**: Check logs and health endpoint

## Security Notes

- API is configured with CORS for web access
- No authentication required (suitable for public APIs)
- Rate limiting not implemented (consider for production)
- Input validation prevents oversized requests

Your FreeSummarizer API is now ready for deployment on Render's free tier!