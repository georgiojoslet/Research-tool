import streamlit as st
import streamlit.components.v1 as components
from components.github_search import search_github_repos
from pages.components.pdf_preview import show_pdf_preview

st.set_page_config(initial_sidebar_state="collapsed")

# 🔙 Back Button
if st.button("← Back to search"):
    st.switch_page("app.py")

st.title("📄 Paper Summary")

# 🚨 Check for selection
if "papers" in st.session_state and "selected_index" in st.session_state:
    i = st.session_state["selected_index"]
    paper = st.session_state["papers"][i]
    token = st.secrets["GITHUB_TOKEN"]

    st.markdown(f"## {paper.title}")
    st.write("📅 Published:", paper.published.date())
    st.write("✍️ Authors:", ", ".join(author.name for author in paper.authors))

    # Open in New Tab
    st.markdown(f'<a href="{paper.pdf_url}" target="_blank">🧾 Open PDF in new tab</a>', unsafe_allow_html=True)

    # 📑 PDF Preview
    st.markdown("### 📖 PDF Preview")
    show_pdf_preview(paper.pdf_url)

    # 🔗 GitHub Repositories
    st.markdown("### 🔗 Related GitHub Projects")
    with st.spinner("🔍 Searching GitHub..."):
        repos = search_github_repos(paper.title, token)

    if repos:
        for repo in repos:
            st.markdown(f"- [{repo['full_name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
    else:
        st.info("No GitHub projects found for this paper.")
else:
    st.warning("Please return to the main page and select a paper.")
