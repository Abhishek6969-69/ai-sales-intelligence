from dotenv import load_dotenv
from tinyfish import TinyFish

load_dotenv()

client = TinyFish()


def research_company(company: str):
    query = (
        f"{company} company industry employees headquarters "
        f"founded technologies revenue"
    )

    search_response = client.search.query(
        query=query,
        location="IN",
        language="en"
    )

    search_results = search_response.results[:3]

    urls = [result.url for result in search_results]

    fetch_response = client.fetch.get_contents(
        urls=urls,
        format="markdown"
    )

    pages = []

    for page in fetch_response.results:
        pages.append({
            "title": page.title,
            "url": page.url,
            "content": page.text
        })

    return {
        "company": company,
        "pages": pages
    }