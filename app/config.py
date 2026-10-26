import os
from dataclasses import dataclass
from pathlib import Path


def _default_writable_path(env_name: str, relative_path: str) -> str:
    value = os.getenv(env_name)
    if value:
        return value

    base = Path("/tmp/autonomous-agi-lab")
    base.mkdir(parents=True, exist_ok=True)
    target = base / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    return str(target)


@dataclass
class AppConfig:
    app_name: str = os.getenv("APP_NAME", "Autonomous AGI Lab")
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    repo_root: str = os.getenv("REPO_ROOT", _default_writable_path("REPO_ROOT", "repo"))
    memory_path: str = os.getenv("MEMORY_PATH", _default_writable_path("MEMORY_PATH", "memory/memory.json"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = AppConfig()
