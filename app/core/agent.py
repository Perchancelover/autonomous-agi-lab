from __future__ import annotations

from typing import Any

from app.core.self_upgrade import SelfUpgradeManager


class AutonomousAgent:
    def __init__(self, memory_store, web_tool, self_upgrade: SelfUpgradeManager):
        self.memory_store = memory_store
        self.web_tool = web_tool
        self.self_upgrade = self_upgrade

    async def answer(self, user_message: str) -> dict[str, Any]:
        memory_hits = self.memory_store.search(user_message, limit=5)

        external_findings = []
        if user_message.strip():
            web_results = await self.web_tool.search(user_message, max_results=3)
            for result in web_results:
                try:
                    page_text = await self.web_tool.fetch(result["url"])
                except Exception:
                    page_text = result["snippet"]
                external_findings.append({
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": page_text[:500],
                })

        answer = self._compose_answer(user_message, memory_hits, external_findings)
        self.memory_store.add(
            source="user",
            category="conversation",
            content=f"User: {user_message}\nAgent: {answer}",
            tags=["conversation", "response"],
        )

        return {
            "answer": answer,
            "memory_hits": len(memory_hits),
            "external_findings": len(external_findings),
            "status": "ok",
        }

    async def run_learning_cycle(self, goal: str) -> dict[str, Any]:
        search_results = await self.web_tool.search(goal, max_results=5)
        findings = []
        for result in search_results:
            try:
                text = await self.web_tool.fetch(result["url"])
            except Exception:
                text = result["snippet"]
            findings.append({
                "title": result["title"],
                "url": result["url"],
                "summary": text[:800],
            })

        summary = self._summarize_findings(goal, findings)
        self.memory_store.add(
            source="learning_cycle",
            category="research",
            content=f"Goal: {goal}\nSummary: {summary}",
            tags=["learning", "research", "goal"],
        )
        return {
            "goal": goal,
            "summary": summary,
            "findings": findings,
        }

    async def propose_self_upgrade(self, motivation: str, rel_path: str = "README.md") -> dict[str, Any]:
        improvement = (
            f"# Self-generated improvement note\n"
            f"Motivation: {motivation}\n"
            f"This file was updated by the autonomous learning loop to capture the next research direction."
        )
        patch_result = self.self_upgrade.write_or_patch(
            rel_path,
            improvement,
            reason=f"autonomous learning update: {motivation}",
        )
        self.memory_store.add(
            source="self_upgrade",
            category="meta",
            content=f"Motivation: {motivation}\nPatch applied: {rel_path}",
            tags=["self-improvement", "meta"],
        )
        return patch_result

    def _summarize_findings(self, goal: str, findings: list[dict[str, Any]]) -> str:
        if not findings:
            return f"No external findings were collected for the goal '{goal}'."
        chunks = [f"For '{goal}', the agent found:"]
        for item in findings[:3]:
            chunks.append(f"- {item['title']}: {item['summary'][:220]}")
        return "\n".join(chunks)

    def _compose_answer(self, user_message: str, memory_hits: list[dict[str, Any]], external_findings: list[dict[str, Any]]) -> str:
        memory_block = "\n".join(
            f"- {entry['content'][:220]}" for entry in memory_hits[:3]
        ) if memory_hits else "- No relevant memory found."

        web_block = "\n".join(
            f"- {item['title']}: {item['snippet'][:220]}" for item in external_findings[:3]
        ) if external_findings else "- No external research was needed."

        return (
            f"I am a learning agent scaffold.\n\n"
            f"User request: {user_message}\n\n"
            f"Relevant memory:\n{memory_block}\n\n"
            f"Web findings:\n{web_block}\n\n"
            f"Next step: continue research, improve the memory system, and add stronger planning, evaluation, and self-modifying code loops."
        )
