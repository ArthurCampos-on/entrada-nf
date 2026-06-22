"""
agendador.py — Dispara o relatório diário no horário configurado.

Em vez de dormir sempre 30 segundos (polling cego), o loop calcula
quantos segundos faltam para o próximo minuto inteiro e dorme esse tempo.
Resultado: CPU quase zero, e o disparo ocorre dentro de ±1 segundo
do horário configurado em vez de ±30 segundos.
"""

import threading
import time
from datetime import date, datetime, timedelta
from typing import Callable

from src.config import cfg
from src.logger import log


class Agendador:

    def __init__(self, callback_relatorio: Callable[[], None]) -> None:
        """
        Parâmetros
        ----------
        callback_relatorio:
            Função a chamar no horário agendado (ex: agente.relatorio_diario).
        """
        self._cb      = callback_relatorio
        self._horario = cfg("agendador.horario_diario", "08:00")
        self._rodando = False
        self._ultimo: date | None = None

    def iniciar(self) -> None:
        """Inicia o loop de agendamento em thread daemon."""
        self._rodando = True
        threading.Thread(target=self._loop, daemon=True).start()
        log.info(f"⏰ Agendador iniciado — relatório às {self._horario}")

    def parar(self) -> None:
        """Para o loop de agendamento."""
        self._rodando = False

    def proximo_disparo(self) -> str:
        """Retorna string legível com o horário e tempo restante até o próximo disparo."""
        agora = datetime.now()
        h, m  = self._horario.split(":")
        prox  = agora.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
        if prox <= agora:
            prox += timedelta(days=1)
        diff = prox - agora
        horas  = int(diff.total_seconds() // 3600)
        minutos = int((diff.total_seconds() % 3600) // 60)
        return f"{self._horario} (em {horas}h {minutos}min)"

    def _loop(self) -> None:
        """
        Loop principal do agendador.

        Dorme até o próximo minuto inteiro em vez de 30 s fixos,
        garantindo disparo dentro de ±1 s do horário com CPU mínima.
        """
        while self._rodando:
            agora = datetime.now()

            # Verifica se é hora de disparar
            if agora.strftime("%H:%M") == self._horario and agora.date() != self._ultimo:
                log.info("⏰ Disparando relatório automático...")
                try:
                    self._cb()
                except Exception as e:
                    log.error(f"Erro no relatório automático: {e}")
                self._ultimo = agora.date()

            # Calcula tempo até o próximo minuto inteiro e dorme esse tanto.
            # Mínimo de 5 s para não travar se o relógio estiver no segundo 0.
            segundos_ate_proximo_minuto = 60 - agora.second
            time.sleep(max(segundos_ate_proximo_minuto, 5))
