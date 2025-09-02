# main.py
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math

# small NLP libs
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
from nltk import sent_tokenize

app = FastAPI(title="FreeSummarizer")

class SummarizeRequest(BaseModel):
    text: str
    max_words: Optional[int] = 200  # target words in summary

# Ensure necessary NLTK data present (punkt). It's small (~13MB).
# On first run this will download punkt if missing.
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def approx_sentence_count_for_target(text: str, target_words: int) -> int:
    sentences = sent_tokenize(text)
    if not sentences:
        return 1
    words = sum(len(s.split()) for s in sentences)
    avg_words_per_sentence = max(1, words / len(sentences))
    return max(1, int(math.ceil(target_words / avg_words_per_sentence)))

@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided.")

    # sanitize max_words
    target_words = max(30, min(800, req.max_words or 200))

    # If text is short, return it (or truncated)
    total_words = len(text.split())
    if total_words <= target_words + 20:
        # already short enough
        return {"summary": text, "word_count": total_words, "method": "original"}

    # compute how many sentences to request from the extractive summarizer
    sentence_count = approx_sentence_count_for_target(text, target_words)

    # Use Sumy + LexRank (unsupervised extractive). Lightweight and free.
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)

    # Keep original order: map sentences to their first occurrence index in the original text
    summary_texts = [str(s).strip() for s in summary_sentences if str(s).strip()]
    # some safety: if sumy returned nothing, fallback
    if not summary_texts:
        # fallback: take first N sentences
        fallback_sentences = sent_tokenize(text)[:sentence_count]
        summary_texts = fallback_sentences

    # Order by where each sentence appears in original text
    lowered = text.lower()
    ordered = sorted(
        summary_texts,
        key=lambda s: lowered.find(s.lower()) if lowered.find(s.lower()) != -1 else float("inf"),
    )

    summary = " ".join(ordered).strip()

    # Post-trim to be near target_words (not exact)
    words = summary.split()
    if len(words) > target_words + 30:
        summary = " ".join(words[: target_words + 30])

    return {
        "summary": summary,
        "word_count": len(summary.split()),
        "method": "extractive-lexrank"
    }

# basic root
@app.get("/")
async def root():
    return {"message": "FreeSummarizer up. POST /summarize with JSON {text, max_words}."}
