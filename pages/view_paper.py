import streamlit as st
import requests
import tempfile
import os
from dotenv import load_dotenv

from components.github_search import search_github_repos
from pages.components.pdf_qa_engine import PDFQAEngine

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Load .env and check GROQ_API_KEY
load_dotenv()
api_key_env = os.getenv("GROQ_API_KEY")
if not api_key_env:
    st.error("GROQ_API_KEY not found in .env file.")
    st.stop()

# Get selected paper
selected_index = st.session_state.get("selected_index")
papers = st.session_state.get("papers", [])

if selected_index is None or not papers:
    st.error("No paper selected. Please go back to the main page.")
    st.stop()

# Reset state if a new paper is selected
if "last_selected_index" not in st.session_state or st.session_state["last_selected_index"] != selected_index:
    st.session_state.pop("pdf_processed", None)
    st.session_state.pop("qa_engine", None)
    st.session_state.pop("summary_text", None)
    st.session_state["last_selected_index"] = selected_index

paper = papers[selected_index]

# Back Button
if st.button("⬅️ Back to Results"):
    st.switch_page("app.py")

# Paper Details
st.title(paper["title"])
st.write("📅 Published on:", paper["published"])
st.write("✍️ Authors:", ", ".join(paper["authors"]))
st.markdown(f'🔗 [View on arXiv]({paper["url"]})')

# GitHub lookup
st.subheader("🔗 Related GitHub Projects")
repos = search_github_repos(paper["title"], st.secrets["GITHUB_TOKEN"])
if repos:
    for repo in repos:
        st.markdown(f"- [{repo['full_name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
else:
    st.info("No GitHub projects found for this paper.")

@st.cache_resource(show_spinner=False)
def load_pdf_qa_engine(pdf_bytes: bytes) -> PDFQAEngine:
    return PDFQAEngine.from_pdf(pdf_bytes)

if "pdf_processed" not in st.session_state:
    with st.spinner("Downloading and processing PDF..."):
        # Infer PDF URL from arXiv ID
        try:
            arxiv_id = paper["url"].split("/")[-1]
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            response = requests.get(pdf_url)

            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name

                with open(tmp_file_path, "rb") as f:
                    pdf_bytes = f.read()

                try:
                    qa_engine = load_pdf_qa_engine(pdf_bytes)
                    st.session_state["qa_engine"] = qa_engine
                    st.session_state["summary_text"] = qa_engine.summary_text
                    st.session_state["pdf_processed"] = True
                except Exception as e:
                    st.error(f"Failed to process PDF: {e}")
                    st.stop()

                os.remove(tmp_file_path)
            else:
                st.error("Failed to download the PDF.")
                st.stop()

        except Exception as e:
            st.error(f"Error extracting PDF URL: {e}")
            st.stop()

# Summary Section
st.write("📄 **Summary:**")
st.write(st.session_state.get("summary_text", "No summary available."))

# Question Answering Section
# 🧠 PDF-based QA
st.subheader("💬 Ask Questions About This Paper")
query = st.text_input("Ask")


if query:
    with st.spinner("Answering..."):
        try:
            qa_engine = st.session_state.get("qa_engine")
            if qa_engine:
                answer = qa_engine.answer_question(query)
                st.success("Answer:")
                st.write(answer)
            else:
                st.warning("PDF not yet processed. Please refresh.")
        except Exception as e:
            st.error(f"Failed to answer the question: {e}")

