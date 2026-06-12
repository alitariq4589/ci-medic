from typing import Protocol


class Provider(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Return model output for a system/user prompt pair."""
        ...
