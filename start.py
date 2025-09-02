#!/usr/bin/env python3
"""
FreeSummarizer Startup Script
Handles NLTK data download and starts the FastAPI server
"""

import os
import sys
import subprocess
import nltk
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("FreeSummarizerStartup")

def ensure_nltk_data():
    """Ensure required NLTK data is downloaded"""
    try:
        nltk.data.find("tokenizers/punkt")
        logger.info("NLTK punkt tokenizer already available")
    except LookupError:
        logger.info("Downloading NLTK punkt tokenizer...")
        try:
            nltk.download("punkt", quiet=True)
            logger.info("NLTK punkt tokenizer downloaded successfully")
        except Exception as e:
            logger.error(f"Failed to download NLTK data: {e}")
            return False
    return True

def start_server():
    """Start the FastAPI server"""
    # Get port from environment or use default
    port = os.getenv("PORT", "8000")
    host = os.getenv("HOST", "0.0.0.0")
    
    # Build uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app",
        "--host", host,
        "--port", port
    ]
    
    # Add reload flag if in development
    if os.getenv("ENVIRONMENT", "development") == "development":
        cmd.append("--reload")
    
    logger.info(f"Starting FreeSummarizer API on {host}:{port}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Server failed to start: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    logger.info("=" * 50)
    logger.info("FreeSummarizer API - Starting Up")
    logger.info("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    logger.info(f"Python version: {sys.version}")
    
    # Ensure NLTK data is available
    if not ensure_nltk_data():
        logger.error("Failed to setup NLTK data")
        sys.exit(1)
    
    # Start the server
    logger.info("Starting FastAPI server...")
    if not start_server():
        logger.error("Failed to start server")
        sys.exit(1)

if __name__ == "__main__":
    main()