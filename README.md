# Autonomous AGI Lab

This repository is a serious research scaffold for building an autonomous, self-improving learning system. It is intentionally honest: it does not claim to be a finished AGI. It is a foundation for a long-term project that can evolve toward agentic autonomy, memory, web research, self-reflection, and code evolution.

What this repo includes:

- FastAPI application for a browser interface
- Autonomous agent loop with memory
- Web search and fetch tools
- Reflection and self-improvement planning
- Local code patching framework for repository evolution
- Hostless.cloud-friendly deployment configuration
- Evaluation-ready project structure

Important note:

This is not a fake “AGI is done” project. It is a real engineering scaffold designed to be extended over time toward increasingly autonomous behavior. The system can learn from the web, store knowledge, reason over it, and propose self-directed improvements.

## Quick start

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. Open the app:
   ```text
   http://localhost:8000
   ```

## Hostless.cloud deployment

This app is designed to run as a normal Python web service with a `PORT` environment variable. In Hostless, use the default startup command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

The included `Dockerfile` also supports container-based deployment if needed.

## Project structure

```text
app/
  __init__.py
  config.py
  core/
    agent.py
    memory.py
    self_upgrade.py
    tools.py
  main.py
Dockerfile
README.md
requirements.txt
.env.example
```

## Architecture overview

- Memory: stores prior observations, messages, and web findings
- Web tools: searches the internet and fetches pages for research
- Agent loop: reads user intent, finds related memory, gathers external info, and forms a response
- Reflection: summarizes what was learned and suggests improvements
- Self-upgrade: can create or modify repository files in a controlled, reviewable way

## Development roadmap

This project is meant to evolve through real research and engineering effort. The next milestones are:

1. Better reasoning and planning loops
2. Persistent memory with priority and forgetting policies
3. More advanced web research and structured extraction
4. Autonomous task execution and evaluation
5. Self-directed code evolution with review checkpoints
6. Real-world benchmarking against objective tasks

## License

This project is intentionally open for experimentation and long-term research. Use it responsibly and in line with the laws and policies of your environment.
