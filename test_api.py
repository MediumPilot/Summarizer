import requests
import json

def test_summarizer():
    """Test the FreeSummarizer API"""
    
    # Test data
    test_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often used to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".

    The scope of AI is disputed: as machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect. A quip in Tesler's Theorem says "AI is whatever hasn't been done yet." For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.

    Modern machine learning techniques are at the core of AI. Problems for AI applications include reasoning, knowledge representation, planning, learning, natural language processing, perception, and the ability to move and manipulate objects. General intelligence is among the field's long-term goals.
    """

    # API endpoint
    base_url = "http://localhost:8000"
    
    print("Testing FreeSummarizer API...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print("✓ Root endpoint test:")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        print()
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Make sure the server is running:")
        print("  uvicorn main:app --reload")
        return
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")
        return
    
    # Test 2: Summarization endpoint
    try:
        data = {
            "text": test_text,
            "max_words": 100
        }
        
        response = requests.post(f"{base_url}/summarize", json=data)
        print("✓ Summarization test:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Summary length: {result['word_count']} words")
            print(f"  Method: {result['method']}")
            print(f"  Summary: {result['summary'][:100]}...")
        else:
            print(f"  Error: {response.text}")
        print()
    except Exception as e:
        print(f"✗ Summarization error: {e}")
        return
    
    # Test 3: Edge case - short text
    try:
        short_data = {
            "text": "This is a very short text.",
            "max_words": 50
        }
        
        response = requests.post(f"{base_url}/summarize", json=short_data)
        print("✓ Short text test:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Method: {result['method']}")
            print(f"  Summary: {result['summary']}")
        print()
    except Exception as e:
        print(f"✗ Short text test error: {e}")
    
    print("Testing complete!")

if __name__ == "__main__":
    test_summarizer()