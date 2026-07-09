"""IssueProvider interface — implement this to integrate any issue tracker.

Enterprise plugins implement this ABC and register
themselves in ~/.geno/settings.json under tasks.providers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class IssueProvider(ABC):
    """Adapter between geno-tasks and an external issue tracker."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier, e.g. 'jira', 'linear', 'github'."""

    @abstractmethod
    def fetch(self, issue_id: str) -> dict:
        """Return a dict of issue metadata by ID."""

    @abstractmethod
    def list_assigned(self) -> list[dict]:
        """Return issues currently assigned to the configured user."""

    @abstractmethod
    def list_reported(self) -> list[dict]:
        """Return issues reported/created by the configured user."""


def load_providers() -> list[IssueProvider]:
    """Discover and instantiate all registered providers from settings.json."""
    import json
    from pathlib import Path
    settings_path = Path.home() / ".geno" / "settings.json"
    if not settings_path.exists():
        return []
    try:
        data = json.loads(settings_path.read_text())
        provider_specs = data.get("tasks", {}).get("providers", [])
    except Exception:
        return []
    providers = []
    for spec in provider_specs:
        module_path = spec.get("module")
        class_name = spec.get("class")
        if not module_path or not class_name:
            continue
        try:
            import importlib
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            providers.append(cls(spec.get("config", {})))
        except Exception:
            pass
    return providers
