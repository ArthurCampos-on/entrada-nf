"""
rpa_relatorio.py — Gera o relatório de compras.

Fluxo completo (baseado em RELATÓRIO.docx):
  1.  Clicar no placeholder da empresa      → selecao_empresa_relatorio
  2.  Digitar "Duna" (filtro)
  3.  Clicar em Duna-Tubarão                → selecao_duna_tubarao_relatorio
  4a. Clicar no campo data de entrada       → entrada_data_relatorio
  4b. Digitar data do dia anterior
  4c. Clicar novamente para confirmar       → entrada_data_relatorio
  5a. Clicar no campo data de emissão       → emissao_data_relatorio
  5b. Digitar data do dia anterior
  5c. Clicar novamente para confirmar       → emissao_data_relatorio
  6.  Clicar em Pesquisar                   → botao_pesquisa_relatorio
  7.  Clicar em Nota (ordena crescente)     → botao_nota_relatorio
  8.  Clicar em Imprimir Lista              → botao_imprimir_lista_relatorio
  9.  Clicar em Sim                         → botao_sim_relatorio
  10. Apertar Enter
  11. Clicar no ícone de impressão          → botao_icone_impressao_relatorio
  12. Apertar Enter
  13. Aguardar tela do browser              → aba_impressao_relatorio
  14. Ctrl+P → Enter
"""

from datetime import date, timedelta

from src.tela   import Tela
from src.config import cfg
from src.logger import log


class RelatorioCompras:

    def __init__(self, tela: Tela):
        self.tela = tela
        self._nome_filtro  = cfg("empresa.nome_filtro",   "Duna")
        self._nome_empresa = cfg("empresa.nome_completo", "Duna Tubarão")

    def gerar_dia_anterior(self) -> bool:
        """Gera o relatório do dia anterior (chamado automaticamente pelo agendador às 8h)."""
        ontem    = date.today() - timedelta(days=1)
        data_str = ontem.strftime("%d/%m/%Y")
        log.info(f"Gerando relatório — data: {data_str}")
        return self._executar(data_str)

    # ─────────────────────────────────────────────────────────────────

    def _executar(self, data: str) -> bool:
        try:
            self._passos_1_3_selecionar_empresa()
            self._passos_4_5_preencher_datas(data)
            self._passo_6_pesquisar()
            self._passo_7_aba_nota()
            self._passo_8_imprimir_lista()
            self._passo_9_sim()
            self._passo_10_enter()
            self._passo_11_icone_impressao()
            self._passo_12_enter()
            self._passo_13_aguardar_browser()
            self._passo_14_ctrl_p()
            log.info("✓ Relatório concluído.")
            return True
        except TimeoutError as e:
            log.error(f"Timeout no relatório: {e}")
            self.tela.screenshot("erro_relatorio")
            return False
        except Exception as e:
            log.error(f"Erro no relatório: {e}")
            self.tela.screenshot("erro_relatorio")
            return False

    # ─────────────────────────────────────────────────────────────────

    def _passos_1_3_selecionar_empresa(self):
        """Passos 1-3: abre seleção de empresa e escolhe Duna-Tubarão."""
        log.debug("Passos 1-3: selecionando empresa...")
        self.tela.clicar("selecao_empresa_relatorio")
        self.tela.esperar(0.5)
        self.tela.digitar(self._nome_filtro)
        self.tela.esperar(0.8)
        self.tela.clicar("selecao_duna_tubarao_relatorio")

    def _passos_4_5_preencher_datas(self, data: str):
        """
        Passos 4-5: preenche data de entrada e emissão.
        ⚠ Cada campo exige: clicar → digitar → clicar de novo para confirmar.
        """
        log.debug(f"Passos 4-5: preenchendo datas com {data}...")

        # Data de entrada (clicar → digitar → clicar de novo)
        self.tela.clicar("entrada_data_relatorio")
        self.tela.limpar_e_digitar(data)
        self.tela.clicar("entrada_data_relatorio")   # confirma

        # Data de emissão (clicar → digitar → clicar de novo)
        self.tela.clicar("emissao_data_relatorio")
        self.tela.limpar_e_digitar(data)
        self.tela.clicar("emissao_data_relatorio")   # confirma

    def _passo_6_pesquisar(self):
        log.debug("Passo 6: pesquisar...")
        self.tela.clicar("botao_pesquisa_relatorio")
        self.tela.esperar(2)

    def _passo_7_aba_nota(self):
        log.debug("Passo 7: aba Nota...")
        self.tela.clicar("botao_nota_relatorio")

    def _passo_8_imprimir_lista(self):
        log.debug("Passo 8: Imprimir Lista...")
        self.tela.clicar("botao_imprimir_lista_relatorio")

    def _passo_9_sim(self):
        log.debug("Passo 9: Sim...")
        self.tela.clicar("botao_sim_relatorio")

    def _passo_10_enter(self):
        """Passo 10: Enter após o Sim."""
        log.debug("Passo 10: Enter...")
        self.tela.tecla("enter")

    def _passo_11_icone_impressao(self):
        log.debug("Passo 11: ícone de impressão...")
        self.tela.clicar("botao_icone_impressao_relatorio")

    def _passo_12_enter(self):
        """Passo 12: Enter para abrir no browser."""
        log.debug("Passo 12: Enter...")
        self.tela.tecla("enter")

    def _passo_13_aguardar_browser(self):
        """Passo 13: aguarda a tela do relatório aparecer no browser."""
        log.debug("Passo 13: aguardando browser...")
        self.tela.aguardar("aba_impressao_relatorio", timeout=20)
        self.tela.esperar(1)

    def _passo_14_ctrl_p(self):
        """Passo 14: Ctrl+P → Enter para imprimir."""
        log.debug("Passo 14: Ctrl+P → Enter...")
        self.tela.tecla("ctrl", "p")
        self.tela.esperar(1.5)
        self.tela.tecla("enter")
        log.debug("Relatório enviado para impressão.")
