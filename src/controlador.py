"""
controlador.py
--------------
Executa RPAs em background thread, permitindo controle via dashboard web.

Fluxo:
  1. Dashboard envia POST /api/executar com tipo + notas
  2. ControladorRPA inicia thread e substitui pedir_opcao/pausar da tela
  3. Quando automação pausa (aguarda input), seta acao_pendente
  4. Dashboard detecta via GET /api/estado e mostra dialog no celular
  5. Usuário responde → POST /api/responder → thread continua
  6. Logs em tempo real via polling GET /api/estado
"""

import logging
import threading
from datetime import datetime
from typing import Optional


class _CapturadorLog(logging.Handler):
    """Intercepta logs do agente e os repassa ao controlador."""

    def __init__(self, ctrl: "ControladorRPA") -> None:
        super().__init__()
        self._ctrl = ctrl
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelname in {"DEBUG"}:
            return
        self._ctrl._log(record.levelname, self.format(record))


class ControladorRPA:
    """
    Gerencia execução de RPAs em thread separada.

    Atributos públicos usados pelo DashboardServer:
        status          "idle" | "running" | "paused" | "error"
        acao_pendente   None  | dict com titulo e opcoes (quando pausado)
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
        self._evento = threading.Event()
        self._resposta: Optional[str] = None

        self._thread: Optional[threading.Thread] = None

        # Captura logs do agente para exibir no dashboard
        self._handler = _CapturadorLog(self)
        logging.getLogger("nbs_agent").addHandler(self._handler)

    # ── API pública ───────────────────────────────────────────────────

    def executar(
        self,
        tipo: str,
        notas: Optional[list[str]] = None,
        quantidade: Optional[int] = None,
    ) -> tuple[bool, str]:
        """
        Inicia um RPA em background thread.

        Returns:
            (True, "")        → iniciou com sucesso
            (False, "motivo") → não pôde iniciar
        """
        with self._lock:
            if self.status in ("running", "paused"):
                return False, f"Já há uma execução em andamento: {self.tipo_atual}"

        self.logs = []
        self.status = "running"
        self.tipo_atual = tipo
        self.iniciado_em = datetime.now().strftime("%H:%M:%S")
        self.acao_pendente = None

        self._thread = threading.Thread(
            target=self._run,
            args=(tipo, notas, quantidade),
            daemon=True,
        )
        self._thread.start()
        return True, ""

    def responder(self, valor: str) -> bool:
        """Responde a uma pausa manual pendente. Retorna True se havia ação."""
        if not self.acao_pendente:
            return False
        self._resposta = valor
        self._evento.set()
        return True

    def get_estado(self) -> dict:
        """Estado serializado para o frontend."""
        return {
            "status": self.status,
            "tipo": self.tipo_atual,
            "iniciado_em": self.iniciado_em,
            "logs": self.logs[-150:],
            "acao_pendente": self.acao_pendente,
        }

    # ── Thread de execução ────────────────────────────────────────────

    def _run(self, tipo: str, notas, quantidade) -> None:
        tela = self.agente.tela

        # Intercepta as pausas manuais para resposta via web
        orig_pedir  = tela.pedir_opcao
        orig_pausar = tela.pausar_para_usuario
        tela.pedir_opcao         = self._pedir_opcao_web
        tela.pausar_para_usuario = self._pausar_web

        try:
            self._log("INFO", f"▶ Iniciando {tipo}...")

            if tipo == "relatorio":
                from src.rpa_relatorio import RelatorioCompras
                ok = RelatorioCompras(tela).gerar_dia_anterior()
                self._log(
                    "SUCCESS" if ok else "ERROR",
                    "✓ Relatório gerado com sucesso." if ok else "✗ Falha no relatório.",
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
                self._log("ERROR", f"✗ Tipo desconhecido: {tipo}")

            self.status = "idle"
            self._log("SUCCESS", "✓ Execução finalizada.")

        except Exception as e:
            self._log("ERROR", f"✗ Erro inesperado: {e}")
            self.status = "error"

        finally:
            tela.pedir_opcao         = orig_pedir
            tela.pausar_para_usuario = orig_pausar
            self.acao_pendente       = None
            self.tipo_atual          = None

    # ── Interceptores de pausa ────────────────────────────────────────

    def _pedir_opcao_web(self, titulo: str, opcoes: dict) -> str:
        """
        Substitui tela.pedir_opcao() durante execução web.
        Seta acao_pendente, bloqueia a thread e aguarda resposta do dashboard.
        """
        self.acao_pendente = {
            "tipo": "opcao",
            "titulo": titulo,
            "opcoes": [{"chave": k, "descricao": v} for k, v in opcoes.items()],
        }
        self.status = "paused"
        self._log("PAUSE", f"⏸  Aguardando resposta: {titulo}")
        self._evento.clear()
        self._evento.wait(timeout=600)   # espera até 10 min
        self.status = "running"
        self.acao_pendente = None
        return self._resposta or list(opcoes.keys())[0]

    def _pausar_web(self, mensagem: str) -> bool:
        """Substitui tela.pausar_para_usuario() durante execução web."""
        self.acao_pendente = {
            "tipo": "confirmacao",
            "titulo": mensagem,
            "opcoes": [
                {"chave": "y", "descricao": "✓  Continuar"},
                {"chave": "n", "descricao": "✗  Cancelar"},
            ],
        }
        self.status = "paused"
        self._log("PAUSE", "⏸  Pausa manual — aguardando confirmação")
        self._evento.clear()
        self._evento.wait(timeout=600)
        self.status = "running"
        self.acao_pendente = None
        return (self._resposta or "y") == "y"

    # ── Helpers ───────────────────────────────────────────────────────

    def _log(self, nivel: str, msg: str) -> None:
        self.logs.append({
            "ts": datetime.now().strftime("%H:%M:%S"),
            "nivel": nivel,
            "msg": msg,
        })
        if len(self.logs) > self.MAX_LOGS:
            self.logs.pop(0)

    def _logar_resultados(self, resultados: dict) -> None:
        for nota, ok in resultados.items():
            self._log(
                "SUCCESS" if ok else "ERROR",
                f"{'✓' if ok else '✗'}  Nota {nota}: {'OK' if ok else 'FALHOU'}",
            )
