"""
setup.py
--------
Instala dependências e verifica se tudo está pronto.
Execute uma vez antes de rodar o sistema:
  python scripts/setup.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def rodar(cmd: list):
    print(f"  $ {' '.join(cmd)}")
    subprocess.check_call(cmd)


def main():
    print("\n=== NBS Agent — Setup ===\n")

    # 1. Cria pastas necessárias
    print("Criando pastas...")
    for pasta in ["data/logs", "data/screenshots", "imagens"]:
        (ROOT / pasta).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {pasta}/")

    # 2. Instala dependências
    print("\nInstalando dependências...")
    rodar([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])

    # 3. Checklist de configuração
    print("""
=== Checklist antes de rodar ===

  1. ✏  Edite config/settings.yaml com:
       - URL do NBS (já está: http://10.32.1.139:85/)
       - cloud_usuario e cloud_senha (login Cloud Service)
       - nbs_usuario e nbs_senha (login NBS Shortcut)

  2. 🖼  Adicione as imagens dos botões em imagens/:
       Use Win+Shift+S para recortar cada elemento da tela

       LOGIN:
         campo_usuario_nbs.png   → campo Usuário do NBS Shortcut
         btn_confirmar.png       → botão Confirmar do NBS Shortcut
         menu_principal.png      → menu lateral após login

       RELATÓRIO:
         menu_compras.png        → ícone Compras no menu
         empresa_duna_tubarao.png→ DUNA - TUBARAO na lista
         campo_data_entrada.png  → campo de data de Entrada
         campo_data_emissao.png  → campo de data de Emissão
         btn_oculos_pesquisar.png→ ícone de óculos (pesquisar)
         aba_nota.png            → aba Nota
         btn_imprimir_lista.png  → botão Imprimir Lista
         btn_sim.png             → botão Sim da confirmação
         opcao_screen.png        → opção Screen na impressão
         btn_print.png           → botão Print
         btn_impressora_viewer.png → ícone da impressora no viewer
         btn_print_viewer.png    → botão Print no viewer
         btn_imprimir_final.png  → botão Imprimir do Ctrl+P

       FÁBRICA:
         btn_incluir.png         → botão Incluir na barra
         opcao_compra.png        → opção Compra no popup
         btn_interface.png       → botão Interface
         campo_numero_nota.png   → campo Número Nota
         aba_definir_cfop.png    → aba Definir Tributação/CFOP
         menu_definir_cfop.png   → item 'Definir CFOP' no menu direito
         janela_cfop.png         → título da janela Interface de Compra CFOP
         dropdown_tributados.png → dropdown Tributados
         opcao_tributavel.png    → opção Tributável / COMPRA PECAS
         campo_tributados_pesquisa.png → campo de pesquisa no dropdown
         menu_tabelas.png        → menu Tabelas na barra
         menu_tabela_itens.png   → item Tabela de Itens
         opcao_compra_pecas_fe.png → COMPRA PECAS E ACESSORIOS F/E
         btn_ok.png              → botão OK
         btn_aceitar.png         → botão Aceitar
         aba_cruzamento_pedidos.png → aba Cruzamento de Pedidos
         seta_direita_cruzamento.png → seta → do cruzamento
         pedido_lista_esquerda.png  → pedido na lista esquerda
         item_pedido_azul_direita.png → item azul já na lista direita
         btn_recalculo.png       → botão Recálculo
         aba_locacoes.png        → aba Locações
         dropdown_local.png      → dropdown Local
         opcao_principal_pecas.png → opção PRINCIPAL(PEÇAS)
         campo_locacao.png       → campo Locação
         btn_sugestao.png        → botão Sugestão
         aba_financeiro.png      → aba Financeiro
         campo_entrada_dias.png  → campo Entrada (Dias)
         campo_intervalo_dias.png→ campo Intervalo (Dias)
         campo_total_parcelas.png→ campo Total Parcelas
         dropdown_tipo_pagamento.png → dropdown Tipo de Pagamento
         opcao_boleto_bancario.png → opção Boleto Bancário
         btn_gerar_financeiro.png→ botão Gerar
         btn_confirmar.png       → botão Confirmar final

  3. ▶  Execute:
       python __main__.py

=================================
""")


if __name__ == "__main__":
    main()
