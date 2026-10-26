from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str


class WebTool:
    """Search and fetch layer with graceful fallbacks for blocked or redirected endpoints."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        import httpx
        from bs4 import BeautifulSoup

        if not query or not query.strip():
            return []

        endpoints = [
            ("https://api.duckduckgo.com/", {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}),
            ("https://lite.duckduckgo.com/lite/", {"q": query}),
            ("https://html.duckduckgo.com/html/", {"q": query}),
        ]

        for url, params in endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
                    response.raise_for_status()

                if url.startswith("https://api.duckduckgo.com/"):
                    data = response.json()
                    results: list[dict[str, Any]] = []
                    if data.get("AbstractText"):
                        results.append({
                            "title": data.get("Heading") or query,
                            "url": data.get("AbstractURL") or "https://duckduckgo.com/",
                            "snippet": data.get("AbstractText")[:500],
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })
                    for topic in data.get("RelatedTopics", [])[:max_results]:
                        if isinstance(topic, dict):
                            title = topic.get("Text", query).split(" - ")[0][:120]
                            url_value = topic.get("FirstURL") or "https://duckduckgo.com/"
                            snippet = topic.get("Text", "")[:500]
                            results.append({
                                "title": title,
                                "url": url_value,
                                "snippet": snippet,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            })
                    if results:
                        return results[:max_results]

                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                for item in soup.select(".result")[:max_results]:
                    link = item.select_one("a.result-link")
                    snippet = item.select_one(".result-snippet")
                    if not link:
                        continue
                    title = link.get_text(" ", strip=True)
                    href = link.get("href")
                    snippet_text = snippet.get_text(" ", strip=True) if snippet else ""
                    if href:
                        results.append({
                            "title": title,
                            "url": href,
                            "snippet": snippet_text,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })
                if results:
                    return results
            except Exception:
                continue

        return [{
            "title": "Web search unavailable",
            "url": "https://duckduckgo.com/",
            "snippet": "Search is unavailable; fallback mode activated.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]

    async def fetch(self, url: str) -> str:
        import httpx
        from bs4 import BeautifulSoup

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(" ", strip=True)
            return text[:3000]
        except Exception:
            return "Content unavailable; fetch was blocked or redirected."
