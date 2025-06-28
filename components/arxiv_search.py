import arxiv

def arxiv_search(topic, max_results=5):
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []
    for result in search.results():
        papers.append({
            "title": result.title,
            "summary": result.summary,
            "url": result.entry_id,
            "published": result.published.strftime("%Y-%m-%d"),
            "authors": [author.name for author in result.authors]
        })

    return papers

