# Document AI System (RAG + Extraction)

An end-to-end **Document Intelligence System** built using:

* FastAPI (Backend)
* LLM (OpenAI)
* RAG (FAISS Vector DB)
* Streamlit (Frontend)

This system allows you to:

* Upload documents (PDF, DOCX, TXT)
* Ask questions about documents (RAG-based QA)
* Extract structured data from documents
* Get confidence scores with guardrails

---

# Features

## 1. Document Upload

* Upload any document (PDF, DOCX, TXT)
* Automatically:

  * Reads content
  * Cleans text
  * Splits into chunks
  * Stores embeddings in FAISS

---

## 2. Ask Questions (RAG)

Example questions:

* What is the customer name?
* What is the carrier rate?
* When is pickup scheduled?

System:

* Retrieves relevant chunks
* Uses LLM to answer
* Returns:

  * Answer
  * Source text
  * Confidence score

---

## 3. Structured Data Extraction

Extract fields like:

* shipment_id
* shipper
* consignee
* pickup_datetime
* delivery_datetime
* rate
* currency
* weight

Returns:

```json
{
  "shipment_id": "...",
  "shipper": "...",
  "rate": 1000,
  "currency": "USD"
}
```

---

## 4. Guardrails

System prevents hallucination using:

* Similarity threshold
* Confidence scoring
* Strict prompting

If data not found:

```
"Not found in document"
```

---

# Project Structure

```
.
│   main.py                  # Entry point (runs FastAPI)
│
├── routes/                 # API endpoints
│   ├── upload.py           # Upload document
│   ├── ask.py              # Ask questions
│   ├── extract.py          # Extract structured data
│
├── services/               # Core logic
│   ├── ingestion.py        # Document processing & vector DB
│   ├── rag.py              # Question answering logic
│   ├── extraction.py       # Structured extraction
│   ├── guardrails.py       # Safety checks
│
├── frontend/
│   └── streamlit_app.py    # UI (chat interface)
│
├── data/                   # Uploaded files
├── vector_store/           # FAISS embeddings
```

---

# Setup Instructions

## 1. Clone Project

```bash
git clone <your-repo>
cd project-folder
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt

or

uv add -r requirements.txt
```


---

## 🔹 4. Setup Environment Variables

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

# Running the Project

## Option 1: Run Backend Only

```bash
python main.py
```

Server runs at:

```
http://localhost:8000
```

---

## Option 2: Run Frontend (Streamlit)

```bash
streamlit run frontend/streamlit_app.py
```

Runs at:

```
http://localhost:8501
```

---

## Option 3: Run Both Together (Recommended)

Create `main.py`:

```python
import subprocess
import sys

subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--reload"])
subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
```

Run:

```bash
python main.py
```

---

# API Endpoints

## Upload Document

```
POST /upload
```

---

## Ask Question

```
POST /ask
```

Request:

```json
{
  "doc_id": "your_doc_id",
  "question": "What is the customer name?"
}
```

---

## Extract Data

```
GET /extract/{doc_id}
```

---

# How It Works

## 1. Ingestion (`ingestion.py`)

* Reads document
* Cleans text
* Splits into chunks
* Creates embeddings
* Stores in FAISS

---

## 2. RAG (`rag.py`)

* Rewrites query
* Retrieves relevant chunks
* Uses LLM to answer
* Applies guardrails
* Calculates confidence

---

## 3. Extraction (`extraction.py`)

* Retrieves context
* Uses structured prompt
* Returns JSON output

---

## 4. Guardrails (`guardrails.py`)

* Filters low-quality results
* Prevents hallucination
* Controls confidence threshold

---

# Confidence Score

Calculated using:

* Retrieval similarity
* Chunk agreement
* Answer coverage

---

# Limitations

* OCR-heavy PDFs may need preprocessing
* Very large documents may need chunk tuning
* Depends on embedding quality

---

# Future Improvements

* Multi-document search
* Hybrid search (BM25 + Vector)
* UI enhancements
* Caching layer
* Docker deployment

---

# Final Note

This project demonstrates:

* Real-world RAG pipeline
* Production-style LLM integration
* Safe & reliable document AI system
