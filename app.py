import streamlit as st
import arxiv
import requests

# 🏷️ App Title
st.title("📚 Intelligent Research Assistant with GitHub Tracing")

# 📝 User input
topic = st.text_input("Enter a research topic (e.g., Vision Transformers, LLMs in Healthcare)")

# 🔐 Load GitHub Token
token = st.secrets["GITHUB_TOKEN"]


# 📚 Function to search arXiv
def search_arxiv_papers(topic, max_results=5):
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    return list(search.results())


# 🔗 Function to find GitHub repos that mention the paper
def search_github_repos(paper_title, token):
    query = f'"{paper_title}" in:readme'
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/search/repositories?q={query}&per_page=3"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        return []


# 🚀 If topic is entered, do everything
if topic:
    st.subheader("🔍 Top Relevant Research Papers")
    papers = search_arxiv_papers(topic)

    for paper in papers:
        st.markdown(f"### [{paper.title}]({paper.pdf_url})")
        st.write("📅 Published on:", paper.published.date())
        st.write("✍️ Authors:", ", ".join(author.name for author in paper.authors))
        st.write("📝 Abstract:", paper.summary[:400] + "...")

        # GitHub lookup
        st.markdown("#### 🔗 Related GitHub Projects")
        repos = search_github_repos(paper.title, token)
        if repos:
            for repo in repos:
                st.markdown(f"- [{repo['full_name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
        else:
            st.info("No GitHub projects found for this paper.")
        
        st.divider()
