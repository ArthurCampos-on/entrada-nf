"""
mapeamento_imagens.py
---------------------
Mapeia cada nome de botão/elemento (usado nos RPAs) para o arquivo
de imagem real extraído do docx BOTÕES_PRINT.

Como identificamos cada imagem:
  - Dimensões muito pequenas (< 120px) = ícones/botões pequenos
  - Dimensões médias = botões de ação
  - Dimensões grandes = capturas de tela completas (referência visual)

ATENÇÃO: Algumas imagens precisam ser renomeadas para os nomes que
o código dos RPAs espera (ex: 'btn_incluir.png').
Execute este script uma vez para criar os links corretos na pasta imagens/.

Uso:
    python src/mapeamento_imagens.py
"""

import os
import shutil
from pathlib import Path

# Raiz do projeto
RAIZ = Path(__file__).parent.parent
PASTA_IMAGENS = RAIZ / "imagens"


# ------------------------------------------------------------------ #
#  MAPEAMENTO: nome_esperado_pelo_rpa -> arquivo_real_extraido        #
#                                                                     #
#  ⚠ PREENCHA ESTE DICIONÁRIO após ver as imagens visualmente.       #
#  Execute:  python src/mapeamento_imagens.py --visualizar            #
#  para abrir cada imagem e identificar o que é.                     #
# ------------------------------------------------------------------ #

MAPA = {

    # ── LOGIN ──────────────────────────────────────────────────────────
    # login_01: campo usuário NBS Shortcut   (207x47)
    # login_02: campo senha NBS Shortcut     (214x46)
    # login_03: botão Confirmar              (235x54)
    "campo_usuario_nbs":    "login_01_image40.png",
    "campo_senha_nbs":      "login_02_image6.png",
    "btn_confirmar_login":  "login_03_image18.png",
    "menu_principal":       "login_01_image40.png",  # ← AJUSTE após ver

    # ── COMPRAS ────────────────────────────────────────────────────────
    # compras_01: ícone Compras no menu      (67x57)
    # compras_02: tela principal Compras     (981x403) ← tela de referência
    # compras_03: empresa DUNA TUBARAO       (212x52)
    "menu_compras":              "compras_01_image2.png",
    "empresa_duna_tubarao":      "compras_03_image27.png",

    # ── RELATÓRIO ──────────────────────────────────────────────────────
    # relatorio_01: campo data              (200x27)
    # relatorio_02: calendário/datepicker   (286x205)
    # relatorio_03: outro datepicker        (248x204)
    # relatorio_04: ícone óculos pesquisar  (59x47)
    # relatorio_05: aba Nota                (100x57)
    # relatorio_06: btn Imprimir Lista      (89x58)
    # relatorio_07: btn de ação             (102x31)
    # relatorio_08: btn Sim                 (138x57)
    # relatorio_09: ícone pequeno           (32x40)
    # relatorio_10: btn Print/Screen        (123x55)
    "campo_data_entrada":       "relatorio_01_image36.png",
    "campo_data_emissao":       "relatorio_01_image36.png",  # mesmo campo ← AJUSTE
    "btn_oculos_pesquisar":     "relatorio_04_image41.png",
    "aba_nota":                 "relatorio_05_image33.png",
    "btn_imprimir_lista":       "relatorio_06_image15.png",
    "btn_sim":                  "relatorio_08_image22.png",
    "opcao_screen":             "relatorio_10_image35.png",
    "btn_print":                "relatorio_07_image14.png",
    "btn_impressora_viewer":    "relatorio_09_image44.png",
    "btn_print_viewer":         "relatorio_07_image14.png",  # ← AJUSTE
    "btn_imprimir_final":       "relatorio_08_image22.png",  # ← AJUSTE

    # ── FÁBRICA ────────────────────────────────────────────────────────
    # fabrica_01: btn Incluir              (80x66)
    # fabrica_02: opção Compra             (73x53)
    # fabrica_03: btn Interface            (124x64)
    # fabrica_04: campo Número Nota        (125x32)
    # fabrica_05: aba Definir CFOP         (196x51)
    # fabrica_06: item Definir CFOP menu   (154x44)
    # fabrica_07: tela referência fábrica  (1060x404) ← tela inteira
    # fabrica_08: janela CFOP              (369x64)
    # fabrica_09: dropdown Tributados      (272x35)
    # fabrica_10: campo longo (tabela?)    (503x52)
    # fabrica_11: btn OK/Aceitar           (120x39)
    "btn_incluir":               "fabrica_01_image9.png",
    "opcao_compra":              "fabrica_02_image17.png",
    "btn_interface":             "fabrica_03_image38.png",
    "campo_numero_nota":         "fabrica_04_image31.png",
    "aba_definir_cfop":          "fabrica_05_image4.png",
    "menu_definir_cfop":         "fabrica_06_image1.png",
    "janela_cfop":               "fabrica_08_image26.png",
    "dropdown_tributados":       "fabrica_09_image34.png",
    "opcao_tributavel":          "fabrica_09_image34.png",  # ← AJUSTE
    "campo_tributados_pesquisa": "fabrica_09_image34.png",  # ← AJUSTE
    "menu_tabelas":              "fabrica_10_image19.png",  # ← AJUSTE
    "menu_tabela_itens":         "fabrica_10_image19.png",  # ← AJUSTE
    "opcao_compra_pecas_fe":     "fabrica_09_image34.png",  # ← AJUSTE
    "btn_ok":                    "fabrica_11_image8.png",
    "btn_aceitar":               "fabrica_11_image8.png",   # ← AJUSTE
    "btn_confirmar":             "fabrica_11_image8.png",   # ← AJUSTE

    # ── AINDA FALTAM (sem imagem por enquanto) ─────────────────────────
    # Estes precisam de novos recortes que você vai tirar depois:
    # "aba_cruzamento_pedidos"     ← aba na tela de entrada de nota
    # "seta_direita_cruzamento"    ← seta → do cruzamento de pedidos
    # "pedido_lista_esquerda"      ← pedido aparecendo à esquerda
    # "item_pedido_azul_direita"   ← item azul já na lista direita
    # "btn_recalculo"              ← botão Recálculo
    # "aba_locacoes"               ← aba Locações
    # "dropdown_local"             ← dropdown Local
    # "opcao_principal_pecas"      ← PRINCIPAL(PEÇAS)
    # "campo_locacao"              ← campo Locação
    # "btn_sugestao"               ← botão Sugestão
    # "aba_financeiro"             ← aba Financeiro
    # "campo_entrada_dias"         ← campo Entrada (Dias)
    # "campo_intervalo_dias"       ← campo Intervalo (Dias)
    # "campo_total_parcelas"       ← campo Total Parcelas
    # "dropdown_tipo_pagamento"    ← dropdown Tipo de Pagamento
    # "opcao_boleto_bancario"      ← opção Boleto Bancário
    # "btn_gerar_financeiro"       ← botão Gerar
}


def aplicar_mapeamento():
    """
    Cria cópias das imagens com os nomes esperados pelos RPAs.
    Não apaga as originais — apenas cria aliases.
    """
    criados = 0
    avisos  = 0

    for nome_rpa, arquivo_original in MAPA.items():
        origem = PASTA_IMAGENS / arquivo_original
        destino = PASTA_IMAGENS / f"{nome_rpa}.png"

        if not origem.exists():
            print(f"  ⚠ FALTANDO: {arquivo_original}  (necessário para '{nome_rpa}')")
            avisos += 1
            continue

        if destino.exists():
            continue  # Já existe, não sobrescreve

        shutil.copy2(origem, destino)
        criados += 1

    print(f"\n✓ {criados} imagens mapeadas.")
    if avisos:
        print(f"⚠ {avisos} imagens faltando — veja os comentários no mapa acima.")


def visualizar():
    """Abre cada imagem para identificação visual."""
    import subprocess, sys
    for secao in ["login", "compras", "relatorio", "fabrica", "transferencia", "entrada_cte"]:
        imgs = sorted([f for f in os.listdir(PASTA_IMAGENS) if f.startswith(secao)])
        for img in imgs:
            print(f"  {img}")
            # Abre a imagem no visualizador padrão do Windows
            caminho = str(PASTA_IMAGENS / img)
            if sys.platform == "win32":
                os.startfile(caminho)
            input("    Enter para próxima...")


if __name__ == "__main__":
    import sys
    if "--visualizar" in sys.argv:
        visualizar()
    else:
        print("Aplicando mapeamento de imagens...")
        aplicar_mapeamento()
        print("\nItens marcados com '← AJUSTE' precisam ser verificados visualmente.")
        print("Execute:  python src/mapeamento_imagens.py --visualizar")
