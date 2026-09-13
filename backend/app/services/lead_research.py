from dotenv import load_dotenv
from tinyfish import TinyFish

load_dotenv()

client = TinyFish()


def research_lead(name: str, job_title: str, company: str):
    queries = [
        f'"{name}" "{company}" "{job_title}" LinkedIn',
        f'"{name}" "{company}" professional',
        f'"{name}" "{company}" experience responsibilities',
    ]

    pages = []

    for query in queries:
        search_response = client.search.query(
            query=query,
            location="IN",
            language="en"
        )

        search_results = search_response.results[:3]

        urls = [result.url for result in search_results]

        if not urls:
            continue

        fetch_response = client.fetch.get_contents(
            urls=urls,
            format="markdown"
        )

        for page in fetch_response.results:
            pages.append({
                "title": page.title,
                "url": page.url,
                "content": page.text
            })

        if len(pages) >= 5:
            break

    return {
        "name": name,
        "job_title": job_title,
        "company": company,
        "pages": pages[:5]
    }