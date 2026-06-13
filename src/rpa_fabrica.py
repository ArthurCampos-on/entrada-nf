"""
rpa_fabrica.py
--------------
Lança notas de fábrica — fluxo conforme documentação:

  1.  Estar em Compras
  2.  Clicar em Incluir
  3.  Clicar em Compra
  4.  Clicar em Interface
  5.  Digitar número da nota no placeholder
  6.  Clicar em Pesquisar
  7.  Clicar na aba Definir Tributação/CFOP
  8.  Botão direito no centro da tela
  9.  Clicar em Definir CFOP
  10. Clicar no placeholder de Tributados
      → selecionar COMPRA PECAS E ACESSORIOS (F/E ou D/E)
  11. Clicar em OK
  12. Clicar em Aceitar
  13. Clicar na aba Cruzamento de Pedidos
  14. Clicar na seta direita
  15. Clicar em Confirmar
  16. Clicar em OK
  17. Clicar em Recálculo
  18. Ir para aba Locações
  19. Clicar no placeholder Local
  20. Clicar em PRINCIPAL(PEÇAS)
  21. Clicar no placeholder Locação Padrão → digitar SL → Enter
  22. Ir para aba Financeiro
  23. Digitar 60 → Enter → 60 → Enter → 1 → Enter → Boleto Bancario → Enter
  24. Clicar em Confirmar

Pausas manuais:
  - Após passo 6 (pesquisar nota): aguarda você fazer trabalho manual → Y/N
  - Se cruzamento não encontrar pedido: pausa para correção manual → Y/N
"""

import time
from src.tela import Tela
from src.logger import log


class LancamentoFabrica:
    """Executa o lançamento de notas de fábrica."""

    def __init__(self, tela: Tela):
        self.tela = tela

    def lancar_notas(self, notas: list[str]) -> dict:
        """
        Lança uma ou mais notas.
        Retorna dict {numero_nota: True/False}
        """
        resultados = {}
        total = len(notas)
        for i, nota in enumerate(notas, 1):
            nota = nota.strip()
            log.info(f"[{i}/{total}] Lançando nota: {nota}")
            resultados[nota] = self._lancar_uma_nota(nota)
            if i < total:
                self.tela.esperar(1)
        return resultados

    # ------------------------------------------------------------------ #
    #  FLUXO DE UMA NOTA                                                  #
    # ------------------------------------------------------------------ #

    def _lancar_uma_nota(self, numero: str) -> bool:
        try:
            self._passos_1_4_abrir_interface()
            self._passo_5_6_digitar_nota(numero)

            # Pausa manual — trabalho nos itens
            ok = self.tela.pausar_para_usuario(
                f"Nota {numero} — confira os dados carregados.\n"
                "  Quando estiver pronto pressione Y para continuar."
            )
            if not ok:
                log.warning(f"Nota {numero}: cancelada no passo manual.")
                return False

            self._passo_7_aba_cfop()
            self._passo_8_9_definir_cfop()
            self._passo_10_tributacao()
            self._passo_11_ok()
            self._passo_12_aceitar()
            self._passo_13_aba_cruzamento()

            if not self._passo_14_16_cruzamento_pedidos(numero):
                return False

            self._passo_17_recalculo()
            self._passos_18_21_locacoes()
            self._passos_22_23_financeiro()
            self._passo_24_confirmar()

            log.info(f"✓ Nota {numero} lançada.")
            return True

        except TimeoutError as e:
            log.error(f"Timeout na nota {numero}: {e}")
            self.tela.screenshot(f"erro_fabrica_{numero}")
            return False
        except Exception as e:
            log.error(f"Erro na nota {numero}: {e}")
            self.tela.screenshot(f"erro_fabrica_{numero}")
            return False

    # ------------------------------------------------------------------ #
    #  PASSOS                                                             #
    # ------------------------------------------------------------------ #

    def _passos_1_4_abrir_interface(self):
        """Passos 1-4: Incluir → Compra → Interface."""
        log.debug("Passos 1-4: abrindo interface de compra...")
        self.tela.clicar("btn_incluir_fabrica")
        self.tela.esperar(0.5)
        self.tela.clicar("opcao_compra")
        self.tela.esperar(0.5)
        self.tela.clicar("btn_interface_fabrica")
        self.tela.esperar(1)

    def _passo_5_6_digitar_nota(self, numero: str):
        """Passos 5-6: digitar número da nota e pesquisar."""
        log.debug(f"Passos 5-6: digitando nota {numero} e pesquisando...")
        self.tela.clicar("campo_numero_nota")
        self.tela.limpar_e_digitar(numero)
        self.tela.clicar("btn_pesquisar_nota")
        self.tela.esperar(2)

    def _passo_7_aba_cfop(self):
        """Passo 7: aba Definir Tributação/CFOP."""
        log.debug("Passo 7: abrindo aba Definir Tributação...")
        self.tela.clicar("aba_definir_cfop")
        self.tela.esperar(0.8)

    def _passo_8_9_definir_cfop(self):
        """Passos 8-9: botão direito no centro → Definir CFOP."""
        log.debug("Passos 8-9: botão direito → Definir CFOP...")
        self.tela.clique_direito_centro_tela()
        self.tela.esperar(0.5)
        self.tela.clicar("menu_definir_cfop")
        self.tela.esperar(0.5)

    def _passo_10_tributacao(self):
        """
        Passo 10: clicar no placeholder Tributados e selecionar
        COMPRA PECAS E ACESSORIOS (pode ser F/E ou D/E).
        """
        log.debug("Passo 10: selecionando tributação...")
        self.tela.clicar("campo_tributados")
        self.tela.esperar(0.5)
        self.tela.clicar("opcao_compra_pecas")
        self.tela.esperar(0.3)

    def _passo_11_ok(self):
        """Passo 11: clicar em OK."""
        log.debug("Passo 11: OK...")
        self.tela.clicar("btn_ok_cfop")

    def _passo_12_aceitar(self):
        """Passo 12: clicar em Aceitar."""
        log.debug("Passo 12: Aceitar...")
        self.tela.clicar("btn_aceitar_cfop")

    def _passo_13_aba_cruzamento(self):
        """Passo 13: aba Cruzamento de Pedidos."""
        log.debug("Passo 13: aba Cruzamento de Pedidos...")
        self.tela.clicar("aba_cruzamento_pedidos")
        self.tela.esperar(1)

    def _passo_14_16_cruzamento_pedidos(self, numero: str) -> bool:
        """
        Passos 14-16: seta direita → Confirmar → OK.
        Se não encontrar pedido, pausa para correção manual.
        """
        log.debug("Passos 14-16: cruzamento de pedidos...")

        # Tenta clicar na seta direita
        if self.tela.existe("seta_direita_cruzamento"):
            self.tela.clicar("seta_direita_cruzamento")
            self.tela.esperar(0.5)
            self.tela.clicar("btn_confirmar_cruzamento")
            self.tela.esperar(0.5)
            if self.tela.existe("btn_ok_cruzamento"):
                self.tela.clicar("btn_ok_cruzamento")
            return True

        # Pedido não encontrado — pausa manual
        log.warning(f"Nota {numero}: pedido não encontrado no cruzamento.")
        return self.tela.pausar_para_usuario(
            f"Nota {numero} — pedido não encontrado automaticamente.\n"
            "  Resolva manualmente e deixe o item azul do lado direito.\n"
            "  Depois pressione Y para continuar."
        )

    def _passo_17_recalculo(self):
        """Passo 17: Recálculo."""
        log.debug("Passo 17: Recálculo...")
        self.tela.clicar("btn_recalculo")
        self.tela.esperar(1.5)

    def _passos_18_21_locacoes(self):
        """
        Passos 18-21: aba Locações → PRINCIPAL(PEÇAS) → SL → Enter.
        """
        log.debug("Passos 18-21: configurando locações...")
        self.tela.clicar("aba_locacoes_fabrica")
        self.tela.esperar(0.8)
        # Clica no placeholder Local
        self.tela.clicar("campo_local_fabrica")
        self.tela.esperar(0.5)
        # Seleciona PRINCIPAL(PEÇAS)
        self.tela.clicar("opcao_principal_fabrica")
        self.tela.esperar(0.5)
        # Digita SL no placeholder de locação e aperta Enter
        self.tela.clicar("campo_locacao_fabrica")
        self.tela.digitar("SL")
        self.tela.tecla("enter")
        self.tela.esperar(0.5)

    def _passos_22_23_financeiro(self):
        """
        Passos 22-23: aba Financeiro.
        Digita: 60 → Enter → 60 → Enter → 1 → Enter → Boleto Bancario → Enter
        """
        log.debug("Passos 22-23: configurando financeiro...")
        self.tela.clicar("aba_financeiro")
        self.tela.esperar(0.8)
        # Entrada (dias): 60
        self.tela.digitar("60")
        self.tela.tecla("enter")
        # Intervalo (dias): 60
        self.tela.digitar("60")
        self.tela.tecla("enter")
        # Total parcelas: 1
        self.tela.digitar("1")
        self.tela.tecla("enter")
        # Tipo pagamento: Boleto Bancario
        self.tela.digitar("Boleto Bancario")
        self.tela.tecla("enter")
        self.tela.esperar(1)

    def _passo_24_confirmar(self):
        """Passo 24: Confirmar — finaliza o lançamento."""
        log.debug("Passo 24: Confirmar final...")
        self.tela.clicar("btn_confirmar_final")
        self.tela.esperar(2)
