"""agendador.py — dispara relatório diário no horário configurado."""
import threading, time
from datetime import datetime
from src.config import cfg
from src.logger import log

class Agendador:
    def __init__(self, callback_relatorio):
        self._cb       = callback_relatorio
        self._horario  = cfg("agendador.horario_diario", "08:00")
        self._rodando  = False
        self._ultimo   = None

    def iniciar(self):
        self._rodando = True
        threading.Thread(target=self._loop, daemon=True).start()
        log.info(f"⏰ Agendador iniciado — relatório às {self._horario}")

    def parar(self):
        self._rodando = False

    def proximo_disparo(self) -> str:
        from datetime import timedelta
        agora = datetime.now()
        h, m  = self._horario.split(":")
        prox  = agora.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
        if prox <= agora:
            prox += timedelta(days=1)
        diff = prox - agora
        return f"{self._horario} (em {int(diff.total_seconds()//3600)}h {int((diff.total_seconds()%3600)//60)}min)"

    def _loop(self):
        while self._rodando:
            agora = datetime.now()
            if agora.strftime("%H:%M") == self._horario and agora.date() != self._ultimo:
                log.info(f"⏰ Disparando relatório automático...")
                try:
                    self._cb()
                except Exception as e:
                    log.error(f"Erro no relatório automático: {e}")
                self._ultimo = agora.date()
            time.sleep(30)
