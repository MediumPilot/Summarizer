"""
Comprehensive Test Suite for FreeSummarizer API
This file contains 10+ detailed test cases to thoroughly test the summarization API
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

class SummarizerTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result and update counters"""
        status = "✓ PASSED" if passed else "✗ FAILED"
        result = {
            "test_name": test_name,
            "status": status,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
        print()
    
    def test_server_connectivity(self) -> bool:
        """Test 1: Check if server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_test_result("Server Connectivity", True, f"Server responded with status {response.status_code}")
                return True
            else:
                self.log_test_result("Server Connectivity", False, f"Unexpected status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test_result("Server Connectivity", False, "Connection refused - server not running")
            return False
        except Exception as e:
            self.log_test_result("Server Connectivity", False, f"Error: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """Test 2: Test root endpoint response"""
        try:
            response = requests.get(f"{self.base_url}/")
            data = response.json()
            
            expected_message = "FreeSummarizer API is running"
            if response.status_code == 200 and data.get("message") == expected_message and "version" in data:
                self.log_test_result("Root Endpoint", True, f"Correct API info returned, version: {data.get('version')}")
            else:
                self.log_test_result("Root Endpoint", False, f"Unexpected response: {data}")
        except Exception as e:
            self.log_test_result("Root Endpoint", False, f"Error: {str(e)}")
    
    def test_basic_summarization(self):
        """Test 3: Basic text summarization functionality"""
        test_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often used to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".

        The scope of AI is disputed: as machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect. A quip in Tesler's Theorem says "AI is whatever hasn't been done yet." For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.

        Modern machine learning techniques are at the core of AI. Problems for AI applications include reasoning, knowledge representation, planning, learning, natural language processing, perception, and the ability to move and manipulate objects. General intelligence is among the field's long-term goals.
        """
        
        try:
            data = {"text": test_text.strip(), "max_words": 100}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                word_count = result.get("word_count", 0)
                summary = result.get("summary", "")
                method = result.get("method", "")
                
                if summary and word_count > 0 and word_count <= 130:  # Allow some flexibility
                    self.log_test_result("Basic Summarization", True, 
                                       f"Summary generated: {word_count} words, method: {method}")
                else:
                    self.log_test_result("Basic Summarization", False, 
                                       f"Invalid summary: {word_count} words, method: {method}")
            else:
                self.log_test_result("Basic Summarization", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Basic Summarization", False, f"Error: {str(e)}")
    
    def test_short_text_handling(self):
        """Test 4: Handle short text that doesn't need summarization"""
        short_text = "This is a very short text that doesn't need summarization."
        
        try:
            data = {"text": short_text, "max_words": 50}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                method = result.get("method", "")
                summary = result.get("summary", "")
                
                if method == "original" and summary == short_text:
                    self.log_test_result("Short Text Handling", True, 
                                       f"Correctly returned original text, method: {method}")
                else:
                    self.log_test_result("Short Text Handling", False, 
                                       f"Unexpected handling: method={method}, summary={summary[:50]}...")
            else:
                self.log_test_result("Short Text Handling", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Short Text Handling", False, f"Error: {str(e)}")
    
    def test_empty_text_validation(self):
        """Test 5: Validate empty text input"""
        try:
            data = {"text": "", "max_words": 100}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 400:
                self.log_test_result("Empty Text Validation", True, 
                                   "Correctly rejected empty text with 400 status")
            else:
                self.log_test_result("Empty Text Validation", False, 
                                   f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test_result("Empty Text Validation", False, f"Error: {str(e)}")
    
    def test_whitespace_only_text(self):
        """Test 6: Handle whitespace-only text"""
        try:
            data = {"text": "   \n\t   ", "max_words": 100}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 400:
                self.log_test_result("Whitespace-Only Text", True, 
                                   "Correctly rejected whitespace-only text")
            else:
                self.log_test_result("Whitespace-Only Text", False, 
                                   f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test_result("Whitespace-Only Text", False, f"Error: {str(e)}")
    
    def test_word_count_limits(self):
        """Test 7: Test different word count limits"""
        test_text = """
        Climate change refers to long-term shifts in global or regional climate patterns. Since the mid-20th century, scientists have observed unprecedented changes in Earth's climate system, primarily attributed to increased levels of greenhouse gases produced by human activities. The burning of fossil fuels, deforestation, and industrial processes have significantly increased atmospheric concentrations of carbon dioxide, methane, and other greenhouse gases.

        The effects of climate change are wide-ranging and include rising global temperatures, melting ice caps and glaciers, rising sea levels, and more frequent extreme weather events such as hurricanes, droughts, and heatwaves. These changes pose significant threats to ecosystems, biodiversity, agriculture, water resources, and human settlements, particularly in vulnerable regions.

        Addressing climate change requires coordinated global action, including transitioning to renewable energy sources, improving energy efficiency, protecting and restoring forests, and developing sustainable transportation systems. International agreements like the Paris Climate Accord aim to limit global warming and promote climate resilience.
        """
        
        word_limits = [50, 100, 200, 300]
        all_passed = True
        
        for limit in word_limits:
            try:
                data = {"text": test_text.strip(), "max_words": limit}
                response = requests.post(f"{self.base_url}/summarize", json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    word_count = result.get("word_count", 0)
                    
                    # Allow some flexibility (±30 words as per the algorithm)
                    if word_count <= limit + 30:
                        continue
                    else:
                        all_passed = False
                        break
                else:
                    all_passed = False
                    break
            except Exception:
                all_passed = False
                break
        
        if all_passed:
            self.log_test_result("Word Count Limits", True, 
                               f"All word limits respected: {word_limits}")
        else:
            self.log_test_result("Word Count Limits", False, 
                               f"Word limit validation failed for limit: {limit}")
    
    def test_large_text_processing(self):
        """Test 8: Process large text (chunking functionality)"""
        # Create a large text by repeating content
        base_text = """
        Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. Unlike traditional programming where explicit instructions are provided, machine learning systems learn patterns from data and make predictions or decisions without being explicitly programmed for every scenario.

        There are several types of machine learning approaches. Supervised learning uses labeled training data to learn a mapping function from inputs to outputs. Common supervised learning tasks include classification, where the goal is to predict discrete categories, and regression, where the goal is to predict continuous values. Unsupervised learning, on the other hand, works with unlabeled data to discover hidden patterns or structures, such as clustering similar data points or reducing dimensionality.

        Deep learning, a subset of machine learning, uses artificial neural networks with multiple layers to model and understand complex patterns in data. These deep neural networks have achieved remarkable success in various domains including computer vision, natural language processing, and speech recognition. The availability of large datasets and powerful computing resources has been crucial for the advancement of deep learning techniques.
        """
        
        # Repeat to create large text (approximately 50KB)
        large_text = (base_text * 50).strip()
        
        try:
            data = {"text": large_text, "max_words": 150}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                method = result.get("method", "")
                word_count = result.get("word_count", 0)
                
                if "chunked" in method and word_count > 0:
                    self.log_test_result("Large Text Processing", True, 
                                       f"Successfully processed large text: {len(large_text)} chars, method: {method}")
                else:
                    self.log_test_result("Large Text Processing", False, 
                                       f"Unexpected processing: method={method}, words={word_count}")
            else:
                self.log_test_result("Large Text Processing", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Large Text Processing", False, f"Error: {str(e)}")
    
    def test_extremely_large_text_rejection(self):
        """Test 9: Reject extremely large text input"""
        # Create text larger than MAX_INPUT_CHARS (200,000)
        huge_text = "A" * 250000  # 250KB of text
        
        try:
            data = {"text": huge_text, "max_words": 100}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 413:  # Payload Too Large
                self.log_test_result("Extremely Large Text Rejection", True, 
                                   "Correctly rejected oversized input with 413 status")
            else:
                self.log_test_result("Extremely Large Text Rejection", False, 
                                   f"Expected 413, got {response.status_code}")
        except Exception as e:
            self.log_test_result("Extremely Large Text Rejection", False, f"Error: {str(e)}")
    
    def test_special_characters_handling(self):
        """Test 10: Handle text with special characters and formatting"""
        special_text = """
        The Schrödinger equation is a linear partial differential equation that governs the wave function of a quantum-mechanical system. It is a key result in quantum mechanics, and its discovery was a significant landmark in the development of the subject. The equation is named after Erwin Schrödinger, who postulated the equation in 1925, and published it in 1926, forming the basis for the work that resulted in his Nobel Prize in Physics in 1933.

        Mathematically, the time-dependent Schrödinger equation is: iℏ ∂/∂t |ψ⟩ = Ĥ |ψ⟩

        Here, ψ (psi) represents the wave function, ℏ is the reduced Planck constant, and Ĥ is the Hamiltonian operator. The equation describes how the quantum state of a physical system changes with time.

        Special characters: àáâãäåæçèéêëìíîïñòóôõöøùúûüý
        Symbols: ∑∏∫∂∇∆Ω∞±≤≥≠≈∈∉⊂⊃∪∩
        """
        
        try:
            data = {"text": special_text.strip(), "max_words": 80}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary", "")
                word_count = result.get("word_count", 0)
                
                if summary and word_count > 0:
                    self.log_test_result("Special Characters Handling", True, 
                                       f"Successfully processed text with special characters: {word_count} words")
                else:
                    self.log_test_result("Special Characters Handling", False, 
                                       "Failed to generate summary from special characters text")
            else:
                self.log_test_result("Special Characters Handling", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Special Characters Handling", False, f"Error: {str(e)}")
    
    def test_multilingual_text(self):
        """Test 11: Handle multilingual text (primarily English with some foreign words)"""
        multilingual_text = """
        Globalization has led to increased cultural exchange and the adoption of foreign words into English. For example, "entrepreneur" comes from French, "kindergarten" from German, "tsunami" from Japanese, and "fiesta" from Spanish. This linguistic borrowing enriches the English language and reflects our interconnected world.

        In business contexts, terms like "kaizen" (Japanese for continuous improvement), "feng shui" (Chinese for harmonious arrangement), and "savoir-faire" (French for know-how) are commonly used. These borrowed words often capture concepts that don't have direct English equivalents.

        The phenomenon of code-switching, where speakers alternate between languages within a conversation, is common in multilingual communities. This practice demonstrates the dynamic nature of language and how speakers adapt their communication to their audience and context.
        """
        
        try:
            data = {"text": multilingual_text.strip(), "max_words": 70}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary", "")
                word_count = result.get("word_count", 0)
                
                if summary and word_count > 0:
                    self.log_test_result("Multilingual Text Handling", True, 
                                       f"Successfully processed multilingual text: {word_count} words")
                else:
                    self.log_test_result("Multilingual Text Handling", False, 
                                       "Failed to generate summary from multilingual text")
            else:
                self.log_test_result("Multilingual Text Handling", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Multilingual Text Handling", False, f"Error: {str(e)}")
    
    def test_technical_document_summarization(self):
        """Test 12: Summarize technical documentation"""
        technical_text = """
        RESTful APIs (Representational State Transfer) are architectural principles for designing networked applications. REST relies on a stateless, client-server communication protocol, typically HTTP. RESTful applications use HTTP requests to perform CRUD (Create, Read, Update, Delete) operations on resources.

        Key principles of REST include: 1) Stateless communication - each request contains all information needed to process it; 2) Client-server architecture - separation of concerns between client and server; 3) Cacheable responses - responses should be cacheable when appropriate; 4) Uniform interface - consistent way to interact with resources; 5) Layered system - architecture can be composed of hierarchical layers.

        HTTP methods in REST: GET retrieves data, POST creates new resources, PUT updates existing resources, DELETE removes resources, PATCH partially updates resources. Status codes indicate the result: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Internal Server Error).

        JSON (JavaScript Object Notation) is the most common data format for REST APIs due to its lightweight nature and easy parsing. Authentication methods include API keys, OAuth 2.0, and JWT tokens. Rate limiting prevents abuse by restricting the number of requests per time period.
        """
        
        try:
            data = {"text": technical_text.strip(), "max_words": 120}
            response = requests.post(f"{self.base_url}/summarize", json=data)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary", "")
                word_count = result.get("word_count", 0)
                method = result.get("method", "")
                
                # Check if technical terms are preserved
                technical_terms = ["REST", "API", "HTTP", "JSON"]
                terms_preserved = sum(1 for term in technical_terms if term in summary)
                
                if summary and word_count > 0 and terms_preserved >= 2:
                    self.log_test_result("Technical Document Summarization", True, 
                                       f"Successfully summarized technical content: {word_count} words, {terms_preserved}/4 key terms preserved")
                else:
                    self.log_test_result("Technical Document Summarization", False, 
                                       f"Technical summarization issues: {word_count} words, {terms_preserved}/4 terms preserved")
            else:
                self.log_test_result("Technical Document Summarization", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Technical Document Summarization", False, f"Error: {str(e)}")
    
    def test_response_time_performance(self):
        """Test 13: Measure API response time performance"""
        test_text = """
        Renewable energy sources are becoming increasingly important as the world seeks to reduce greenhouse gas emissions and combat climate change. Solar power harnesses energy from the sun using photovoltaic cells or solar thermal collectors. Wind power uses turbines to convert kinetic energy from wind into electricity. Hydroelectric power generates electricity from flowing water, typically through dams.

        Other renewable sources include geothermal energy, which taps into Earth's internal heat, and biomass energy, which comes from organic materials. Each renewable energy source has its advantages and challenges. Solar and wind are intermittent, requiring energy storage solutions. Hydroelectric power can impact local ecosystems. Geothermal is location-dependent.

        The transition to renewable energy requires significant infrastructure investment, policy support, and technological advancement. Energy storage technologies like batteries are crucial for managing the intermittent nature of some renewable sources. Smart grids can help optimize energy distribution and consumption.
        """
        
        try:
            data = {"text": test_text.strip(), "max_words": 100}
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/summarize", json=data)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time < 10.0:  # Should respond within 10 seconds
                self.log_test_result("Response Time Performance", True, 
                                   f"API responded in {response_time:.2f} seconds")
            elif response.status_code == 200:
                self.log_test_result("Response Time Performance", False, 
                                   f"API too slow: {response_time:.2f} seconds")
            else:
                self.log_test_result("Response Time Performance", False, 
                                   f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test_result("Response Time Performance", False, f"Error: {str(e)}")
    
    def test_concurrent_requests(self):
        """Test 14: Handle multiple concurrent requests"""
        import threading
        import queue
        
        test_text = """
        Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative.
        """
        
        results_queue = queue.Queue()
        
        def make_request():
            try:
                data = {"text": test_text.strip(), "max_words": 50}
                response = requests.post(f"{self.base_url}/summarize", json=data, timeout=15)
                results_queue.put(response.status_code == 200)
            except Exception:
                results_queue.put(False)
        
        # Create 5 concurrent threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        successful_requests = 0
        while not results_queue.empty():
            if results_queue.get():
                successful_requests += 1
        
        if successful_requests >= 4:  # Allow 1 failure out of 5
            self.log_test_result("Concurrent Requests", True, 
                               f"{successful_requests}/5 concurrent requests successful")
        else:
            self.log_test_result("Concurrent Requests", False, 
                               f"Only {successful_requests}/5 concurrent requests successful")
    
    def test_api_documentation_endpoints(self):
        """Test 15: Check if API documentation endpoints are accessible"""
        endpoints_to_test = ["/docs", "/redoc"]
        all_accessible = True
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code != 200:
                    all_accessible = False
                    break
            except Exception:
                all_accessible = False
                break
        
        if all_accessible:
            self.log_test_result("API Documentation Endpoints", True, 
                               "Both /docs and /redoc endpoints accessible")
        else:
            self.log_test_result("API Documentation Endpoints", False, 
                               "Documentation endpoints not accessible")
    
    def run_all_tests(self):
        """Run all test cases and generate a comprehensive report"""
        print("=" * 80)
        print("FREESUMMARIZER API - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print()
        
        # Check server connectivity first
        if not self.test_server_connectivity():
            print("❌ Cannot proceed with tests - server is not accessible")
            print("Please ensure the server is running with: uvicorn main:app --reload")
            return
        
        print("🚀 Running comprehensive test suite...\n")
        
        # Run all tests
        test_methods = [
            self.test_root_endpoint,
            self.test_basic_summarization,
            self.test_short_text_handling,
            self.test_empty_text_validation,
            self.test_whitespace_only_text,
            self.test_word_count_limits,
            self.test_large_text_processing,
            self.test_extremely_large_text_rejection,
            self.test_special_characters_handling,
            self.test_multilingual_text,
            self.test_technical_document_summarization,
            self.test_response_time_performance,
            self.test_concurrent_requests,
            self.test_api_documentation_endpoints
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test_result(test_name, False, f"Test execution error: {str(e)}")
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate and display final test report"""
        total_tests = len(self.test_results)
        success_rate = (self.passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("=" * 80)
        print("FINAL TEST REPORT")
        print("=" * 80)
        print(f"Total Tests Run: {total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if not result["passed"]:
                    print(f"❌ {result['test_name']}: {result['details']}")
            print()
        
        print("DETAILED RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            status_icon = "✅" if result["passed"] else "❌"
            print(f"{status_icon} {result['test_name']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Your API is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD! Your API is mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️  NEEDS IMPROVEMENT! Several issues need to be addressed.")
        else:
            print("❌ CRITICAL ISSUES! Major problems need to be fixed.")
        
        print("=" * 80)

def main():
    """Main function to run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive test suite for FreeSummarizer API")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    tester = SummarizerTester(args.url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()