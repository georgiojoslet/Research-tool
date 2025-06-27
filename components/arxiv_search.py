import arxiv
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the sentence embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# LLM fact-checking using Ollama (Llama 3)
def local_llm_fact_check(topic, abstract):
    prompt = f"""
The user is researching: "{topic}"

Below is the abstract of a paper:
\"\"\"
{abstract}
\"\"\"

Summarize any scientific claims or methods, and briefly assess if they seem plausible or need verification. Limit to 2–3 sentences.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma:2b", "prompt": prompt, "temperature": 0.4, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            return data["response"].strip()
        else:
            return "⚠️ LLM returned an invalid response format."
    except Exception as e:
        return f"⚠️ Fact-check failed: {e}"

# Search arXiv with similarity scoring and LLM-based fact-checking
def search_arxiv_papers(topic, max_results=5):
    search = arxiv.Search(
        query=topic,
        max_results=max_results * 2,
        sort_by=arxiv.SortCriterion.Relevance
    )

    topic_embedding = model.encode([topic])[0]
    results = []
    seen_titles = set()

    for paper in search.results():
        if paper.title in seen_titles:
            continue
        seen_titles.add(paper.title)

        combined_text = f"{paper.title} {paper.summary}"
        paper_embedding = model.encode([combined_text])[0]
        similarity = cosine_similarity([topic_embedding], [paper_embedding])[0][0]

        if similarity >= 0.2:
            paper.similarity = similarity
            paper.fact_check = local_llm_fact_check(topic, paper.summary)
            results.append(paper)

        if len(results) >= max_results:
            break

    return sorted(results, key=lambda p: p.similarity, reverse=True)
