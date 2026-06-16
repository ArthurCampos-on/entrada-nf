"""
rpa_transferencia.py — Lança notas de transferência.

Fluxo completo (baseado em TRANSFERÊNCIA.docx):
  1.  Clicar em Incluir                       → botao_incluir_transferencia
  2.  Clicar em Transferência                 → botao_transferencia
  3.  Clicar em Interface                     → botao_interface_relatorio
  4.  Clicar em Interface de Saída            → botao_nota_saida_transferencia
  5.  Clicar em Pesquisar                     → botao_pesquisa_transferencia
  6.  Clicar em Aceitar                       → botao_aceitar_transferencia
  7.  Apertar Enter
  8.  Clicar na aba Locação                   → botao_locacao_transferencia
  9.  Clicar no placeholder de locação        → placeholder_locacao_transferencia
  10. Escolher PRINCIPAL PEÇA                 → selecao_principal_locacao_transferencia
  11. Clicar em Locação Padrão e escrever SL  → locacao_padrao_transferencia
  12. Apertar Enter
  13. Clicar em OK/Confirmar                  → botao_comfirmar_transferencia
  14. Apertar Seta Esquerda + Enter
  15. Apertar Enter
  16. Apertar Enter
"""

from src.tela   import Tela
from src.config import cfg
from src.logger import log


class LancamentoTransferencia:

    def __init__(self, tela: Tela):
        self.tela = tela
        self._locacao_padrao = cfg("locacao.padrao",     "SL")
        self._locacao_tipo   = cfg("locacao.tipo_pecas", "PRINCIPAL(PEÇAS)")

    def lancar_notas(self, notas: list[str]) -> dict:
        """Lança uma ou mais notas. Retorna {numero: True/False}."""
        resultados = {}
        total = len(notas)
        for i, nota in enumerate(notas, 1):
            nota = nota.strip()
            log.info(f"[{i}/{total}] Transferência: {nota}")
            resultados[nota] = self._lancar_uma_nota(nota)
            if i < total:
                self.tela.esperar(1)
        return resultados

    # ─────────────────────────────────────────────────────────────────

    def _lancar_uma_nota(self, numero: str) -> bool:
        try:
            self._passos_1_4_abrir_interface()
            self._passo_5_pesquisar()
            self._passo_6_aceitar()
            self._passo_7_enter()
            self._passos_8_12_locacoes()
            self._passo_13_confirmar()
            self._passos_14_16_teclado_final()
            log.info(f"✓ Transferência {numero} concluída.")
            return True
        except TimeoutError as e:
            log.error(f"Timeout na transferência {numero}: {e}")
            self.tela.screenshot(f"erro_transf_{numero}")
            return False
        except Exception as e:
            log.error(f"Erro na transferência {numero}: {e}")
            self.tela.screenshot(f"erro_transf_{numero}")
            return False

    # ─────────────────────────────────────────────────────────────────

    def _passos_1_4_abrir_interface(self):
        """Passos 1-4: Incluir → Transferência → Interface → Interface de Saída."""
        log.debug("Passos 1-4: abrindo interface de transferência...")
        self.tela.clicar("botao_incluir_transferencia")
        self.tela.esperar(0.5)
        self.tela.clicar("botao_transferencia")
        self.tela.esperar(0.5)
        self.tela.clicar("btn_interface")
        self.tela.esperar(0.5)
        self.tela.clicar("btn_interface_saida")
        self.tela.esperar(1)

    def _passo_5_pesquisar(self):
        log.debug("Passo 5: pesquisar...")
        self.tela.clicar("btn_pesquisar_transf")
        self.tela.esperar(1.5)

    def _passo_6_aceitar(self):
        log.debug("Passo 6: Aceitar...")
        self.tela.clicar("btn_aceitar")

    def _passo_7_enter(self):
        """Passo 7: Enter após Aceitar."""
        log.debug("Passo 7: Enter...")
        self.tela.tecla("enter")

    def _passos_8_12_locacoes(self):
        """
        Passos 8-12: aba Locação → placeholder → PRINCIPAL(PEÇAS) → SL → Enter.
        """
        log.debug(f"Passos 8-12: locações (tipo={self._locacao_tipo}, cód={self._locacao_padrao})...")
        self.tela.clicar("botao_locacao_transferencia")
        self.tela.esperar(0.8)
        self.tela.clicar("placeholder_locacao_transferencia")
        self.tela.esperar(0.5)
        self.tela.clicar("selecao_principal_locacao_transferencia")
        self.tela.esperar(0.5)
        self.tela.clicar("locacao_padrao_transferencia")
        self.tela.digitar(self._locacao_padrao)   # "SL"
        self.tela.tecla("enter")
        self.tela.esperar(0.5)

    def _passo_13_confirmar(self):
        log.debug("Passo 13: Confirmar...")
        self.tela.clicar("botao_comfirmar_transferencia")

    def _passos_14_16_teclado_final(self):
        """
        Passos 14-16: Seta Esquerda + Enter → Enter → Enter.
        Fecha as janelas de confirmação restantes via teclado.
        """
        log.debug("Passos 14-16: teclado final (← Enter, Enter, Enter)...")
        self.tela.tecla("left")
        self.tela.tecla("enter")
        self.tela.tecla("enter")
        self.tela.tecla("enter")
        self.tela.esperar(1.5)
