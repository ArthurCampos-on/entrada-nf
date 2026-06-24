"""
agente.py
---------
Orquestrador principal — une RPAs, agendador e menu.

OBS: o login no NBS (Cloud Service + NBS Shortcut) NÃO é feito por
este agente. O usuário deve estar logado no sistema antes de usar
as automações (relatórios, fábrica, transferência, entrada CT-e).
"""

from src.tela              import Tela
from src.rpa_relatorio     import RelatorioCompras
from src.rpa_fabrica       import LancamentoFabrica
from src.rpa_transferencia import LancamentoTransferencia
from src.rpa_entrada_cte   import EntradaCTE
from src.agendador         import Agendador
from src.menu              import pedir_notas
from src.config            import cfg
from src.logger            import log, configurar


class NBSAgent:

    def __init__(self) -> None:
        configurar(
            nivel   = cfg("logging.nivel",   "INFO"),
            arquivo = cfg("logging.arquivo", "data/logs/nbs_agent.log"),
        )
        self.tela       = Tela()
        self._agendador: Agendador | None = None

    # ------------------------------------------------------------------ #
    #  INICIALIZAÇÃO                                                      #
    # ------------------------------------------------------------------ #

    def iniciar(self) -> bool:
        """
        Inicializa o agente.

        Configura o logger e exibe mensagem de início.
        O usuário deve estar logado no NBS antes de chamar este método.

        Returns:
            True sempre (mantido para compatibilidade futura com checagens).
        """
        log.info("=" * 50)
        log.info("  NBS Agent iniciando...")
        log.info("=" * 50)
        log.info("✓ Sistema pronto para automações.")
        return True

    def iniciar_agendador(self) -> None:
        """Inicia o agendador do relatório diário em thread daemon."""
        self._agendador = Agendador(callback_relatorio=self.relatorio_diario)
        self._agendador.iniciar()

    def encerrar(self) -> None:
        """Para o agendador e registra encerramento no log."""
        if self._agendador:
            self._agendador.parar()
        log.info("NBS Agent encerrado.")

    # ------------------------------------------------------------------ #
    #  AÇÕES                                                              #
    # ------------------------------------------------------------------ #

    def relatorio_diario(self) -> bool:
        """
        Gera o relatório de compras do dia anterior.

        Chamado automaticamente pelo agendador ou manualmente via menu.

        Returns:
            True se o relatório foi gerado com sucesso, False caso contrário.
        """
        log.info("Iniciando relatório diário...")
        ok = RelatorioCompras(self.tela).gerar_dia_anterior()
        if ok:
            print("  ✓ Relatório gerado com sucesso.")
        else:
            print("  ✗ Falha no relatório. Veja data/logs/ para detalhes.")
        return ok

    def lancar_fabrica(self) -> None:
        """
        Solicita números de nota ao usuário e executa lançamento de fábrica.

        Aceita uma ou mais notas separadas por vírgula.
        Cada nota passa pelos 25 passos do fluxo de fábrica.
        """
        notas = pedir_notas("fábrica")
        if not notas:
            return
        resultados = LancamentoFabrica(self.tela).lancar_notas(notas)
        self._exibir_resultados(resultados)

    def lancar_transferencia(self) -> None:
        """
        Solicita números de nota ao usuário e executa lançamento de transferência.

        Aceita uma ou mais notas separadas por vírgula.
        Cada nota passa pelos 16 passos do fluxo de transferência.
        """
        notas = pedir_notas("transferência")
        if not notas:
            return
        resultados = LancamentoTransferencia(self.tela).lancar_notas(notas)
        self._exibir_resultados(resultados)

    def lancar_entrada_cte(self) -> None:
        """
        Solicita quantidade de notas CT-e e executa o lançamento.

        Todas as notas do lote devem pertencer ao mesmo fornecedor.
        A primeira nota executa o fluxo completo; as demais reutilizam a tela.
        """
        try:
            qtd_str = input("\n  Quantas notas CT-e do mesmo fornecedor? ").strip()
            qtd = int(qtd_str)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            print("  ✗ Número inválido.")
            return
        resultados = EntradaCTE(self.tela).lancar(qtd)
        self._exibir_resultados(resultados)

    # ------------------------------------------------------------------ #
    #  HELPERS                                                            #
    # ------------------------------------------------------------------ #

    def _exibir_resultados(self, resultados: dict[str, bool]) -> None:
        """Imprime no terminal o resultado de cada nota processada."""
        print("\n  Resultado:")
        for nota, ok in resultados.items():
            icone = "✓" if ok else "✗"
            print(f"  {icone} Nota {nota}: {'OK' if ok else 'FALHOU'}")
