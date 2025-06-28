import streamlit as st
import os
from components.arxiv_search import arxiv_search  # Unified function
from dotenv import load_dotenv

st.set_page_config(page_title="Intelligent Research Assistant", layout="wide", initial_sidebar_state="collapsed")
st.title("📚 PaperPilot – An intelligent Research Assistant with GitHub Tracing")

# Load environment variables

# User input
topic = st.text_input("Enter a research topic (e.g., Vision Transformers, LLMs in Healthcare)")
token = st.secrets["GITHUB_TOKEN"]

# Run search and cache results
if topic:
    if "papers" not in st.session_state or st.session_state.get("topic") != topic:
        with st.spinner("Fetching and analyzing papers..."):


            papers = arxiv_search(topic, max_results=5)
            st.session_state["papers"] = papers
            st.session_state["topic"] = topic
    else:
        papers = st.session_state["papers"]

    st.subheader("🔍 Top Relevant Research Papers")

    for i, paper in enumerate(papers):
        if st.button(paper["title"], key=f"paper_btn_{i}"):
            st.session_state["selected_index"] = i
            st.switch_page("pages/view_paper.py")

        st.write("📅 Published on:", paper["published"])
        st.write("✍️ Authors:", ", ".join(paper["authors"]))
        st.write(f"🔗 [View on arXiv]({paper['url']})")

        with st.expander("📝 Abstract"):
            st.write(paper["summary"][:2000])

        # Optional: if fact_check or similarity available
        if "fact_check" in paper:
            with st.expander("🔍 LLM Fact-Check Summary"):
                st.write(paper["fact_check"])
        if "similarity" in paper:
            st.write(f"🧠 Relevance Score: {paper['similarity']:.2f}")

        st.divider()

