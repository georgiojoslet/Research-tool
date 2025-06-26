import streamlit as st
from components.arxiv_search import search_arxiv_papers
from components.github_search import search_github_repos

st.set_page_config(page_title="Intelligent Research Assistant", layout="wide")
st.title("📚 Intelligent Research Assistant with GitHub Tracing")

# 🔍 Topic Input
topic = st.text_input("Enter a research topic (e.g., Vision Transformers, LLMs in Healthcare)")
token = st.secrets["GITHUB_TOKEN"]

# 🔍 Fetch and display papers
if topic:
    with st.spinner("Fetching relevant research papers..."):
        papers = search_arxiv_papers(topic, max_results=3)
        st.session_state["papers"] = papers  # Save for view_paper

    st.subheader("🔍 Top Relevant Research Papers")

    for i, paper in enumerate(papers):
        if st.button(paper.title, key=f"paper_btn_{i}"):
            st.session_state["selected_index"] = i
            st.switch_page("pages/view_paper.py")

        st.write("📅 Published on:", paper.published.date())
        st.write("✍️ Authors:", ", ".join(author.name for author in paper.authors))

        with st.expander("📝 Abstract"):
            st.write(paper.summary[:2000])

        st.divider()
