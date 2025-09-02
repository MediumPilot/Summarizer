# FreeSummarizer

A lightweight FastAPI-based text summarization service that uses extractive summarization with LexRank algorithm.

## Features

- **Extractive Summarization**: Uses the LexRank algorithm for high-quality text summarization
- **Configurable Length**: Specify target word count for summaries (30-800 words)
- **Fast API**: RESTful API built with FastAPI
- **Automatic Fallbacks**: Handles edge cases gracefully
- **NLTK Integration**: Uses NLTK for sentence tokenization

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd d:\Summarizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `fastapi` - Web framework
   - `uvicorn` - ASGI server
   - `sumy` - Summarization library
   - `nltk` - Natural language processing toolkit

3. **Download NLTK data** (automatic on first run):
   The application will automatically download the required NLTK punkt tokenizer data on first use.

## Usage

### Starting the Server

Run the FastAPI server using uvicorn:

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### API Endpoints

#### GET `/`
Returns a welcome message and basic usage information.

**Response:**
```json
{
  "message": "FreeSummarizer up. POST /summarize with JSON {text, max_words}."
}
```

#### POST `/summarize`
Summarizes the provided text.

**Request Body:**
```json
{
  "text": "Your long text to summarize goes here...",
  "max_words": 200
}
```

**Parameters:**
- `text` (required): The text to summarize
- `max_words` (optional): Target word count for summary (default: 200, range: 30-800)

**Response:**
```json
{
  "summary": "The summarized text...",
  "word_count": 150,
  "method": "extractive-lexrank"
}
```

## Testing Locally

### Method 1: Using curl

1. **Start the server**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Test the root endpoint**:
   ```bash
   curl http://localhost:8000/
   ```

3. **Test summarization**:
   ```bash
   curl -X POST "http://localhost:8000/summarize" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"This is a long text that needs to be summarized. It contains multiple sentences with various information. The summarizer should extract the most important sentences and create a concise summary. This is useful for processing large documents and getting quick insights.\", \"max_words\": 50}"
   ```

### Method 2: Using Python requests

Create a test script `test_api.py`:

```python
import requests
import json

# Test data
test_text = """
Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often used to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".

The scope of AI is disputed: as machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect. A quip in Tesler's Theorem says "AI is whatever hasn't been done yet." For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.

Modern machine learning techniques are at the core of AI. Problems for AI applications include reasoning, knowledge representation, planning, learning, natural language processing, perception, and the ability to move and manipulate objects. General intelligence is among the field's long-term goals.
"""

# Start server first: uvicorn main:app --reload

# Test the API
url = "http://localhost:8000/summarize"
data = {
    "text": test_text,
    "max_words": 100
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))
```

Run the test:
```bash
python test_api.py
```

### Method 3: Using FastAPI Interactive Docs

1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

2. Open your browser and go to: `http://localhost:8000/docs`

3. Use the interactive Swagger UI to test the API endpoints directly in your browser.

## Troubleshooting

### Import Errors
If you encounter import errors like "Import 'sumy.parsers.plaintext' could not be resolved":

1. **Ensure all dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   pip list | grep sumy
   pip list | grep nltk
   ```

3. **If using a virtual environment**, make sure it's activated:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

### NLTK Data Issues
If you encounter NLTK data errors:

```bash
python -c "import nltk; nltk.download('punkt')"
```

### Port Already in Use
If port 8000 is busy, use a different port:
```bash
uvicorn main:app --reload --port 8001
```

## Project Structure

```
d:\Summarizer\
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server
- **Sumy**: Library for automatic summarization of text documents
- **NLTK**: Natural Language Toolkit for text processing

## Algorithm Details

The summarizer uses the **LexRank algorithm**, which:
1. Creates a graph of sentences based on similarity
2. Applies PageRank-like algorithm to rank sentences
3. Selects top-ranked sentences for the summary
4. Maintains original sentence order in the output

## License

This project is open source and available under the MIT License.