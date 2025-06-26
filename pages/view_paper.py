import streamlit as st
import requests
import tempfile
import os

from components.github_search import search_github_repos
from pages.components.pdf_qa_engine import PDFQAEngine

qa_engine = PDFQAEngine()
st.set_page_config(page_title="View Paper", layout="wide")

# Get selected paper
selected_index = st.session_state.get("selected_index")
papers = st.session_state.get("papers", [])

if selected_index is None or not papers:
    st.error("No paper selected. Please go back to the main page.")
    st.stop()

paper = papers[selected_index]

# Back Button
if st.button("⬅️ Back to Results"):
    st.switch_page("app.py")

# Paper Details
st.title(paper.title)
st.write("📅 Published on:", paper.published.date())
st.write("✍️ Authors:", ", ".join(author.name for author in paper.authors))
st.markdown(f'<a href="{paper.pdf_url}" target="_blank">📄 Open Full Paper (PDF)</a>', unsafe_allow_html=True)

# GitHub lookup
st.subheader("🔗 Related GitHub Projects")
repos = search_github_repos(paper.title, st.secrets["GITHUB_TOKEN"])
if repos:
    for repo in repos:
        st.markdown(f"- [{repo['full_name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
else:
    st.info("No GitHub projects found for this paper.")

# 🧠 PDF-based QA
st.subheader("💬 Ask Questions About This Paper")

if "pdf_processed" not in st.session_state:
    with st.spinner("Downloading and processing PDF..."):
        response = requests.get(paper.pdf_url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            with open(tmp_file_path, "rb") as f:
                pdf_bytes = f.read()
                summary = qa_engine.process_pdf(pdf_bytes)

            st.session_state["pdf_processed"] = True
            st.session_state["summary_text"] = summary

            # Cleanup (optional: set delete=True above to auto delete)
            os.remove(tmp_file_path)
        else:
            st.error("Failed to download the PDF.")
            st.stop()

st.write("📄 **Summary:**")
st.write(st.session_state["summary_text"])

query = st.text_input("Ask a question about this paper")

if query:
    with st.spinner("Answering..."):
        answer = qa_engine.answer_question(query)
        st.success("Answer:")
        st.write(answer)
