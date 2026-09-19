'''
we are keeping the arxiv service and have the nodes call
the service for main reasons:
1. easy implementation or replacement, you know, incase we ever 
decide to add scholar or replace arxive with some other paper service
2. keeping this cleaner
'''
import arxiv

def search_papers(query:str, max_results:int=5)->list[dict]:
    client = arxiv.Client(
        page_size=max_results,
        delay_seconds=3, #this so we dont end up hammering arxiv with requests
        num_retries=2 #incase first fails
    )
    search=arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance, #rather than choosing whats newest, it chooses whats most relevant.
    ) 
    papers = []
    for result in client.results(search):
        paper ={
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "published": result.published.isoformat(),
            "arxiv_id": result.get_short_id(),
            "pdf_url": result.pdf_url,
        }
        papers.append(paper)
    return papers

def get_paper(arxiv_id:str)->dict:
    client= arxiv.Client(
        page_size=1,
        delay_seconds=3,
        num_retries=2,
    )
    search=arxiv.Search(
        id_list=[arxiv_id],
    )
    results=list(client.results(search))
    if not results:
        raise ValueError(f"No paper found for arXiv ID: {arxiv_id}")
    result=results[0]
    return{
        "title": result.title,
        "authors": [author.name for author in result.authors],
        "abstract": result.summary,
        "published": result.published.isoformat(),
        "arxiv_id": result.get_short_id(),
        "pdf_url": result.pdf_url,
    }

# testing block
if __name__ == "__main__":
    results = search_papers("KV cache compression", 3)

    for i, paper in enumerate(results, start=1):
        print(f"\n--- Paper {i} ---")
        print(f"Title: {paper['title']}")
        print(f"arXiv ID: {paper['arxiv_id']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"PDF: {paper['pdf_url']}")