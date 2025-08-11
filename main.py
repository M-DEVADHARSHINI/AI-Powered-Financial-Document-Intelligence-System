import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# =============== CONFIG ===============
GROQ_API_KEY = "YOUR_GROQ_API_KEY"  # <-- Put your Groq API key here
MODEL_NAME = "llama3-70b-8192"

client = Groq(api_key=GROQ_API_KEY)

# =============== FUNCTIONS ===============

def extract_text_from_url(url):
    """Fetch and clean main text from a news article URL."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())
    except Exception as e:
        return f"[Error fetching article: {e}]"

def ask_groq(question, context):
    """Send context + question to Groq API and return answer."""
    try:
        chat_completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers based on provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            temperature=0
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error from Groq API: {e}]"

# =============== STREAMLIT UI ===============

st.set_page_config(page_title="News AI Q&A", layout="wide")
st.title("📰 AI-Powered News Q&A (Groq)")

col1, col2 = st.columns(2)

# --- Left Column: URL Input ---
with col1:
    st.subheader("📎 News Article URLs")
    urls = st.text_area("Enter one or more article URLs (one per line):", height=200)
    process_btn = st.button("Fetch Articles")

# --- Right Column: Question & Answer ---
with col2:
    st.subheader("❓ Ask a Question")
    question = st.text_input("Enter your question about the articles:")
    answer = ""
    sources = []

if process_btn and urls.strip():
    article_texts = []
    sources = []
    for url in urls.strip().split("\n"):
        url = url.strip()
        if url:
            text = extract_text_from_url(url)
            if text:
                article_texts.append(text)
                sources.append(url)

    if article_texts and question.strip():
        combined_context = "\n\n".join(article_texts)
        answer = ask_groq(question, combined_context)

        # Display answer & sources
        with col2:
            st.markdown("### 🧠 Answer")
            st.write(answer)
            st.markdown("### 📚 Sources")
            for s in sources:
                st.markdown(f"- [{s}]({s})")

elif process_btn:
    st.warning("Please enter at least one article URL.")

