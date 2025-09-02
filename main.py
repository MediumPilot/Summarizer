# main.py
import os
import math
import logging
import traceback
import time
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import nltk
from nltk import sent_tokenize

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("FreeSummarizer")

app = FastAPI(
    title="FreeSummarizer API",
    description="A professional text summarization service using extractive summarization algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    text: str
    max_words: Optional[int] = 200

# Ensure punkt
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    logger.info("Downloading punkt...")
    nltk.download("punkt")

# Tunable limits (set via env)
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "200000"))  # refuse bigger than this
CHUNK_CHAR_TARGET = int(os.getenv("CHUNK_CHAR_TARGET", "45000"))  # target chars per chunk
MAX_SENTENCE_COUNT = int(os.getenv("MAX_SENTENCE_COUNT", "200"))

def split_text_to_chunks_by_sentences(text: str, chunk_target_chars: int) -> List[str]:
    """Split text into chunks by grouping sentences until chunk_target_chars reached."""
    sents = sent_tokenize(text)
    chunks = []
    current = []
    current_len = 0
    for sent in sents:
        slen = len(sent) + 1
        if current and current_len + slen > chunk_target_chars:
            chunks.append(" ".join(current).strip())
            current = [sent]
            current_len = slen
        else:
            current.append(sent)
            current_len += slen
    if current:
        chunks.append(" ".join(current).strip())
    # fallback: if no sentences (weird), split raw by char windows
    if not chunks:
        for i in range(0, len(text), chunk_target_chars):
            chunks.append(text[i : i + chunk_target_chars])
    return chunks

def summarize_text_with_sumy(text: str, sentence_count: int, prefer="lexrank") -> List[str]:
    """Return list of summary sentences (strings). Try lexrank, fallback to lsa."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    if prefer == "lexrank":
        try:
            summ = LexRankSummarizer()
            sents = [str(s).strip() for s in summ(parser.document, sentence_count) if str(s).strip()]
            if sents:
                return sents
        except Exception as e:
            logger.warning("LexRank failed: %s", e)
    # fallback
    try:
        summ = LsaSummarizer()
        sents = [str(s).strip() for s in summ(parser.document, sentence_count) if str(s).strip()]
        if sents:
            return sents
    except Exception as e:
        logger.warning("LSA failed: %s", e)
    # final fallback: first N sentences from original
    raw_sents = sent_tokenize(text)
    return raw_sents[: max(1, min(len(raw_sents), sentence_count))]

def ordered_join(sentences: List[str], original_text: str) -> str:
    """Return sentences ordered by their first appearance in original_text, joined."""
    lowered = original_text.lower()
    ordered = sorted(
        sentences,
        key=lambda s: lowered.find(s.lower()) if lowered.find(s.lower()) != -1 else float("inf"),
    )
    return " ".join(ordered).strip()

@app.post("/summarize")
async def summarize(req: SummarizeRequest, request: Request):
    try:
        text = (req.text or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="No text provided.")

        # size guard
        if len(text) > MAX_INPUT_CHARS:
            detail = f"Input too large ({len(text)} chars). Max allowed: {MAX_INPUT_CHARS} chars."
            logger.warning(detail)
            raise HTTPException(status_code=413, detail=detail)

        target_words = max(30, min(800, req.max_words or 200))

        # If already short, return original (or truncated)
        total_words = len(text.split())
        if total_words <= target_words + 20:
            return {"summary": text, "word_count": total_words, "method": "original"}

        # Split into chunks
        chunks = split_text_to_chunks_by_sentences(text, CHUNK_CHAR_TARGET)
        logger.info("Text split into %d chunk(s) (target %d chars)", len(chunks), CHUNK_CHAR_TARGET)

        # For each chunk, compute sentence budget roughly proportional to chunk length
        partial_summaries = []
        for chunk in chunks:
            # compute sentence count: estimate avg words per sentence in chunk
            sents = sent_tokenize(chunk)
            if not sents:
                sent_count = 1
            else:
                words = sum(len(s.split()) for s in sents)
                avg_words_per_sent = max(1, words / len(sents))
                sent_count = max(1, int(math.ceil((target_words / len(chunks)) / avg_words_per_sent)))
            sent_count = min(sent_count, MAX_SENTENCE_COUNT)
            try:
                sents_out = summarize_text_with_sumy(chunk, sent_count, prefer="lexrank")
                partial_summaries.append(" ".join(sents_out))
            except Exception as e:
                logger.error("Error summarizing chunk: %s", e)
                # fallback: first sent_count sentences
                partial_summaries.append(" ".join(sents[: max(1, min(len(sents), sent_count))]))

        # Combine partial summaries
        combined = "\n\n".join([p for p in partial_summaries if p.strip()])
        logger.info("Combined partial summaries length: %d chars", len(combined))

        # Final summarization pass: aim for target_words
        # Determine final sentence_count from combined text
        final_sents = sent_tokenize(combined)
        if not final_sents:
            # nothing sensible, fallback to first N sentences of original
            final_summary = " ".join(sent_tokenize(text)[: max(1, min(len(sent_tokenize(text)), 5))])
            method_used = "fallback-first-sents"
        else:
            words_combined = sum(len(s.split()) for s in final_sents)
            avg_words_per_sent = max(1, words_combined / len(final_sents))
            final_sent_count = max(1, int(math.ceil(target_words / avg_words_per_sent)))
            final_sent_count = min(final_sent_count, MAX_SENTENCE_COUNT)
            final_sentences = summarize_text_with_sumy(combined, final_sent_count, prefer="lexrank")
            final_summary = ordered_join(final_sentences, combined)
            method_used = "chunked-lexrank"

        # Post-trim to be near target_words
        w = final_summary.split()
        if len(w) > target_words + 30:
            final_summary = " ".join(w[: target_words + 30])

        return {"summary": final_summary, "word_count": len(final_summary.split()), "method": method_used}

    except HTTPException:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("Unhandled exception in /summarize:\n%s", tb)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "exception": str(exc), "traceback": tb},
        )

@app.get("/")
async def root():
    return {
        "message": "FreeSummarizer API is running",
        "version": "1.0.0",
        "endpoints": {
            "summarize": "POST /summarize - Summarize text",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "usage": "POST /summarize with JSON {text, max_words}"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and deployment"""
    try:
        # Test NLTK availability
        nltk.data.find("tokenizers/punkt")
        nltk_status = "available"
    except LookupError:
        nltk_status = "punkt_missing"
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "nltk_status": nltk_status,
        "limits": {
            "max_input_chars": MAX_INPUT_CHARS,
            "chunk_target_chars": CHUNK_CHAR_TARGET,
            "max_sentence_count": MAX_SENTENCE_COUNT
        }
    }
