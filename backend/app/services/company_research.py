from dotenv import load_dotenv
from tinyfish import TinyFish

load_dotenv()

client = TinyFish()


def research_company(company: str) -> dict:
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

    return {"company": company, "pages": pages}


def research_company_signals(company: str) -> dict:
    """
    Research active buying signals: funding, hiring, expansion, etc.
    """
    queries = [
        f"{company} funding raised investment 2024 2025",
        f"{company} hiring engineers expansion growth",
        f"{company} new product launch acquisition partnership",
    ]

    pages = []

    for query in queries:
        try:
            search_response = client.search.query(
                query=query,
                location="IN",
                language="en"
            )

            search_results = search_response.results[:2]
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
                    "content": page.text[:1500]
                })

            if len(pages) >= 4:
                break

        except Exception:
            continue

    return {"company": company, "pages": pages[:4]}


def research_company_competitor(company: str, product_category: str = "cloud observability") -> dict:
    """
    Research what tools/vendors the company currently uses.
    """
    queries = [
        f"{company} technology stack tools software",
        f"{company} uses {product_category} monitoring observability",
    ]

    pages = []

    for query in queries:
        try:
            search_response = client.search.query(
                query=query,
                location="IN",
                language="en"
            )

            search_results = search_response.results[:2]
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
                    "content": page.text[:1500]
                })

            if len(pages) >= 3:
                break

        except Exception:
            continue

    return {"company": company, "pages": pages[:3]}