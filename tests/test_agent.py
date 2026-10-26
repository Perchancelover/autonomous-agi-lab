from __future__ import annotations

import pytest

from app.core.agent import AutonomousAgent
from app.core.memory import MemoryStore
from app.core.self_upgrade import SelfUpgradeManager
from app.core.tools import WebTool


class FakeWebTool(WebTool):
    async def search(self, query: str, max_results: int = 5):
        return [
            {"title": "Example Result", "url": "https://example.com", "snippet": "A test result about learning."}
        ]

    async def fetch(self, url: str) -> str:
        return "This is some fetched content relevant to the research question."


@pytest.mark.asyncio
async def test_agent_answer(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    agent = AutonomousAgent(
        memory_store=store,
        web_tool=FakeWebTool(),
        self_upgrade=SelfUpgradeManager(tmp_path),
    )

    result = await agent.answer("How should an agent learn from the web?")

    assert result["status"] == "ok"
    assert "User request" in result["answer"]
    assert "Web findings" in result["answer"]


@pytest.mark.asyncio
async def test_learning_cycle_generates_summary(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    agent = AutonomousAgent(
        memory_store=store,
        web_tool=FakeWebTool(),
        self_upgrade=SelfUpgradeManager(tmp_path),
    )

    result = await agent.run_learning_cycle("autonomous learning")

    assert "summary" in result
    assert "autonomous learning" in result["goal"]
