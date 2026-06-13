"""
rpa_relatorio.py
----------------
Gera o relatório de compras — 14 passos conforme documentação:

  1.  Clicar no placeholder da empresa
  2.  Digitar "Duna"
  3.  Clicar em Duna Tubarão
  4.  Trocar data de Entrada e Emissão para o dia anterior
  5.  Clicar em Pesquisar
  6.  Clicar na aba Nota
  7.  Clicar em Imprimir Lista
  8.  Clicar em Sim
  9.  Clicar em Print (Screen)
  10. Clicar no ícone de impressão (desenho)
  11. Clicar em Print no viewer
  12. Tela do relatório abre no browser
  13. Ctrl+P → Enter (imprimir)
  14. Fim da automação do relatório
"""

import time
from datetime import date, timedelta
from src.tela import Tela
from src.logger import log


class RelatorioCompras:
    """Executa o fluxo de geração do relatório de compras."""

    def __init__(self, tela: Tela):
        self.tela = tela

    def gerar_dia_anterior(self) -> bool:
        """Gera o relatório do dia anterior (chamado automaticamente às 8h)."""
        ontem = date.today() - timedelta(days=1)
        data_str = ontem.strftime("%d/%m/%Y")
        log.info(f"Gerando relatório diário — {data_str}")
        return self._executar(data_str)

    # ------------------------------------------------------------------ #
    #  FLUXO PRINCIPAL                                                    #
    # ------------------------------------------------------------------ #

    def _executar(self, data: str) -> bool:
        try:
            self._passo_1_3_selecionar_empresa()
            self._passo_4_preencher_datas(data)
            self._passo_5_pesquisar()
            self._passo_6_aba_nota()
            self._passo_7_imprimir_lista()
            self._passo_8_clicar_sim()
            self._passo_9_print_screen()
            self._passo_10_11_imprimir_viewer()
            self._passo_13_ctrl_p()
            log.info("✓ Relatório gerado com sucesso.")
            return True
        except TimeoutError as e:
            log.error(f"Timeout no relatório: {e}")
            self.tela.screenshot("erro_relatorio")
            return False
        except Exception as e:
            log.error(f"Erro no relatório: {e}")
            self.tela.screenshot("erro_relatorio")
            return False

    # ------------------------------------------------------------------ #
    #  PASSOS                                                             #
    # ------------------------------------------------------------------ #

    def _passo_1_3_selecionar_empresa(self):
        """Passos 1-3: seleciona empresa Duna Tubarão."""
        log.debug("Passos 1-3: selecionando empresa...")
        # Clica no placeholder da empresa
        self.tela.clicar("campo_empresa")
        self.tela.esperar(0.5)
        # Digita Duna para filtrar
        self.tela.digitar("Duna")
        self.tela.esperar(0.8)
        # Clica em Duna Tubarão na lista
        self.tela.clicar("empresa_duna_tubarao")

    def _passo_4_preencher_datas(self, data: str):
        """
        Passo 4: preenche data de Entrada e Emissão.
        Clica no campo, limpa e digita a data — mais rápido que usar o calendário.
        """
        log.debug(f"Passo 4: preenchendo datas com {data}...")

        # Data de Entrada
        self.tela.clicar("campo_data_entrada")
        self.tela.limpar_e_digitar(data)
        self.tela.tecla("enter")

        # Data de Emissão
        self.tela.clicar("campo_data_emissao")
        self.tela.limpar_e_digitar(data)
        self.tela.tecla("enter")

    def _passo_5_pesquisar(self):
        """Passo 5: clicar em Pesquisar."""
        log.debug("Passo 5: pesquisando...")
        self.tela.clicar("btn_pesquisar")
        self.tela.esperar(2)  # aguarda resultados carregarem

    def _passo_6_aba_nota(self):
        """Passo 6: clicar na aba Nota."""
        log.debug("Passo 6: clicando na aba Nota...")
        self.tela.clicar("aba_nota")

    def _passo_7_imprimir_lista(self):
        """Passo 7: clicar em Imprimir Lista."""
        log.debug("Passo 7: Imprimir Lista...")
        self.tela.clicar("btn_imprimir_lista")

    def _passo_8_clicar_sim(self):
        """Passo 8: clicar em Sim na confirmação fiscal. Sempre Sim."""
        log.debug("Passo 8: confirmando com Sim...")
        self.tela.clicar("btn_sim")

    def _passo_9_print_screen(self):
        """Passo 9: clicar em Print (opção Screen)."""
        log.debug("Passo 9: selecionando Print/Screen...")
        self.tela.clicar("btn_print")

    def _passo_10_11_imprimir_viewer(self):
        """Passos 10-11: clicar no ícone de impressão e depois em Print."""
        log.debug("Passos 10-11: imprimindo no viewer...")
        self.tela.clicar("btn_desenho_imprimir")
        self.tela.esperar(1)
        self.tela.clicar("btn_print_viewer")

    def _passo_13_ctrl_p(self):
        """
        Passo 13: relatório abre no browser — Ctrl+P e Enter para imprimir.
        Destino já vem selecionado como Duna Estoque.
        """
        log.debug("Passo 13: Ctrl+P → Enter...")
        self.tela.esperar(2)  # aguarda a tela do browser abrir
        self.tela.tecla("ctrl", "p")
        self.tela.esperar(1.5)
        self.tela.tecla("enter")
        log.debug("Relatório enviado para impressão.")
