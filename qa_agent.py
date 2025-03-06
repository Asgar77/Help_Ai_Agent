import argparse
import requests
import ollama
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import time

# 🛑 User-Agent to prevent blocking when crawling websites
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ✅ Validate URL Format
def is_valid_url(url):
    """Checks if the given URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# ✅ Crawl Website for Documentation Pages
def crawl_website(base_url, max_pages=50, visited=None):
    """Recursively crawls a help website and extracts pages."""
    if visited is None:
        visited = set()

    if len(visited) >= max_pages or base_url in visited:
        return []

    print(f"Crawling: {base_url}")
    
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {base_url}: Status {response.status_code}")
            return []

        visited.add(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pages = [(base_url, soup)]
        
        # Extract and follow documentation-related links
        base_domain = urlparse(base_url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)

            parsed_url = urlparse(full_url)
            if (parsed_url.netloc == base_domain and 
                full_url not in visited and
                any(keyword in full_url.lower() for keyword in ["help", "docs", "guide", "faq", "tutorial"])):
                
                child_pages = crawl_website(full_url, max_pages, visited)
                pages.extend(child_pages)
                if len(visited) >= max_pages:
                    break

        return pages
    except Exception as e:
        print(f"Error crawling {base_url}: {str(e)}")
        return []

# ✅ Extract Relevant Content from Pages
def extract_content(soup):
    """Extracts meaningful content while removing unnecessary elements."""
    for element in soup.select('nav, header, footer, aside, .navigation, .menu, .sidebar, .footer, .header'):
        element.decompose()

    main_content = soup.select('main, article, .content, .main, #content, #main')
    if main_content:
        return " ".join([element.get_text(strip=True, separator=' ') for element in main_content])
    else:
        return soup.body.get_text(strip=True, separator=' ') if soup.body else ""

# ✅ Load Website Content
def load_website_content(url):
    """Loads and processes documentation content from a website."""
    if not is_valid_url(url):
        raise ValueError("Invalid URL format")

    try:
        pages = crawl_website(url)
        if not pages:
            raise ValueError(f"Could not retrieve content from {url}")

        documents = []
        for page_url, soup in pages:
            content = extract_content(soup)
            if content:
                documents.append({"page_content": content, "metadata": {"source": page_url}})

        print(f"Extracted {len(documents)} pages")
        return documents
    except Exception as e:
        raise Exception(f"Error loading website content: {str(e)}")

# ✅ Q&A Agent Class
class QAAgent:
    def __init__(self, url, model_name="llama3.2:latest", embed_model="nomic-embed-text"):
        self.url = url
        self.model_name = model_name
        self.embed_model = embed_model
        self.vectorstore = None

    # ✅ Process & Index Documentation
    def process_documentation(self):
        """Processes and indexes documentation content."""
        try:
            print(f"Loading content from {self.url}...")
            documents = load_website_content(self.url)

            docs = [Document(page_content=doc["page_content"], metadata=doc["metadata"]) for doc in documents]
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = text_splitter.split_documents(docs)

            print(f"Processed {len(docs)} pages into {len(splits)} chunks")

            embeddings = OllamaEmbeddings(model=self.embed_model)
            persist_directory = "data/chroma"
            os.makedirs(persist_directory, exist_ok=True)

            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=persist_directory
            )

            return True
        except Exception as e:
            print(f"Error processing documentation: {str(e)}")
            return False

    # ✅ Answer User Questions
    def answer_question(self, question):
        """Finds relevant answers based on indexed documentation."""
        if not self.vectorstore:
            return "Error: Documentation has not been processed yet."

        try:
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            retrieved_docs = retriever.invoke(question)

            context = "\n\n".join([
                f"[From: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}" 
                for doc in retrieved_docs
            ])

            if not context:
                return "I couldn't find any relevant information in the documentation."

            prompt = f"""You are a helpful documentation assistant. 
            Answer the following question based ONLY on the provided context.
            If the information is not in the context, respond with "I don't have information about that in the documentation."
            
            Question: {question}
            
            Context:
            {context}
            """

            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )

            answer = response['message']['content']
            sources = list(set([doc.metadata.get('source', 'unknown') for doc in retrieved_docs]))
            sources_text = "\n\nSources:\n" + "\n".join([f"- {source}" for source in sources])

            return answer + sources_text

        except Exception as e:
            return f"Error answering question: {str(e)}"

