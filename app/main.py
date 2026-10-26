from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.core.agent import AutonomousAgent
from app.core.memory import MemoryStore
from app.core.self_upgrade import SelfUpgradeManager
from app.core.tools import WebTool


memory_store = MemoryStore(settings.memory_path)
web_tool = WebTool()
self_upgrade = SelfUpgradeManager(settings.repo_root)
agent = AutonomousAgent(memory_store=memory_store, web_tool=web_tool, self_upgrade=self_upgrade)

app = FastAPI(title=settings.app_name)


class ChatMessage(BaseModel):
    message: str


class LearningRequest(BaseModel):
    goal: str


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "memory_count": memory_store.count(),
    }


@app.get("/api/agent/status")
async def agent_status() -> dict:
    return {
        "app": settings.app_name,
        "memory_count": memory_store.count(),
        "repo_root": str(Path(settings.repo_root).resolve()),
    }


@app.post("/api/chat")
async def chat(payload: ChatMessage) -> dict:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return await agent.answer(payload.message)


@app.post("/api/agent/learn")
async def learn(payload: LearningRequest) -> dict:
    if not payload.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")
    return await agent.run_learning_cycle(payload.goal)


@app.post("/api/agent/self-upgrade")
async def self_upgrade_endpoint(payload: dict) -> dict:
    motivation = payload.get("motivation", "self-improvement")
    rel_path = payload.get("path", "README.md")
    return await agent.propose_self_upgrade(motivation, rel_path)


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """
    <html>
      <head>
        <title>Autonomous AGI Lab</title>
        <style>
          body { font-family: Arial, sans-serif; background: #0b1020; color: #eef2ff; margin: 0; padding: 2rem; }
          .container { max-width: 980px; margin: 0 auto; }
          .card { background: #131a2e; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
          textarea, input, button { width: 100%; box-sizing: border-box; padding: 12px; border-radius: 8px; border: 1px solid #2d3a5d; margin-top: 12px; }
          textarea { min-height: 110px; background: #0d1326; color: white; }
          button { background: #6d8cff; color: white; border: none; font-weight: bold; cursor: pointer; }
          .response { white-space: pre-wrap; margin-top: 1rem; background: #10192d; border-radius: 8px; padding: 1rem; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="card">
            <h1>Autonomous AGI Lab</h1>
            <p>This interface is a test harness for an autonomous learning agent research scaffold.</p>
            <textarea id="message" placeholder="Ask the agent to reason, research, or plan..."></textarea>
            <button onclick="sendMessage()">Send</button>
            <button onclick="runLearningCycle()">Run learning cycle</button>
            <div id="response" class="response">Awaiting input...</div>
          </div>
        </div>
        <script>
          async function sendMessage() {
            const message = document.getElementById('message').value;
            const response = document.getElementById('response');
            response.textContent = 'Thinking...';
            const res = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message })
            });
            const data = await res.json();
            response.textContent = JSON.stringify(data, null, 2);
          }

          async function runLearningCycle() {
            const goal = document.getElementById('message').value || 'autonomous learning';
            const response = document.getElementById('response');
            response.textContent = 'Running research cycle...';
            const res = await fetch('/api/agent/learn', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ goal })
            });
            const data = await res.json();
            response.textContent = JSON.stringify(data, null, 2);
          }
        </script>
      </body>
    </html>
    """
