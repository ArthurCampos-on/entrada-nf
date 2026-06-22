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


def rodar(cmd: list[str]) -> None:
    print(f"  $ {' '.join(cmd)}")
    subprocess.check_call(cmd)


def main() -> None:
    print("\n=== NBS Agent v1.1.0 — Setup ===\n")

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

  1. ✏  Edite config/settings.yaml com suas configurações.

  2. 🖼  Adicione as imagens dos botões em imagens/
       Use Win+Shift+S (Windows) ou equivalente para recortar cada elemento.
       Dicas: recorte pequeno e preciso, sem sombras, sem bordas extras.

       RELATÓRIO (10 imagens):
         campo_empresa.png              → campo de seleção da empresa
         empresa_duna_tubarao.png       → opção Duna-Tubarão na lista
         entrada_data_relatorio.png     → campo data de entrada
         emissao_data_relatorio.png     → campo data de emissão
         botao_pesquisa_relatorio.png   → botão pesquisar
         botao_nota_relatorio.png       → aba Nota (ordena crescente)
         btn_imprimir_lista.png         → botão Imprimir Lista
         botao_sim.png                  → botão Sim (confirmação)
         botao_icone_impressao_relatorio.png → ícone de impressão
         aba_ipressao_relatorio.png     → tela do relatório no browser

       TRANSFERÊNCIA (11 imagens — algumas compartilhadas com Fábrica):
         botao_incluir.png              → botão Incluir em Compras
         botao_transferencia.png        → opção Transferência
         btn_interface.png              → botão Interface
         btn_interface_saida.png        → opção Interface de Saída
         btn_pesquisar_transf.png       → botão pesquisar notas
         btn_aceitar.png                → botão Aceitar
         aba_locacao.png                → aba Locações
         campo_locacao.png              → placeholder de locação
         principal_pecas.png            → opção PRINCIPAL(PEÇAS)
         locacao_padrao.png             → placeholder locação padrão
         btn_confirmar.png              → botão Confirmar/OK final

       FÁBRICA (15 imagens — botao_incluir, btn_interface, btn_aceitar,
                aba_locacao, campo_locacao, principal_pecas, locacao_padrao
                já capturadas acima):
         botao_compra.png               → opção Compra
         placeholder_nota_fabrica.png   → campo número da nota
         btn_pesquisar_nota.png         → botão pesquisar nota
         aba_definir_tributacao.png     → aba Definir Tributação/CFOP
         area_centro.png                → referência visual centro tela
         definir_cfop.png               → opção Definir CFOP (menu direito)
         campo_tributados.png           → dropdown Tributados
         selecao_pecas_acessorios.png   → opção COMPRA PEÇAS E ACESSÓRIOS
         btn_ok.png                     → botão OK
         aba_cruzamento_pedidos.png     → aba Cruzamento de Pedidos
         seta_cruzamento.png            → seta → do cruzamento
         botao_confirmar.png            → botão Confirmar no cruzamento
         aba_financeiro.png             → aba Financeiro
         btn_confirmar_final.png        → botão Confirmar final

       ENTRADA CT-e (24 imagens — já incluídas no projeto):
         adm_aba.png · nbs_fiscal.png · entrada_cte.png
         incluir_icone.png · persona.png · icone_pesquisa.png
         aceitar_icone.png · numerode_nota.png · modelo_fiscal.png
         barra_modelo.png · codigo_57.png · barra_natureza.png
         cfops.png · codigo_natureza.png · tributavel_codigo.png
         naotributavel_codigo.png · verde_aceitar.png · adicao.png
         contabilizacao.png · raio.png · faturamento.png
         seta_preta.png · confirmar.png
         cancelar.png  ← PENDENTE: capturar quando botão aparecer no fluxo

  3. ▶  Execute:
       python __main__.py

  4. 📋  Consulte a documentação:
       ARCHITECTURE.md  → visão técnica e fluxo de execução
       IMAGENS.md       → tabela completa de imagens
       TROUBLESHOOTING.md → problemas comuns e soluções
       COMO_USAR.md     → guia do usuário final

=================================
""")


if __name__ == "__main__":
    main()
