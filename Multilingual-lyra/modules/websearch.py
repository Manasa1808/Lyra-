import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def search_and_summarise(user_text: str, n_results: int = 3) -> str:
    t = user_text.lower()
    q = re.sub(r"^(search|look up|google|web search)\s*", "", t, flags=re.I).strip()
    if not q:
        q = user_text.strip()

    url = "https://html.duckduckgo.com/html/"
    try:
        r = requests.post(url, data={"q": q}, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("a.result__a")
        snippets = soup.select(".result__snippet")
        results = []
        for i in range(min(n_results, len(items))):
            title = items[i].get_text(" ", strip=True)
            snip = snippets[i].get_text(" ", strip=True) if i < len(snippets) else ""
            results.append({"title": title, "snippet": snip})

        if not results:
            return f"I couldn’t find much on “{q}” right now."

        bullets = "\n".join([f"• {r['title']}: {r['snippet']}" if r["snippet"] else f"• {r['title']}" for r in results])
        return f"Here’s what I found about “{q}”: \n{bullets}"
    except Exception:
        return "Search is having trouble right now."