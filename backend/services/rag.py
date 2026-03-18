from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from backend.services.guardrails import apply_guardrails
from backend.services.ingestion import clean_text
from rank_bm25 import BM25Okapi
import os
from dotenv import load_dotenv

load_dotenv()

VECTOR_PATH = "vector_store"

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY")
)

def keyword_search(chunks, query, top_k=5):
    tokenized_chunks = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)

    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in ranked[:top_k]]


def rewrite_query(query):
    return f"Find the exact value for: {query}"

def answer_question(doc_id, question):

    db = FAISS.load_local(
        f"{VECTOR_PATH}/{doc_id}",
        embeddings,
        allow_dangerous_deserialization=True
    )

    improved_query = rewrite_query(question)

    docs = db.similarity_search_with_score(improved_query, k=6)
    vector_chunks = [clean_text(d[0].page_content) for d in docs]
    scores = [float(d[1]) for d in docs]

    all_docs = db.similarity_search("", k=20)
    all_chunks = [clean_text(d.page_content) for d in all_docs]

    keyword_chunks = keyword_search(all_chunks, question, top_k=5)

    contexts = list(set(vector_chunks + keyword_chunks))

    if not contexts:
        return {
            "answer": "Not found in document",
            "sources": [],
            "confidence": 0.0
        }

    best_score = min(scores) if scores else 999
    guard = apply_guardrails(best_score)
    if guard:
        return guard

    context_text = "\n\n".join(contexts)

    prompt = f"""
            You are a highly accurate document intelligence system designed for extracting factual information from unstructured and OCR-processed documents.

            ### OBJECTIVE
            Extract the exact answer to the user’s question strictly from the provided context.

            ### DOCUMENT CHARACTERISTICS
            - The document may contain OCR noise (e.g., broken words, irregular spacing, formatting issues).
            - Field labels and values may not be perfectly aligned.
            - Information may appear multiple times or in different formats.

            ### INSTRUCTIONS
            - Identify relevant sections using both semantic meaning and keyword proximity.
            - Accurately map field labels to their corresponding values.
            - Be robust to formatting inconsistencies and partial text corruption.
            - Prefer the most complete and relevant value if multiple candidates exist.
            - Do NOT infer or assume information that is not present in the context.

            ### STRICT RULES
            - Return ONLY the final extracted answer.
            - Do NOT include explanations, reasoning, or additional text.
            - If the answer is not present in the context, return exactly:
            "Not found in document"

            ### CONTEXT
            {context_text}

            ### QUESTION
            {question}
            """

    response = llm.invoke(prompt)
    answer = response.content.strip()
    similarity_score = 1 / (1 + best_score)

    keyword_hits = sum(
        1 for c in contexts
        if any(word.lower() in c.lower() for word in answer.split()[:3])
    )

    agreement_score = keyword_hits / len(contexts) if contexts else 0
    coverage_score = min(len(answer) / 100, 1)

    confidence = round(
        (0.5 * similarity_score) +
        (0.3 * agreement_score) +
        (0.2 * coverage_score),
        2
    )

    if confidence < 0.4:
        return {
            "answer": "Not found in document",
            "sources": [],
            "confidence": confidence
        }

    return {
        "answer": answer,
        "sources": contexts,
        "confidence": confidence
    }