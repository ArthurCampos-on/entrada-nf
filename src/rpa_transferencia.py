"""
rpa_transferencia.py
--------------------
Lança notas de transferência — 16 passos:

  1.  Estar em Compras (já abre em compras)
  2.  Clicar em Incluir
  3.  Clicar em Transferência
  4.  Clicar em Interface
  5.  Clicar em Interface de Saída
  6.  Clicar em Pesquisar
  7.  Clicar em Aceitar
  8.  Clicar em Confirmar
  9.  Clicar em OK
  10. Clicar na aba Locações
  11. Clicar no placeholder de Locação
  12. Escolher PRINCIPAL(PEÇAS)
  13. Clicar no placeholder Locação Padrão → digitar SL → Sugestão ou Enter
  14. Clicar em OK
  15. Clicar em Não (ou Enter)
  16. Clicar em OK (ou Enter) — fim
"""

import time
from src.tela import Tela
from src.logger import log


class LancamentoTransferencia:
    """Executa o lançamento de notas de transferência."""

    def __init__(self, tela: Tela):
        self.tela = tela

    def lancar_notas(self, notas: list[str]) -> dict:
        """
        Lança uma ou mais notas de transferência.
        Retorna dict {numero_nota: True/False}
        """
        resultados = {}
        total = len(notas)
        for i, nota in enumerate(notas, 1):
            nota = nota.strip()
            log.info(f"[{i}/{total}] Transferência nota: {nota}")
            resultados[nota] = self._lancar_uma_nota(nota)
            if i < total:
                self.tela.esperar(1)
        return resultados

    # ------------------------------------------------------------------ #
    #  FLUXO DE UMA NOTA                                                  #
    # ------------------------------------------------------------------ #

    def _lancar_uma_nota(self, numero: str) -> bool:
        try:
            self._passos_1_5_abrir_interface()
            self._passo_6_pesquisar()
            self._passo_7_aceitar()
            self._passo_8_confirmar()
            self._passo_9_ok()
            self._passos_10_13_locacoes()
            self._passo_14_ok()
            self._passo_15_nao()
            self._passo_16_ok_final()
            log.info(f"✓ Transferência {numero} lançada.")
            return True

        except TimeoutError as e:
            log.error(f"Timeout na transferência {numero}: {e}")
            self.tela.screenshot(f"erro_transf_{numero}")
            return False
        except Exception as e:
            log.error(f"Erro na transferência {numero}: {e}")
            self.tela.screenshot(f"erro_transf_{numero}")
            return False

    # ------------------------------------------------------------------ #
    #  PASSOS                                                             #
    # ------------------------------------------------------------------ #

    def _passos_1_5_abrir_interface(self):
        """Passos 1-5: Incluir → Transferência → Interface → Interface de Saída."""
        log.debug("Passos 1-5: abrindo interface de transferência...")
        self.tela.clicar("btn_incluir")
        self.tela.esperar(0.5)
        self.tela.clicar("opcao_transferencia")
        self.tela.esperar(0.5)
        self.tela.clicar("btn_interface")
        self.tela.esperar(0.5)
        self.tela.clicar("btn_interface_saida")
        self.tela.esperar(1)

    def _passo_6_pesquisar(self):
        """Passo 6: Pesquisar."""
        log.debug("Passo 6: pesquisando...")
        self.tela.clicar("btn_pesquisar_transf")
        self.tela.esperar(1.5)

    def _passo_7_aceitar(self):
        """Passo 7: Aceitar."""
        log.debug("Passo 7: Aceitar...")
        self.tela.clicar("btn_aceitar")

    def _passo_8_confirmar(self):
        """Passo 8: Confirmar."""
        log.debug("Passo 8: Confirmar...")
        self.tela.clicar("btn_confirmar")

    def _passo_9_ok(self):
        """Passo 9: OK."""
        log.debug("Passo 9: OK...")
        self.tela.clicar("btn_ok")

    def _passos_10_13_locacoes(self):
        """Passos 10-13: aba Locações → PRINCIPAL(PEÇAS) → SL → Sugestão."""
        log.debug("Passos 10-13: locações...")
        self.tela.clicar("aba_locacoes")
        self.tela.esperar(0.8)
        # Placeholder de locação
        self.tela.clicar("campo_local_dropdown")
        self.tela.esperar(0.5)
        # PRINCIPAL(PEÇAS)
        self.tela.clicar("opcao_principal_pecas")
        self.tela.esperar(0.5)
        # Locação padrão: SL + Sugestão ou Enter
        self.tela.clicar("campo_locacao_padrao")
        self.tela.digitar("SL")
        self.tela.esperar(0.3)
        # Tenta clicar em Sugestão, senão aperta Enter
        if self.tela.existe("btn_sugestao"):
            self.tela.clicar("btn_sugestao")
        else:
            self.tela.tecla("enter")
        self.tela.esperar(0.5)

    def _passo_14_ok(self):
        """Passo 14: OK."""
        log.debug("Passo 14: OK...")
        self.tela.clicar("btn_ok_locacao")

    def _passo_15_nao(self):
        """Passo 15: Não (ou Enter)."""
        log.debug("Passo 15: Não...")
        if self.tela.existe("btn_nao"):
            self.tela.clicar("btn_nao")
        else:
            self.tela.tecla("enter")

    def _passo_16_ok_final(self):
        """Passo 16: OK final."""
        log.debug("Passo 16: OK final...")
        if self.tela.existe("btn_ok_final"):
            self.tela.clicar("btn_ok_final")
        else:
            self.tela.tecla("enter")
        self.tela.esperar(1.5)
