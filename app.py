import streamlit as st
from components.arxiv_search import search_arxiv_papers

st.set_page_config(page_title="Intelligent Research Assistant", layout="wide")
st.title("📚 Intelligent Research Assistant with GitHub Tracing")

# User input
topic = st.text_input("Enter a research topic (e.g., Vision Transformers, LLMs in Healthcare)")
token = st.secrets["GITHUB_TOKEN"]

# Run search and cache results
if topic:
    if "papers" not in st.session_state or st.session_state.get("topic") != topic:
        with st.spinner("Fetching and analyzing papers..."):
            papers = search_arxiv_papers(topic, max_results=5)
            st.session_state["papers"] = papers
            st.session_state["topic"] = topic
    else:
        papers = st.session_state["papers"]

    st.subheader("🔍 Top Relevant Research Papers")

    for i, paper in enumerate(papers):
        if st.button(paper.title, key=f"paper_btn_{i}"):
            st.session_state["selected_index"] = i
            st.switch_page("pages/view_paper.py")

        st.write("📅 Published on:", paper.published.date())
        st.write("✍️ Authors:", ", ".join(author.name for author in paper.authors))
        st.write(f"🧠 Relevance Score: `{paper.similarity:.2f}`")

        with st.expander("📝 Abstract"):
            st.write(paper.summary[:2000])

        with st.expander("🔍 LLM Fact-Check Summary"):
            st.write(paper.fact_check)

        st.divider()
