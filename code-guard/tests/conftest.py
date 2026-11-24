import json
from pathlib import Path

import pytest


@pytest.fixture
def repo(tmp_path: Path):
    """Petit dépôt factice ; write(chemin, contenu) crée un fichier relatif à la racine."""

    def write(rel: str, content) -> Path:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not isinstance(content, str):
            content = json.dumps(content)
        path.write_text(content, encoding="utf-8")
        return path

    write.root = tmp_path
    return write
