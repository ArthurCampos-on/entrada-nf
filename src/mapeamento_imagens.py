"""
mapeamento_imagens.py
---------------------
Fonte de verdade de TODAS as imagens do sistema.

Organização:
  IMAGENS_ATIVAS  — usadas pelos RPAs (relatorio, fabrica, transferencia, entrada_cte)
  IMAGENS_COMPRAS — navegação manual (usuario chega em Compras antes de iniciar)

Como usar:
  python src/mapeamento_imagens.py           → valida que todos os PNGs existem
  python src/mapeamento_imagens.py --listar  → lista nomes e caminhos esperados

Nomes adotados:
  Os nomes-chave (ex: "btn_confirmar_final") são EXATAMENTE os nomes dos
  arquivos PNG (ou JPEG) em imagens/ (sem a extensão). Não há tradução —
  o que está aqui é o que está no disco e o que os RPAs passam para tela.clicar().
"""

from pathlib import Path

RAIZ          = Path(__file__).parent.parent
PASTA_IMAGENS = RAIZ / "imagens"


# ═══════════════════════════════════════════════════════════════════════════
#  IMAGENS ATIVAS — referenciadas pelos RPAs
# ═══════════════════════════════════════════════════════════════════════════

IMAGENS_ATIVAS: dict[str, str] = {

    # ── RELATÓRIO ──────────────────────────────────────────────────────────
    # Fluxo: seleciona empresa → preenche datas → pesquisa → imprime

    "campo_empresa":                "Caixa de seleção da empresa",
    "empresa_duna_tubarao":         "Opção Duna-Tubarão na lista",
    "entrada_data_relatorio":       "Campo data de entrada (clicar, digitar, clicar de novo)",
    "emissao_data_relatorio":       "Campo data de emissão (clicar, digitar, clicar de novo)",
    "botao_pesquisa_relatorio":     "Botão pesquisar",
    "botao_nota_relatorio":         "Aba Nota (ordena crescente)",
    "btn_imprimir_lista":           "Botão Imprimir Lista",
    "botao_sim":                    "Botão Sim (confirmação fiscal)",
    "botao_icone_impressao_relatorio": "Ícone de impressão (abre viewer)",
    "aba_ipressao_relatorio":       "Tela do relatório no browser (aguardar aparecer)",

    # ── TRANSFERÊNCIA ──────────────────────────────────────────────────────
    # Fluxo: incluir → transferência → interface → pesquisa → locação → confirmar

    "botao_incluir":                "Botão Incluir em Compras (compartilhado: fábrica e transferência)",
    "botao_transferencia":          "Opção Transferência",
    "btn_interface":                "Botão Interface (carregar nota — compartilhado)",
    "btn_interface_saida":          "Opção Interface de Saída",
    "btn_pesquisar_transf":         "Botão pesquisar notas (transferência)",
    "btn_aceitar":                  "Botão Aceitar (compartilhado: fábrica e transferência)",
    "aba_locacao":                  "Aba Locações (compartilhada: fábrica e transferência)",
    "campo_locacao":                "Placeholder de locação — tipo do item (compartilhado)",
    "principal_pecas":              "Opção PRINCIPAL(PEÇAS) (compartilhada)",
    "locacao_padrao":               "Placeholder locação padrão — digitar SL (compartilhado)",
    "btn_confirmar":                "Botão Confirmar/OK final da transferência",

    # ── FÁBRICA ────────────────────────────────────────────────────────────
    # Fluxo: incluir → compra → interface → nota → tributação → cruzamento → locação → financeiro

    "botao_compra":                 "Opção Compra",
    "placeholder_nota_fabrica":     "Placeholder onde se digita o número da nota",
    "btn_pesquisar_nota":           "Botão pesquisar nota (fábrica)",
    "aba_definir_tributacao":       "Aba Definir Tributação/CFOP",
    "area_centro":                  "Referência visual: centro da tela de tributação (right-click aqui)",
    "definir_cfop":                 "Opção Definir CFOP no menu de contexto",
    "campo_tributados":             "Dropdown Tributados",
    "selecao_pecas_acessorios":     "Opção COMPRA PEÇAS E ACESSÓRIOS",
    "btn_ok":                       "Botão OK na janela de tributação",
    "aba_cruzamento_pedidos":       "Aba Cruzamento de Pedidos",
    "seta_cruzamento":              "Seta → para cruzar pedido",
    "botao_confirmar":              "Botão Confirmar no cruzamento de pedidos",
    "aba_financeiro":               "Aba Financeiro",
    "btn_confirmar_final":          "Botão Confirmar final (fecha lançamento de fábrica)",

    # ── ENTRADA CT-e ───────────────────────────────────────────────────────
    # Fluxo: Fiscal → Entrada CT-e → nova entrada → dados → CFOP → tributação → confirmar

    "adm_aba":                      "Aba ADM (abre o menu de módulos do NBS)",
    "nbs_fiscal":                   "Ícone NBS Fiscal no menu de módulos",
    "entrada_cte":                  "Opção Entrada CT-e dentro do Fiscal",
    "incluir_icone":                "Ícone/botão Incluir (nova entrada)",
    "persona":                      "Campo Persona/Fornecedor",
    "icone_pesquisa":               "Ícone de lupa (pesquisa de fornecedor por CNPJ)",
    "aceitar_icone":                "Ícone aceitar (confirma seleção do fornecedor)",
    "numerode_nota":                "Campo Número da Nota (CT-e2: clica para limpar com Backspace)",
    "modelo_fiscal":                "Campo Modelo Fiscal (abre dropdown de modelos)",
    "barra_modelo":                 "Barra de seleção do modelo fiscal",
    "codigo_57":                    "Opção código 57 (CT-e) na lista de modelos",
    "barra_natureza":               "Campo/barra de Natureza da Operação",
    "cfops":                        "Área de CFOPs (clique para abrir seleção de código)",
    "codigo_natureza":              "Campo Código de Natureza (digitar 1353 ou 2353)",
    "tributavel_codigo":            "Opção Tributável na lista de tributação",
    "naotributavel_codigo":         "Opção Não Tributável na lista de tributação",
    "verde_aceitar":                "Botão verde de aceitar tributação",
    "adicao":                       "Botão Adição (confirma tributação e avança)",
    "contabilizacao":               "Aba Contabilização",
    "raio":                         "Ícone Raio (atalho contabilização automática)",
    "faturamento":                  "Aba Faturamento",
    "seta_preta":                   "Seta preta → (avança para próxima etapa)",
    "confirmar":                    "Botão Confirmar (salva o lançamento CT-e)",
    "cancelar":                     "Botão Cancelar/Fechar (pendente: capturar quando adicionado ao fluxo)",
}


# ═══════════════════════════════════════════════════════════════════════════
#  IMAGENS DE NAVEGAÇÃO — para referência, não usadas pelos RPAs atuais
# ═══════════════════════════════════════════════════════════════════════════

IMAGENS_COMPRAS: dict[str, str] = {
    "menu_lateral":          "Menu lateral com ícones e abas",
    "pecas_aba":             "Aba que libera ícone de Compras",
    "compras_icone":         "Ícone de Compras",
    "compras_tela_empresas": "Menu de empresas após clicar em Compras",
    "compras_botao_saida":   "Botão de saída para acessar Compras",
}


# ═══════════════════════════════════════════════════════════════════════════
#  VALIDAÇÃO
# ═══════════════════════════════════════════════════════════════════════════

_PENDENTES = {"cancelar"}   # imagens conhecidas como pendentes (sem PNG ainda)


def _existe(nome: str) -> bool:
    """Verifica se PNG ou JPEG do nome existe em imagens/."""
    return (
        (PASTA_IMAGENS / f"{nome}.png").exists()
        or (PASTA_IMAGENS / f"{nome}.jpeg").exists()
        or (PASTA_IMAGENS / f"{nome}.jpg").exists()
    )


def validar() -> bool:
    """
    Verifica que todos os PNGs/JPEGs referenciados em IMAGENS_ATIVAS existem.

    Returns:
        True se tudo OK (ou apenas pendentes faltando), False se algum ativo falta.
    """
    faltando = [
        nome for nome in IMAGENS_ATIVAS
        if not _existe(nome) and nome not in _PENDENTES
    ]

    total_ativos = len(IMAGENS_ATIVAS) - len(_PENDENTES)

    if not faltando:
        print(f"✓ Todas as {total_ativos} imagens ativas encontradas.  "
              f"({', '.join(_PENDENTES)} é pendente conforme design)")
        return True

    print(f"⚠ {len(faltando)} imagem(ns) faltando em '{PASTA_IMAGENS}':")
    for nome in faltando:
        desc = IMAGENS_ATIVAS[nome]
        print(f"  ✗ {nome}.png  ←  {desc}")
    return False


def listar() -> None:
    """Lista todas as imagens esperadas com status e descrição."""
    print("\n── IMAGENS ATIVAS (usadas pelos RPAs) ──────────────────────────")
    for nome, desc in IMAGENS_ATIVAS.items():
        if nome in _PENDENTES:
            status = "⏳"
        elif _existe(nome):
            status = "✓"
        else:
            status = "✗"
        print(f"  {status} {nome}.png")
        print(f"       {desc}")

    print("\n── IMAGENS DE NAVEGAÇÃO (referência — não usadas nos RPAs) ─────")
    for nome, desc in IMAGENS_COMPRAS.items():
        status = "✓" if _existe(nome) else "✗"
        print(f"  {status} {nome}.png")
        print(f"       {desc}")


if __name__ == "__main__":
    import sys
    if "--listar" in sys.argv:
        listar()
    else:
        ok = validar()
        sys.exit(0 if ok else 1)
