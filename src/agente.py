"""
agente.py
---------
Orquestrador principal — une browser, RPAs, agendador e menu.

OBS: o login no NBS (Cloud Service + NBS Shortcut) NÃO é feito por
este agente. O usuário deve estar logado no sistema antes de usar
as automações (relatórios, fábrica, transferência).
"""

from src.browser           import Browser
from src.tela              import Tela
from src.rpa_relatorio     import RelatorioCompras
from src.rpa_fabrica       import LancamentoFabrica
from src.rpa_transferencia import LancamentoTransferencia
from src.agendador         import Agendador
from src.menu              import pedir_notas
from src.config            import cfg
from src.logger            import log, configurar


class NBSAgent:

    def __init__(self):
        configurar(
            nivel   = cfg("logging.nivel",   "INFO"),
            arquivo = cfg("logging.arquivo", "data/logs/nbs_agent.log"),
        )
        self.browser    = Browser()
        self.tela       = Tela()
        self._agendador = None

    # ------------------------------------------------------------------ #
    #  INICIALIZAÇÃO                                                      #
    # ------------------------------------------------------------------ #

    def iniciar(self) -> bool:
        """Inicializa o agente — conecta ao Chrome já aberto pelo usuário."""
        log.info("=" * 50)
        log.info("  NBS Agent iniciando...")
        log.info("=" * 50)

        self.browser.iniciar()
        log.info("✓ Sistema pronto para automações.")
        return True

    def iniciar_agendador(self):
        """Inicia o agendador do relatório diário automático."""
        self._agendador = Agendador(callback_relatorio=self.relatorio_diario)
        self._agendador.iniciar()

    def encerrar(self):
        """Para o agendador. O Chrome fica aberto (usuário continua no sistema)."""
        if self._agendador:
            self._agendador.parar()
        log.info("NBS Agent encerrado.")

    # ------------------------------------------------------------------ #
    #  AÇÕES                                                              #
    # ------------------------------------------------------------------ #

    def relatorio_diario(self):
        """Gera o relatório de compras do dia anterior."""
        log.info("Iniciando relatório diário...")
        self.browser.focar_nbs()
        ok = RelatorioCompras(self.tela).gerar_dia_anterior()
        if ok:
            print("  ✓ Relatório gerado com sucesso.")
        else:
            print("  ✗ Falha no relatório. Veja data/logs/ para detalhes.")
        return ok

    def lancar_fabrica(self):
        """Pergunta as notas e executa lançamento de fábrica."""
        notas = pedir_notas("fábrica")
        if not notas:
            return
        self.browser.focar_nbs()
        resultados = LancamentoFabrica(self.tela).lancar_notas(notas)
        self._exibir_resultados(resultados)

    def lancar_transferencia(self):
        """Pergunta as notas e executa lançamento de transferência."""
        notas = pedir_notas("transferência")
        if not notas:
            return
        self.browser.focar_nbs()
        resultados = LancamentoTransferencia(self.tela).lancar_notas(notas)
        self._exibir_resultados(resultados)

    # ------------------------------------------------------------------ #
    #  HELPERS                                                            #
    # ------------------------------------------------------------------ #

    def _exibir_resultados(self, resultados: dict):
        print("\n  Resultado:")
        for nota, ok in resultados.items():
            icone = "✓" if ok else "✗"
            print(f"  {icone} Nota {nota}: {'OK' if ok else 'FALHOU'}")
