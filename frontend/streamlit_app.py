import streamlit as st
import requests
from dotenv import load_dotenv
import os
load_dotenv()

# ---------------- CONFIG ----------------
API_BASE = os.getenv("API_BASE")

st.set_page_config(page_title="Ultra Doc AI", layout="wide")

st.title("Ultra Doc Intelligence")
st.caption("Chat with your logistics document")

# ---------------- SESSION STATE ----------------
if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Upload Document")

    uploaded_file = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file is not None:
        if st.button("Upload"):
            with st.spinner("Processing document..."):
                response = requests.post(
                    f"{API_BASE}/upload",
                    files={"file": uploaded_file}
                )

                if response.status_code == 200:
                    st.session_state.document_id = response.json()["document_id"]
                    st.success("Document uploaded!")
                    st.session_state.messages = []
                else:
                    st.error("Upload failed")

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []

    st.divider()

    if st.button("Extract Data"):
        if not st.session_state.document_id:
            st.warning("Upload document first")
        else:
            with st.spinner("Extracting..."):
                res = requests.post(
                    f"{API_BASE}/extract",
                    json={"document_id": st.session_state.document_id}
                )
                if res.status_code == 200:
                    st.json(res.json())
                else:
                    st.error("Extraction failed")

# ---------------- CHAT UI ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and "meta" in msg:
            with st.expander("Details"):
                st.write("**Confidence:**", msg["meta"]["confidence"])

                st.write("**Sources:**")
                for i, src in enumerate(msg["meta"]["sources"]):
                    st.markdown(f"**Source {i+1}:**")
                    st.write(src)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask about your document...")

if prompt:
    if not st.session_state.document_id:
        st.warning("Please upload a document first")
    else:
        # User message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_BASE}/ask",
                    json={
                        "document_id": st.session_state.document_id,
                        "question": prompt
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    answer = data["answer"]
                    confidence = data["confidence"]
                    sources = data["sources"]

                    st.markdown(answer)

                    # Save message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "meta": {
                            "confidence": confidence,
                            "sources": sources
                        }
                    })

                    # Show meta
                    with st.expander("Details"):
                        st.write("**Confidence:**", confidence)

                        st.write("**Sources:**")
                        for i, src in enumerate(sources):
                            st.markdown(f"**Source {i+1}:**")
                            st.write(src)

                else:
                    st.error("Failed to get response")