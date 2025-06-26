import streamlit as st
from pages.components.pdf_preview import show_pdf_preview
from components.github_search import search_github_repos

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

# Preview PDF
# show_pdf_preview(paper.pdf_url)

# GitHub lookup
st.subheader("🔗 Related GitHub Projects")
repos = search_github_repos(paper.title, st.secrets["GITHUB_TOKEN"])
if repos:
    for repo in repos:
        st.markdown(f"- [{repo['full_name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
else:
    st.info("No GitHub projects found for this paper.")
