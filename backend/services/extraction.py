from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import json

load_dotenv()

VECTOR_PATH = "vector_store"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

def extract_data(doc_id):
    db = FAISS.load_local(
        f"{VECTOR_PATH}/{doc_id}",
        embeddings,
        allow_dangerous_deserialization=True
    )
    docs = db.similarity_search(
        "shipment details, customer, pickup, delivery, rate, weight",
        k=6
    )

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
    You are an expert document information extractor.

    Extract structured shipment data from the context below.

    Requirements:
    - Return ONLY valid JSON
    - If a field is missing, return null
    - Do NOT hallucinate values
    - Fix OCR issues (e.g., "U S D" → "USD")
    - Normalize values where possible

    JSON Schema:
    {{
        "shipment_id": string | null,
        "shipper": string | null,
        "consignee": string | null,
        "pickup_datetime": string | null,
        "delivery_datetime": string | null,
        "equipment_type": string | null,
        "mode": string | null,
        "rate": number | null,
        "currency": string | null,
        "weight": string | null,
        "carrier_name": string | null
    }}

    Context:
    {context}
    """

    response = llm.invoke(prompt)

    try:
        parsed = json.loads(response.content)
    except Exception:
        parsed = {
            "error": "Invalid JSON from LLM",
            "raw_output": response.content
        }

    return {"extracted": parsed}