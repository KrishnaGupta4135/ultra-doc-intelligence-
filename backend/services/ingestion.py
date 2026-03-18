from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from pypdf import PdfReader
import docx
import re
from dotenv import load_dotenv
import os

load_dotenv()

VECTOR_PATH = "vector_store"

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b',
                  lambda m: m.group(0).replace(" ", ""),
                  text)
    text = re.sub(r'\s*@\s*', '@', text)
    text = re.sub(r'\s*\.\s*', '.', text)
    text = re.sub(r'(?<=\d)\s+(?=\d)', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return text.strip()

def load_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = "\n".join([p.extract_text() or "" for p in reader.pages])

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return clean_text(text)

def process_document(doc_id, file_path):
    text = load_text(file_path)

    # chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_text(text)
    # Add metadata for each chunk
    metadatas = [
        {
            "doc_id": doc_id,
            "chunk_id": i
        }
        for i in range(len(chunks))
    ]

    embeddings = OpenAIEmbeddings()

    db = FAISS.from_texts(
        chunks,
        embeddings,
        metadatas=metadatas
    )

    os.makedirs(VECTOR_PATH, exist_ok=True)
    db.save_local(f"{VECTOR_PATH}/{doc_id}")