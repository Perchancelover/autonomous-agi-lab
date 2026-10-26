from __future__ import annotations

from pathlib import Path
from typing import Any


class SelfUpgradeManager:
    """Controlled repository self-improvement access."""

    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root)

    def backup_file(self, file_path: str | Path) -> Path:
        source = self.repo_root / file_path
        backup = source.with_suffix(source.suffix + ".bak")
        if source.exists():
            backup.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        return backup

    def write_or_patch(self, rel_path: str, content: str, reason: str) -> dict[str, Any]:
        target = self.repo_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = self.backup_file(rel_path)
        else:
            backup = None

        target.write_text(content, encoding="utf-8")
        return {
            "status": "updated",
            "path": rel_path,
            "reason": reason,
            "backup": str(backup) if backup else None,
        }

    def append_note(self, rel_path: str, note: str) -> dict[str, Any]:
        target = self.repo_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        new_text = ""
        if target.exists():
            new_text = target.read_text(encoding="utf-8")
        new_text += f"\n# Auto-generated note\n{note}\n"
        return self.write_or_patch(rel_path, new_text, "append note")
