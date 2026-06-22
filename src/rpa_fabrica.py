"""
rpa_fabrica.py — Lança notas de fábrica.

Fluxo completo (baseado em FABRICA.docx):
  1.  Incluir                               → botao_incluir
  2.  Compra                                → botao_compra
  3.  Interface                             → btn_interface
  4.  Clicar no placeholder da nota         → placeholder_nota_fabrica
  5.  Digitar número da nota
  6.  Pesquisar                             → btn_pesquisar_nota
  7.  Aba Definir Tributação/CFOP           → aba_definir_tributacao
  8.  Confirmar tela → botão direito centro → area_centro (referência)
  9.  Definir CFOP                          → definir_cfop
  10. Verificar interface:
        Tela correta → continua             → interface_correta_tributos (referência)
        Tela errada  → pausa manual         → interface_errada_tributos (referência)
  11. Clicar em Tributados                  → campo_tributados
  12. Compra Peças e Acessórios             → selecao_pecas_acessorios
  13. OK                                    → btn_ok
  14. Aceitar                               → btn_aceitar
  15. Aba Cruzamento de Pedidos             → aba_cruzamento_pedidos
  16. ⏸ PAUSA MANUAL — usuário digita 1, 2 ou 3:
        1 → Tentar cruzamento automático (seta_cruzamento → botao_confirmar)
              Se seta não encontrada → pausa (Y para continuar)
        2 → Pular cruzamento, ir direto para Locações
        3 → Pular esta nota inteira
  17. [ITEM LOCAÇÃO] Aba Locações           → aba_locacao
  18. Placeholder locação                   → campo_locacao
  19. PRINCIPAL(PEÇAS)                      → principal_pecas
  20. Locação padrão → digitar SL           → locacao_padrao
  21. Enter
  22. Aba Financeiro                        → aba_financeiro
  23. Digitar: 60 → Enter → 60 → Enter → 1 → Enter → Boleto Bancario → Enter
  24. Confirmar                             → btn_confirmar_final
  25. Seta Esquerda + Enter → Enter → Enter
"""

from src.tela   import Tela
from src.config import cfg
from src.logger import log


class LancamentoFabrica:

    def __init__(self, tela: Tela) -> None:
        self.tela = tela
        self._locacao_padrao = cfg("locacao.padrao",        "SL")
        self._locacao_tipo   = cfg("locacao.tipo_fabrica",  "PRINCIPAL(PEÇAS)")
        self._fin_entrada    = str(cfg("financeiro.entrada_dias",   60))
        self._fin_intervalo  = str(cfg("financeiro.intervalo_dias", 60))
        self._fin_parcelas   = str(cfg("financeiro.total_parcelas",  1))
        self._fin_pagamento  = cfg("financeiro.tipo_pagamento", "Boleto Bancario")

    def lancar_notas(self, notas: list[str]) -> dict[str, bool]:
        """
        Lança uma ou mais notas de fábrica.

        Args:
            notas: Lista de números de nota a lançar.

        Returns:
            Dicionário mapeando número da nota → True (sucesso) / False (falha).
        """
        resultados: dict[str, bool] = {}
        total = len(notas)
        for i, nota in enumerate(notas, 1):
            nota = nota.strip()
            log.info(f"[{i}/{total}] Fábrica: {nota}")
            resultados[nota] = self._lancar_uma_nota(nota)
            if i < total:
                self.tela.esperar(1)
        return resultados

    # ─────────────────────────────────────────────────────────────────

    def _lancar_uma_nota(self, numero: str) -> bool:
        try:
            self._passos_1_3_abrir_interface()
            self._passos_4_6_carregar_nota(numero)
            self._passo_7_aba_tributacao()
            self._passos_8_9_definir_cfop()

            if not self._passo_10_verificar_interface(numero):
                return False

            self._passo_11_tributados()
            self._passo_12_pecas_acessorios()
            self._passo_13_ok()
            self._passo_14_aceitar()
            self._passo_15_aba_cruzamento()

            acao = self._passo_16_manual_cruzamento(numero)
            if acao == "pular":
                log.info(f"Nota {numero}: pulada pelo usuário.")
                return False

            # acao == "locacoes" — continua daqui
            self._passos_17_21_locacoes()
            self._passos_22_23_financeiro()
            self._passo_24_confirmar()
            self._passo_25_teclado_final()

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

    # ─────────────────────────────────────────────────────────────────
    #  PASSOS
    # ─────────────────────────────────────────────────────────────────

    def _passos_1_3_abrir_interface(self) -> None:
        """Passos 1-3: Incluir → Compra → Interface."""
        log.debug("Passos 1-3: abrindo interface de compra...")
        self.tela.clicar("botao_incluir")
        self.tela.esperar(0.5)
        self.tela.clicar("botao_compra")
        self.tela.esperar(0.5)
        self.tela.clicar("btn_interface")
        self.tela.esperar(1)

    def _passos_4_6_carregar_nota(self, numero: str) -> None:
        """Passos 4-6: placeholder → digitar nota → pesquisar."""
        log.debug(f"Passos 4-6: carregando nota {numero}...")
        self.tela.clicar("placeholder_nota_fabrica")
        self.tela.limpar_e_digitar(numero)
        self.tela.clicar("btn_pesquisar_nota")
        self.tela.esperar(2)

    def _passo_7_aba_tributacao(self) -> None:
        """Passo 7: aba Definir Tributação/CFOP."""
        log.debug("Passo 7: aba Definir Tributação...")
        self.tela.clicar("aba_definir_tributacao")
        self.tela.esperar(0.8)

    def _passos_8_9_definir_cfop(self) -> None:
        """
        Passos 8-9: confirma tela (area_centro é referência visual)
        → botão direito no centro → Definir CFOP.
        """
        log.debug("Passos 8-9: confirmando tela e clicando em Definir CFOP...")
        # Aguarda a tela de tributação aparecer (validação visual)
        self.tela.aguardar("area_centro")
        # Botão direito no centro fixo da tela
        self.tela.clique_direito_centro_tela()
        self.tela.esperar(0.5)
        self.tela.clicar("definir_cfop")
        self.tela.esperar(1)

    def _passo_10_verificar_interface(self, numero: str) -> bool:
        """
        Passo 10: usuário informa o estado da tela de tributação.

        Opções:
            1 → Tela correta — automação continua normalmente
            2 → Tela errada  — usuário corrige e digita Y para continuar
            3 → Pular esta nota

        Returns:
            True para continuar, False para pular a nota.
        """
        log.debug("Passo 10: aguardando confirmação da interface de tributação...")
        self.tela.esperar(1)

        acao = self.tela.pedir_opcao(
            f"Tributação — Nota {numero}",
            {
                "1": "Tela correta — continuar",
                "2": "Tela errada — corrigir manualmente",
                "3": "Pular esta nota",
            }
        )

        if acao == "3":
            log.info(f"Nota {numero}: pulada na verificação de tributação.")
            return False

        if acao == "2":
            log.warning(f"Nota {numero}: correção manual de tributação.")
            return self.tela.pausar_para_usuario(
                f"Nota {numero} — corrija a tributação manualmente.\n"
                "  Pressione Y quando estiver na tela correta."
            )

        # acao == "1": tela correta confirmada pelo usuário
        log.debug("Passo 10: tributação confirmada.")
        return True

    def _passo_11_tributados(self) -> None:
        """Passo 11: clicar em Tributados (dropdown)."""
        log.debug("Passo 11: Tributados...")
        self.tela.clicar("campo_tributados")
        self.tela.esperar(0.5)

    def _passo_12_pecas_acessorios(self) -> None:
        """Passo 12: selecionar Compra Peças e Acessórios."""
        log.debug("Passo 12: Compra Peças e Acessórios...")
        self.tela.clicar("selecao_pecas_acessorios")
        self.tela.esperar(0.3)

    def _passo_13_ok(self) -> None:
        log.debug("Passo 13: OK...")
        self.tela.clicar("btn_ok")

    def _passo_14_aceitar(self) -> None:
        log.debug("Passo 14: Aceitar...")
        self.tela.clicar("btn_aceitar")

    def _passo_15_aba_cruzamento(self) -> None:
        log.debug("Passo 15: aba Cruzamento de Pedidos...")
        self.tela.clicar("aba_cruzamento_pedidos")
        self.tela.esperar(1)

    def _passo_16_manual_cruzamento(self, numero: str) -> str:
        """
        Passo 16: ⏸ PAUSA MANUAL — usuário decide como prosseguir.

        Opções:
            1 → Tentar cruzamento automático (procura seta_cruzamento e clica)
                  Se seta não encontrada → nova pausa (Y para continuar para locações)
            2 → Pular cruzamento e ir direto para Locações
            3 → Pular esta nota inteira

        Returns:
            "locacoes" (continuar) ou "pular" (abandonar nota).
        """
        acao = self.tela.pedir_opcao(
            f"Cruzamento de Pedidos — Nota {numero}",
            {
                "1": "Tentar cruzamento automático (clicar na seta)",
                "2": "Pular cruzamento e ir direto para Locações",
                "3": "Pular esta nota",
            }
        )

        if acao == "3":
            return "pular"

        if acao == "2":
            log.info(f"Nota {numero}: cruzamento pulado pelo usuário → indo para Locações.")
            return "locacoes"

        # acao == "1": tenta clicar na seta
        log.debug("Tentando cruzamento automático...")
        if self.tela.existe("seta_cruzamento"):
            self.tela.clicar("seta_cruzamento")
            self.tela.esperar(0.5)
            self.tela.clicar("botao_confirmar")
            log.debug("Cruzamento automático concluído.")
            return "locacoes"

        # Seta não encontrada — pausa manual
        log.warning(f"Nota {numero}: seta de cruzamento não encontrada.")
        ok = self.tela.pausar_para_usuario(
            f"Nota {numero} — seta não encontrada automaticamente.\n"
            "  Resolva o cruzamento manualmente.\n"
            "  Pressione Y quando pronto para continuar para Locações."
        )
        return "locacoes" if ok else "pular"

    def _passos_17_21_locacoes(self) -> None:
        """Passos 17-21: aba Locações → placeholder → PRINCIPAL(PEÇAS) → SL → Enter."""
        log.debug(f"Passos 17-21: locações (tipo={self._locacao_tipo}, cód={self._locacao_padrao})...")
        self.tela.clicar("aba_locacao")
        self.tela.esperar(0.8)
        self.tela.clicar("campo_locacao")
        self.tela.esperar(0.5)
        self.tela.clicar("principal_pecas")
        self.tela.esperar(0.5)
        self.tela.clicar("locacao_padrao")
        self.tela.digitar(self._locacao_padrao)   # "SL"
        self.tela.tecla("enter")
        self.tela.esperar(0.5)

    def _passos_22_23_financeiro(self) -> None:
        """
        Passos 22-23: aba Financeiro → 60 → 60 → 1 → Boleto Bancario → Enter.

        Valores lidos do settings.yaml.
        """
        log.debug(
            f"Passos 22-23: financeiro "
            f"(entrada={self._fin_entrada}d, intervalo={self._fin_intervalo}d, "
            f"parcelas={self._fin_parcelas}, pgto={self._fin_pagamento})..."
        )
        self.tela.clicar("aba_financeiro")
        self.tela.esperar(0.8)
        self.tela.digitar(self._fin_entrada)
        self.tela.tecla("enter")
        self.tela.digitar(self._fin_intervalo)
        self.tela.tecla("enter")
        self.tela.digitar(self._fin_parcelas)
        self.tela.tecla("enter")
        self.tela.digitar(self._fin_pagamento)
        self.tela.tecla("enter")
        self.tela.esperar(1)

    def _passo_24_confirmar(self) -> None:
        """Passo 24: Confirmar — fecha o lançamento."""
        log.debug("Passo 24: Confirmar final...")
        self.tela.clicar("btn_confirmar_final")
        self.tela.esperar(1.5)

    def _passo_25_teclado_final(self) -> None:
        """
        Passo 25: Seta Esquerda + Enter → Enter → Enter.

        Fecha as janelas de confirmação restantes via teclado.
        """
        log.debug("Passo 25: teclado final (← Enter, Enter, Enter)...")
        self.tela.tecla("left")
        self.tela.tecla("enter")
        self.tela.tecla("enter")
        self.tela.tecla("enter")
        self.tela.esperar(1.5)
