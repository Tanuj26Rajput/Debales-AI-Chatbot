import os

from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper

load_dotenv()

search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))

def search_google(query):
    if not os.getenv("SERPAPI_API_KEY"):
        return "SERPAPI_API_KEY is not configured."

    results = []
    data = search.results(query)

    if data.get("error"):
        return f"SERP API error: {data['error']}"

    # Organic snippets are enough context for the final answer in this small demo.
    for result in data.get("organic_results", [])[:3]:
        title = result.get("title", "").strip()
        snippet = result.get("snippet", "").strip()
        link = result.get("link", "").strip()

        if snippet:
            results.append(f"{title}\n{snippet}\nSource: {link}".strip())

    if not results:
        answer_box = data.get("answer_box", {})
        answer = answer_box.get("answer") or answer_box.get("snippet")
        if answer:
            return answer

    return "\n\n".join(results) if results else "No relevant search results found."


search_tool = search_google
