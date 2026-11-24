from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, order=True)
class Finding:
    """Un problème détecté par une règle, rattaché à un fichier et une ligne."""

    path: str
    line: int
    rule: str
    message: str
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data

    def format(self) -> str:
        return f"{self.path}:{self.line}: [{self.severity.value}] {self.rule} – {self.message}"
