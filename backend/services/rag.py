from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from backend.services.guardrails import apply_guardrails
from dotenv import load_dotenv
import os

load_dotenv()

VECTOR_PATH = "vector_store"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()


def rewrite_query(question: str) -> str:
    prompt = f"""
    Convert the user question into a clear search query for document retrieval.

    Question: {question}

    Output only the improved query.
    """
    return llm.invoke(prompt).content.strip()


def answer_question(doc_id, question):
    db = FAISS.load_local(
        f"{VECTOR_PATH}/{doc_id}",
        embeddings,
        allow_dangerous_deserialization=True
    )
    improved_query = rewrite_query(question)
    docs = db.similarity_search_with_score(improved_query, k=6)

    if not docs:
        return {
            "answer": "Not found in document",
            "sources": [],
            "confidence": 0.0
        }
    docs = sorted(docs, key=lambda x: x[1])[:3]
    contexts = [d[0].page_content for d in docs]
    scores = [float(d[1]) for d in docs]

    best_score = min(scores)
    guard = apply_guardrails(best_score)
    if guard:
        return guard

    context_text = "\n\n".join(contexts)

    prompt = f"""
    You are a strict document QA system.

    Instructions:
    - Answer ONLY using the provided context
    - Do NOT guess
    - If answer is missing → say: "Not found in document"
    - Keep answer concise and factual
    - Prefer exact values from context

    Context:
    {context_text}

    Question:
    {question}
    """

    response = llm.invoke(prompt)
    answer = response.content.strip()
    similarity_score = 1 / (1 + best_score)
    keyword_hits = sum(
        1 for c in contexts if any(word.lower() in c.lower() for word in answer.split()[:3])
    )
    agreement_score = keyword_hits / len(contexts)
    coverage_score = min(len(answer) / 200, 1)
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