import json
from pathlib import Path
from typing import Any, List
from datetime import datetime, timezone


class MemoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        return []

    def _write(self, entries: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, source: str, category: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        entry = {
            "id": len(self._read()) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "category": category,
            "content": content,
            "tags": tags or [],
        }
        entries = self._read()
        entries.append(entry)
        self._write(entries)
        return entry

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        q = query.lower()
        matches: list[dict[str, Any]] = []
        for entry in reversed(self._read()):
            haystack = " ".join([
                entry.get("source", ""),
                entry.get("category", ""),
                entry.get("content", ""),
                *[tag for tag in entry.get("tags", [])],
            ]).lower()
            if q in haystack:
                matches.append(entry)
            if len(matches) >= limit:
                break
        return matches

    def list_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        entries = self._read()
        return list(reversed(entries))[:limit]

    def count(self) -> int:
        return len(self._read())
