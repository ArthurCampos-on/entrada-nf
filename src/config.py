"""
config.py — carrega settings.yaml com validação de campos obrigatórios.

Melhoria [8] aplicada:
  Após carregar o YAML, verifica se os campos críticos existem.
  Erros de configuração geram mensagens claras em vez de AttributeError
  crípticos lançados no meio da execução do RPA.
"""
from pathlib import Path
import yaml

_dados: dict | None = None

# [8] Campos que precisam existir no settings.yaml.
# Formato: "secao.chave" — os mesmos aceitos pela função cfg().
_CAMPOS_OBRIGATORIOS = [
    "agendador.horario_diario",
    "imagens.pasta",
    "imagens.confianca",
    "automacao.delay_acao",
    "automacao.timeout_elemento",
    "automacao.tentativas",
    "empresa.nome_filtro",
    "empresa.nome_completo",
    "financeiro.entrada_dias",
    "financeiro.intervalo_dias",
    "financeiro.total_parcelas",
    "financeiro.tipo_pagamento",
    "locacao.padrao",
    "locacao.tipo_fabrica",
    "locacao.tipo_pecas",
    "logging.nivel",
    "logging.arquivo",
    "entrada_cte.faturamento_entrada_dias",
    "entrada_cte.faturamento_intervalo_dias",
    "entrada_cte.faturamento_parcelas",
    "entrada_cte.codigo_contabilizacao",
]


def cfg(caminho: str, padrao: object = None) -> object:
    """
    Lê um valor do settings.yaml usando notação de pontos.

    Args:
        caminho: Caminho no formato "secao.chave" (ex: "imagens.confianca").
        padrao:  Valor retornado se a chave não existir.

    Returns:
        O valor encontrado no YAML ou *padrao* se ausente.

    Exemplos:
        cfg("imagens.confianca")       → 0.8
        cfg("financeiro.entrada_dias") → 60
        cfg("chave.inexistente", "?")  → "?"
    """
    global _dados
    if _dados is None:
        _carregar()
    val = _dados
    for k in caminho.split("."):
        val = val.get(k) if isinstance(val, dict) else None
        if val is None:
            return padrao
    return val


def _carregar() -> None:
    """Carrega o YAML e valida os campos obrigatórios. [8]"""
    global _dados
    for p in [Path(__file__).parent, Path(__file__).parent.parent]:
        f = p / "config" / "settings.yaml"
        if f.exists():
            _dados = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            _validar()
            return
    raise FileNotFoundError("config/settings.yaml não encontrado.")


def _validar() -> None:
    """[8] Verifica campos obrigatórios e lança erro claro se algum faltar."""
    faltando: list[str] = []
    for campo in _CAMPOS_OBRIGATORIOS:
        val = _dados
        for k in campo.split("."):
            val = val.get(k) if isinstance(val, dict) else None
        if val is None:
            faltando.append(campo)

    if faltando:
        linhas = "\n  - ".join(faltando)
        raise ValueError(
            f"settings.yaml está incompleto. Campos obrigatórios ausentes:\n  - {linhas}\n"
            "Consulte o arquivo config/settings.yaml para ver os valores esperados."
        )
