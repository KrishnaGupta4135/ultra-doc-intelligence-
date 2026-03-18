from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

VECTOR_PATH = "vector_store"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

def clean_llm_json(output: str) -> str:
    output = re.sub(r"```json", "", output, flags=re.IGNORECASE)
    output = re.sub(r"```", "", output)
    return output.strip()

def extract_data(doc_id):
    db = FAISS.load_local(
        f"{VECTOR_PATH}/{doc_id}",
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(
        "shipment details customer consignee pickup delivery rate weight carrier equipment",
        k=6
    )

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are an expert document information extraction system.

Return only valid raw JSON.
Do not include markdown, code blocks, or explanations.
Output must be directly parseable using json.loads().

If a field is missing return null.
Do not guess values.
Handle OCR issues such as broken words and spacing.
Normalize values when possible.

JSON schema:
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
    cleaned = clean_llm_json(response.content)

    try:
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {
            "error": "Invalid JSON from LLM",
            "raw_output": response.content
        }

    return {"extracted": parsed}