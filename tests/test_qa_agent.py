import pytest
import requests
from qa_agent import is_valid_url, crawl_website, extract_content, QAAgent
import time

# ✅ Test URL Validation
def test_valid_url():
    assert is_valid_url("https://help.example.com") == True
    assert is_valid_url("http://docs.example.com") == True
    assert is_valid_url("invalid_url") == False
    assert is_valid_url("") == False

# ✅ Test Crawling Functionality
def test_crawl_website():
    url = "https://example.com/help"
    try:
        pages = crawl_website(url, max_pages=2)
        assert isinstance(pages, list)
    except requests.exceptions.RequestException:
        pytest.skip("Skipping test due to network issue")

# ✅ Test Content Extraction
def test_extract_content():
    html = """<html><body><main><p>Help Content</p></main></body></html>"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    content = extract_content(soup)
    assert "Help Content" in content

# ✅ Test Q&A Agent Processing
def test_qa_agent_processing():
    agent = QAAgent("https://help.example.com")
    success = agent.process_documentation()
    assert success == True

# ✅ Test Q&A Response Time
def test_qa_response_time():
    agent = QAAgent("https://help.example.com")
    agent.process_documentation()
    question = "What integrations are available?"
    start_time = time.time()
    answer = agent.answer_question(question)
    end_time = time.time()
    assert len(answer) > 0
    assert (end_time - start_time) < 3  # Ensure response is under 3 seconds

if __name__ == "__main__":
    pytest.main()
