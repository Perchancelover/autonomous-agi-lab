from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str


class WebTool:
    """Simple search and fetch layer using public web endpoints."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        import httpx
        from bs4 import BeautifulSoup

        url = "https://duckduckgo.com/html/"
        params = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[dict[str, Any]] = []
        for item in soup.select(".result")[:max_results]:
            link = item.select_one("a.result-link")
            snippet = item.select_one("a.result-link + .result-snippet")
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
        return results

    async def fetch(self, url: str) -> str:
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        return text[:3000]
