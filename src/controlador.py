"""
controlador.py
--------------
Executa RPAs em background thread, permitindo controle via dashboard web.

Fluxo:
  1. Dashboard envia POST /api/executar com tipo + notas
  2. ControladorRPA inicia thread e substitui métodos interativos da tela
  3. Quando automação pausa (aguarda input), seta acao_pendente
  4. Dashboard detecta via GET /api/estado e mostra dialog/form no browser
  5. Usuário responde → POST /api/responder → thread continua
  6. Usuário cancela → POST /api/cancelar → thread recebe OperacaoCancelada

Tipos de acao_pendente:
  opcao       — botões de seleção (ex: cruzar/pular)
  confirmacao — botão Sim/Não (ex: revisar e confirmar)
  formulario  — form com múltiplos campos (ex: dados da nota CT-e)

Cancelamento cooperativo:
  - tela.aguardar(), tela.esperar() e tela.digitar() são substituídos por
    versões que verificam _cancelando entre cada passo.
  - Se pausado aguardando input, cancelar() acorda a thread via _evento.set().
  - A thread levanta OperacaoCancelada, que é capturada em _run().
"""

from __future__ import annotations

import logging
import time
import threading
from datetime import datetime
from typing import Any, Optional


# ── Exceção de cancelamento ───────────────────────────────────────────────────

class OperacaoCancelada(Exception):
    """Levantada quando o usuário cancela a operação pelo dashboard."""


# ── Capturador de logs ────────────────────────────────────────────────────────

class _CapturadorLog(logging.Handler):
    """Intercepta logs do agente e os repassa ao controlador."""

    def __init__(self, ctrl: "ControladorRPA") -> None:
        super().__init__()
        self._ctrl = ctrl
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelname == "DEBUG":
            return
        self._ctrl._log(record.levelname, self.format(record))


# ── Controlador principal ─────────────────────────────────────────────────────

class ControladorRPA:
    """
    Gerencia execução de RPAs em thread separada.

    Atributos públicos usados pelo DashboardServer:
        status          "idle" | "running" | "paused" | "error" | "cancelado"
        acao_pendente   None | dict com tipo, titulo e dados (quando pausado)
        logs            lista de dicts {ts, nivel, msg}
    """

    MAX_LOGS = 300

    def __init__(self, agente) -> None:
        self.agente = agente
        self._lock = threading.Lock()

        self.status: str = "idle"
        self.tipo_atual: Optional[str] = None
        self.iniciado_em: Optional[str] = None
        self.logs: list[dict] = []

        self.acao_pendente: Optional[dict] = None
        self._evento     = threading.Event()
        self._resposta: Any = None       # str (opcao) ou dict (formulario)
        self._cancelando  = False        # sinaliza cancelamento à thread em curso

        self._thread: Optional[threading.Thread] = None

        self._handler = _CapturadorLog(self)
        logging.getLogger("nbs_agent").addHandler(self._handler)

    # ── API pública ───────────────────────────────────────────────────────────

    def executar(
        self,
        tipo: str,
        notas: Optional[list[str]] = None,
        quantidade: Optional[int] = None,
    ) -> tuple[bool, str]:
        with self._lock:
            if self.status in ("running", "paused"):
                return False, f"Já há uma execução em andamento: {self.tipo_atual}"

        self.logs        = []
        self.status      = "running"
        self.tipo_atual  = tipo
        self.iniciado_em = datetime.now().strftime("%H:%M:%S")
        self.acao_pendente = None
        self._cancelando   = False

        self._thread = threading.Thread(
            target=self._run,
            args=(tipo, notas, quantidade),
            daemon=True,
        )
        self._thread.start()
        return True, ""

    def cancelar(self) -> bool:
        """
        Cancela a operação em andamento.

        - Se rodando: sinaliza _cancelando; os métodos da tela vão levantar
          OperacaoCancelada na próxima instrução (aguardar/esperar/digitar).
        - Se pausado: além de sinalizar, acorda o evento para desbloquear a thread.
        - Retorna False se não há nada em execução.
        """
        if self.status not in ("running", "paused"):
            return False
        self._cancelando = True
        self._log("WARN", "⛔  Cancelamento solicitado pelo usuário")
        if self.status == "paused":
            # Acorda thread que aguarda input — ela vai ver _cancelando e parar
            self._resposta = None
            self._evento.set()
        return True

    def responder(self, valor: Any) -> bool:
        """
        Responde a uma pausa pendente.
          - str  → opcao ou confirmacao (ex: "y", "1")
          - dict → formulario (ex: {"numero": "12345", ...})
        """
        if not self.acao_pendente:
            return False
        self._resposta = valor
        self._evento.set()
        return True

    def get_estado(self) -> dict:
        return {
            "status":        self.status,
            "tipo":          self.tipo_atual,
            "iniciado_em":   self.iniciado_em,
            "logs":          self.logs[-150:],
            "acao_pendente": self.acao_pendente,
            "cancelando":    self._cancelando,
        }

    # ── Thread de execução ────────────────────────────────────────────────────

    def _run(self, tipo: str, notas, quantidade) -> None:
        tela = self.agente.tela

        # ── Guarda métodos originais ──────────────────────────────────────────
        orig_pedir      = tela.pedir_opcao
        orig_pausar     = tela.pausar_para_usuario
        orig_formulario = tela.pedir_formulario
        orig_aguardar   = tela.aguardar
        orig_esperar    = tela.esperar
        orig_digitar    = tela.digitar

        # ── Versões canceláveis dos métodos de tela ───────────────────────────
        def _checar():
            """Levanta OperacaoCancelada se o usuário cancelou."""
            if self._cancelando:
                raise OperacaoCancelada()

        def aguardar_cancelavel(nome, timeout=None):
            _checar()
            return orig_aguardar(nome, timeout)

        def esperar_cancelavel(segundos: float):
            """Dorme em fatias de 0.25 s verificando cancelamento a cada passo."""
            fim = time.time() + segundos
            while time.time() < fim:
                _checar()
                time.sleep(min(0.25, fim - time.time()))

        def digitar_cancelavel(texto):
            _checar()
            return orig_digitar(texto)

        # ── Substitui todos os métodos interativos ────────────────────────────
        tela.pedir_opcao         = self._pedir_opcao_web
        tela.pausar_para_usuario = self._pausar_web
        tela.pedir_formulario    = self._pedir_formulario_web
        tela.aguardar            = aguardar_cancelavel
        tela.esperar             = esperar_cancelavel
        tela.digitar             = digitar_cancelavel

        try:
            self._log("INFO", f"▶  Iniciando {tipo}…")

            if tipo == "relatorio":
                from src.rpa_relatorio import RelatorioCompras
                ok = RelatorioCompras(tela).gerar_dia_anterior()
                self._log(
                    "SUCCESS" if ok else "ERROR",
                    "✓  Relatório gerado." if ok else "✗  Falha no relatório.",
                )

            elif tipo == "fabrica":
                from src.rpa_fabrica import LancamentoFabrica
                resultados = LancamentoFabrica(tela).lancar_notas(notas or [])
                self._logar_resultados(resultados)

            elif tipo == "transferencia":
                from src.rpa_transferencia import LancamentoTransferencia
                resultados = LancamentoTransferencia(tela).lancar_notas(notas or [])
                self._logar_resultados(resultados)

            elif tipo == "entrada_cte":
                from src.rpa_entrada_cte import EntradaCTE
                resultados = EntradaCTE(tela).lancar(quantidade or 1)
                self._logar_resultados(resultados)

            else:
                self._log("ERROR", f"✗  Tipo desconhecido: {tipo}")

            self.status = "idle"
            self._log("SUCCESS", "✓  Execução finalizada.")

        except OperacaoCancelada:
            self._log("WARN", "⛔  Operação cancelada.")
            self.status = "cancelado"

        except Exception as exc:
            self._log("ERROR", f"✗  Erro inesperado: {exc}")
            self.status = "error"

        finally:
            # Restaura todos os métodos originais da tela
            tela.pedir_opcao         = orig_pedir
            tela.pausar_para_usuario = orig_pausar
            tela.pedir_formulario    = orig_formulario
            tela.aguardar            = orig_aguardar
            tela.esperar             = orig_esperar
            tela.digitar             = orig_digitar
            self.acao_pendente       = None
            self.tipo_atual          = None
            self._cancelando         = False

    # ── Interceptores de pausa ────────────────────────────────────────────────

    def _pedir_opcao_web(self, titulo: str, opcoes: dict) -> str:
        """Substitui tela.pedir_opcao() — exibe botões de opção no dashboard."""
        self.acao_pendente = {
            "tipo":   "opcao",
            "titulo": titulo,
            "opcoes": [{"chave": k, "descricao": v} for k, v in opcoes.items()],
        }
        resposta = self._aguardar_resposta(f"⏸   Aguardando seleção: {titulo}")
        return resposta or list(opcoes.keys())[0]

    def _pausar_web(self, mensagem: str) -> bool:
        """Substitui tela.pausar_para_usuario() — exibe confirmação no dashboard."""
        self.acao_pendente = {
            "tipo":   "confirmacao",
            "titulo": mensagem,
            "opcoes": [
                {"chave": "y", "descricao": "✓  Continuar"},
                {"chave": "n", "descricao": "✗  Não continuar"},
            ],
        }
        resposta = self._aguardar_resposta("⏸   Pausa — aguardando confirmação")
        return (resposta or "y") == "y"

    def _pedir_formulario_web(self, titulo: str, campos: list[dict]) -> dict:
        """Substitui tela.pedir_formulario() — exibe formulário no dashboard."""
        self.acao_pendente = {
            "tipo":   "formulario",
            "titulo": titulo,
            "campos": campos,
        }
        resposta = self._aguardar_resposta(f"⏸   Aguardando dados: {titulo}")
        return resposta if isinstance(resposta, dict) else {}

    def _aguardar_resposta(self, msg_log: str) -> Any:
        """
        Pausa a thread até o dashboard responder (ou o usuário cancelar).
        Lança OperacaoCancelada se _cancelando for True ao acordar.
        """
        self.status = "paused"
        self._log("PAUSE", msg_log)
        self._evento.clear()
        self._resposta = None
        self._evento.wait(timeout=600)    # aguarda até 10 min
        self.status = "running"
        self.acao_pendente = None
        if self._cancelando:
            raise OperacaoCancelada()
        return self._resposta

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _log(self, nivel: str, msg: str) -> None:
        self.logs.append({
            "ts":    datetime.now().strftime("%H:%M:%S"),
            "nivel": nivel,
            "msg":   msg,
        })
        if len(self.logs) > self.MAX_LOGS:
            self.logs.pop(0)

    def _logar_resultados(self, resultados: dict) -> None:
        for nota, ok in resultados.items():
            self._log(
                "SUCCESS" if ok else "ERROR",
                f"{'✓' if ok else '✗'}  Nota {nota}: {'OK' if ok else 'FALHOU'}",
            )
