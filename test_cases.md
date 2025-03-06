# 🧪 Test Cases & Validation

## ✅ **1. URL Validation**
| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| Valid URL | `https://help.example.com` | Pass: URL accepted |
| Invalid URL | `invalid_url` | Error: Invalid URL format |
| Empty URL | `''` | Error: URL cannot be empty |

## ✅ **2. Website Crawling & Extraction**
| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| Reachable Help Page | `https://help.slack.com` | Successfully extracts documentation |
| Page Not Found | `https://help.example.com/404` | Error: Page not found |
| JavaScript-Heavy Page | `https://docs.example.com` | Might fail (improvement needed) |

## ✅ **3. Text Processing & Indexing**
| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| Large Documentation | 100+ pages | Successfully indexed in ChromaDB |
| No Extractable Content | `https://example.com/empty` | Warning: No meaningful content found |
| Repeated Crawling | Same website twice | Doesn't duplicate entries in ChromaDB |

## ✅ **4. Question Answering**
| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| Relevant Question | `What integrations are available?` | Provides correct answer with source reference |
| No Relevant Information | `Does this support XYZ feature?` | "No information available" response |
| Ambiguous Question | `How does it work?` | Requests more details from the user |

## ✅ **5. Performance Benchmarks**
| Metric | Expected Value |
|--------|---------------|
| Documentation Processing Time | < 10 seconds for 50 pages |
| Query Response Time | < 2 seconds |

---
🚀 **Use `pytest tests/` to run these cases.**
