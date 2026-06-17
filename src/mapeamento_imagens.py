"""
mapeamento_imagens.py
---------------------
Fonte de verdade de TODAS as imagens do sistema.

Organização:
  IMAGENS_ATIVAS  — usadas pelos RPAs (relatorio, fabrica, transferencia)
  IMAGENS_COMPRAS — navegação manual (usuario chega em Compras antes de iniciar)

Como usar:
  python src/mapeamento_imagens.py           → valida que todos os PNGs existem
  python src/mapeamento_imagens.py --listar  → lista nomes e caminhos esperados

Nomes adotados:
  Os nomes-chave (ex: "botao_incluir_fabrica") são EXATAMENTE os nomes dos
  arquivos PNG em imagens/ (sem a extensão). Não há tradução — o que está
  aqui é o que está no disco e o que os RPAs passam para tela.clicar().
"""

from pathlib import Path

RAIZ          = Path(__file__).parent.parent
PASTA_IMAGENS = RAIZ / "imagens"


# ═══════════════════════════════════════════════════════════════════════════
#  IMAGENS ATIVAS — referenciadas pelos RPAs
# ═══════════════════════════════════════════════════════════════════════════

IMAGENS_ATIVAS = {

    # ── RELATÓRIO ──────────────────────────────────────────────────────────
    # Fluxo: seleciona empresa → preenche datas → pesquisa → imprime

    "selecao_empresa_relatorio":         "Caixa de seleção da empresa",
    "selecao_duna_tubarao_relatorio":    "Opção Duna-Tubarão na lista",
    "entrada_data_relatorio":            "Campo data de entrada (clicar, digitar, clicar de novo)",
    "emissao_data_relatorio":            "Campo data de emissão (clicar, digitar, clicar de novo)",
    "botao_pesquisa_relatorio":          "Botão pesquisar",
    "botao_nota_relatorio":              "Aba Nota (ordena crescente)",
    "botao_imprimir_lista_relatorio":    "Botão Imprimir Lista",
    "botao_sim_relatorio":               "Botão Sim (confirmação fiscal)",
    "botao_icone_impressao_relatorio":   "Ícone de impressão (abre viewer)",
    "aba_impressao_relatorio":           "Tela do relatório no browser (aguardar aparecer)",

    # ── TRANSFERÊNCIA ──────────────────────────────────────────────────────
    # Fluxo: incluir → transferência → interface → pesquisa → locação → confirmar

    "botao_incluir_transferencia":            "Botão Incluir em Compras",
    "botao_transferencia":                    "Opção Transferência",
    "botao_interface_relatorio":              "Botão Interface (carregar nota — mesmo botão do relatório)",
    "botao_nota_saida_transferencia":         "Opção Interface de Saída",
    "botao_pesquisa_transferencia":           "Botão pesquisar notas",
    "botao_aceitar_transferencia":            "Botão Aceitar (confirma nota)",
    "botao_locacao_transferencia":            "Aba Locações",
    "placeholder_locacao_transferencia":      "Placeholder de locação (tipo do item)",
    "selecao_principal_locacao_transferencia":"Opção PRINCIPAL(PEÇAS)",
    "locacao_padrao_transferencia":           "Placeholder locação padrão (digitar SL)",
    "botao_comfirmar_transferencia":          "Botão Confirmar/OK final da transferência",

    # ── FÁBRICA ────────────────────────────────────────────────────────────
    # Fluxo: incluir → compra → interface → nota → tributação → cruzamento → locação → financeiro

    "botao_incluir_fabrica":              "Botão Incluir em Compras",
    "botao_compra_fabrica":               "Opção Compra",
    "botao_interface_fabrica":            "Botão Interface (carregar nota)",
    "placeholder_nota_fabrica":           "Placeholder onde se digita o número da nota",
    "botao_pesquisar_notas_fabrica":      "Botão pesquisar nota",
    "aba_definir_tributacao_fabrica":     "Aba Definir Tributação/CFOP",
    "centro_definicao_tributos_fabrica":  "Referência visual: centro da tela de tributação (right-click aqui)",
    "definir_cfop_fabrica":               "Opção Definir CFOP no menu de contexto",
    "interface_correta_tributos_fabrica": "Tela CORRETA de tributação (sem placeholder de fonte)",
    "interface_errada_tributos_fabrica":  "Tela ERRADA de tributação (com placeholder de fonte visível)",
    "placeholder_tributados_fabrica":     "Dropdown Tributados",
    "selecao_pecas_acessorios_fabrica":   "Opção COMPRA PEÇAS E ACESSÓRIOS",
    "botao_ok_tributados":                "Botão OK na janela de tributação",
    "botao_aceitar_fabrica":              "Botão Aceitar",
    "aba_cruzamento_fabrica":             "Aba Cruzamento de Pedidos",
    "seta_fabrica":                       "Seta → para cruzar pedido",
    "botao_confirmar_pedido_fabrica":     "Botão Confirmar no cruzamento",
    "locacao_aba_fabrica":                "Aba Locações",
    "placeholder_locacao_fabrica":        "Placeholder Local (tipo do produto)",
    "principal_pecas_fabrica":            "Opção PRINCIPAL(PEÇAS)",
    "placeholder_padrao_fabrica":         "Placeholder Locação Padrão (digitar SL)",
    "aba_financeiro_fabrica":             "Aba Financeiro",
    "botao_confirmar_final_fabrica":      "Botão Confirmar final (fecha lançamento)",



# ── ENTRADA CT-e ───────────────────────────────────────────────────────
    # Fluxo: Fiscal → Entrada CT-e → nova entrada → dados → CFOP → tributação → confirmar

    "adm_aba":                "Aba ADM (abre o menu de módulos do NBS)",
    "nbs_fiscal":             "Ícone NBS Fiscal no menu de módulos",
    "entrada_cte":            "Opção Entrada CT-e dentro do Fiscal",
    "incluir_icone":          "Ícone/botão Incluir (nova entrada)",
    "persona":                "Campo Persona/Fornecedor",
    "icone_pesquisa":         "Ícone de lupa (pesquisa de fornecedor por CNPJ)",
    "aceitar_icone":          "Ícone aceitar (confirma seleção do fornecedor)",
    "numerode_nota":          "Campo Número da Nota (CT-e2: clica para limpar com Backspace)",
    "modelo_fiscal":          "Campo Modelo Fiscal (abre dropdown de modelos)",
    "barra_modelo":           "Barra de seleção do modelo fiscal",
    "codigo_57":              "Opção código 57 (CT-e) na lista de modelos",
    "barra_natureza":         "Campo/barra de Natureza da Operação",
    "cfops":                  "Área de CFOPs (clique para abrir seleção de código)",
    "codigo_natureza":        "Campo Código de Natureza (digitar 1353 ou 2353)",
    "tributavel_codigo":      "Opção Tributável na lista de tributação",
    "naotributavel_codigo":   "Opção Não Tributável na lista de tributação",
    "verde_aceitar":          "Botão verde de aceitar tributação",
    "adicao":                 "Botão Adição (confirma tributação e avança)",
    "contabilizacao":         "Aba Contabilização",
    "raio":                   "Ícone Raio (atalho contabilização automática)",
    "faturamento":            "Aba Faturamento",
    "seta_preta":             "Seta preta → (avança para próxima etapa)",
    "confirmar":              "Botão Confirmar (salva o lançamento CT-e)",
    "cancelar":               "Botão Cancelar/Fechar (aparece após confirmar — imagem a adicionar)",
}
# ═══════════════════════════════════════════════════════════════════════════
#  IMAGENS DE NAVEGAÇÃO — para referência, não usadas pelos RPAs atuais
#  (usuário chega na tela de Compras antes de iniciar o agente)
# ═══════════════════════════════════════════════════════════════════════════

IMAGENS_COMPRAS = {
    "menu_lateral":           "Menu lateral com ícones e abas",
    "pecas_aba":              "Aba que libera ícone de Compras",
    "compras_icone":          "Ícone de Compras",
    "compras_tela_empresas":  "Menu de empresas após clicar em Compras",
    "compras_botao_saida":    "Botão de saída para acessar Compras",
}


# ═══════════════════════════════════════════════════════════════════════════
#  VALIDAÇÃO
# ═══════════════════════════════════════════════════════════════════════════

def validar() -> bool:
    """
    Verifica que todos os PNGs referenciados em IMAGENS_ATIVAS existem.
    Retorna True se tudo OK, False se algum faltando.
    """
    faltando = []
    for nome in IMAGENS_ATIVAS:
        if not (PASTA_IMAGENS / f"{nome}.png").exists():
            faltando.append(nome)

    if not faltando:
        print(f"✓ Todas as {len(IMAGENS_ATIVAS)} imagens ativas encontradas.")
        return True

    print(f"⚠ {len(faltando)} imagem(ns) faltando em '{PASTA_IMAGENS}':")
    for nome in faltando:
        desc = IMAGENS_ATIVAS[nome]
        print(f"  ✗ {nome}.png  ←  {desc}")
    return False


def listar():
    """Lista todas as imagens esperadas com descrição."""
    print("\n── IMAGENS ATIVAS (usadas pelos RPAs) ──────────────────────────")
    for nome, desc in IMAGENS_ATIVAS.items():
        existe = "✓" if (PASTA_IMAGENS / f"{nome}.png").exists() else "✗"
        print(f"  {existe} {nome}.png")
        print(f"       {desc}")

    print("\n── IMAGENS DE NAVEGAÇÃO (referência — não usadas nos RPAs) ─────")
    for nome, desc in IMAGENS_COMPRAS.items():
        existe = "✓" if (PASTA_IMAGENS / f"{nome}.png").exists() else "✗"
        print(f"  {existe} {nome}.png")
        print(f"       {desc}")


if __name__ == "__main__":
    import sys
    if "--listar" in sys.argv:
        listar()
    else:
        ok = validar()
        sys.exit(0 if ok else 1)
