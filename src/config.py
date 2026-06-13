"""config.py — carrega settings.yaml."""
from pathlib import Path
import yaml

_dados: dict | None = None

def cfg(caminho: str, padrao=None):
    global _dados
    if _dados is None:
        for p in [Path(__file__).parent, Path(__file__).parent.parent]:
            f = p / "config" / "settings.yaml"
            if f.exists():
                _dados = yaml.safe_load(f.read_text(encoding="utf-8"))
                break
        if _dados is None:
            raise FileNotFoundError("config/settings.yaml não encontrado.")
    val = _dados
    for k in caminho.split("."):
        val = val.get(k) if isinstance(val, dict) else None
        if val is None:
            return padrao
    return val
