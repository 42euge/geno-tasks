"""DeployAdapter interface — implement this to integrate any static site builder + publisher.

Enterprise plugins register an implementation in ~/.geno/settings.json under
tasks.deploy_adapter:

  {
    "tasks": {
      "deploy_adapter": {
        "module": "your_plugin.deploy",
        "class": "YourAdapter",
        "config": {}
      }
    }
  }
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path


class DeployAdapter(ABC):
    """Adapter between geno-tasks and a static site builder + publisher."""

    @abstractmethod
    def build(self, tasks_dir: Path, output_dir: Path) -> None:
        """Generate a static site from tasks_dir into output_dir."""

    @abstractmethod
    def publish(self, output_dir: Path) -> None:
        """Publish the built output_dir to wherever the adapter targets."""


def load_adapter() -> DeployAdapter | None:
    """Instantiate the configured deploy adapter, or None if not set."""
    import json, importlib
    settings_path = Path.home() / ".geno" / "settings.json"
    if not settings_path.exists():
        return None
    try:
        spec = json.loads(settings_path.read_text()).get("tasks", {}).get("deploy_adapter")
        if not spec:
            return None
        mod = importlib.import_module(spec["module"])
        cls = getattr(mod, spec["class"])
        return cls(spec.get("config", {}))
    except Exception:
        return None
