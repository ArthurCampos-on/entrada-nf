"""
tela.py — controla mouse e teclado via PyAutoGUI + OpenCV.
Localiza elementos pelo visual (template matching) em vez de coordenadas fixas.
"""

import time
from pathlib import Path

import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab

from src.config import cfg
from src.logger import log

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


class Tela:

    def __init__(self):
        self._imgs     = Path(cfg("imagens.pasta", "imagens"))
        self._conf     = cfg("imagens.confianca", 0.8)
        self._delay    = cfg("automacao.delay_acao", 0.6)
        self._timeout  = cfg("automacao.timeout_elemento", 15)
        self._shots    = Path("data/screenshots")
        self._shots.mkdir(parents=True, exist_ok=True)

    # ── Localização ───────────────────────────────────────────────────

    def encontrar(self, nome: str) -> tuple[int, int] | None:
        """Procura imagem na tela. Retorna (x, y) do centro ou None."""
        caminho = self._imgs / f"{nome}.png"
        if not caminho.exists():
            log.warning(f"Imagem não encontrada: {caminho}")
            return None

        tela = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
        tmpl = cv2.imread(str(caminho))
        if tmpl is None:
            log.error(f"Não foi possível ler: {caminho}")
            return None

        h, w = tmpl.shape[:2]
        res  = cv2.matchTemplate(tela, tmpl, cv2.TM_CCOEFF_NORMED)
        _, conf, _, pos = cv2.minMaxLoc(res)

        if conf < self._conf:
            return None

        return pos[0] + w // 2, pos[1] + h // 2

    def aguardar(self, nome: str, timeout: int | None = None) -> tuple[int, int]:
        """Aguarda elemento aparecer. Lança TimeoutError se não encontrar."""
        fim = time.time() + (timeout or self._timeout)
        while time.time() < fim:
            pos = self.encontrar(nome)
            if pos:
                return pos
            time.sleep(0.5)
        self.screenshot(f"timeout_{nome}")
        raise TimeoutError(f"'{nome}' não apareceu em {timeout or self._timeout}s")

    def existe(self, nome: str) -> bool:
        return self.encontrar(nome) is not None

    # ── Mouse ─────────────────────────────────────────────────────────

    def clicar(self, nome: str, timeout: int | None = None):
        x, y = self.aguardar(nome, timeout)
        time.sleep(self._delay)
        pyautogui.click(x, y)
        time.sleep(self._delay)

    def clique_direito_centro_tela(self):
        w, h = pyautogui.size()
        time.sleep(self._delay)
        pyautogui.rightClick(w // 2, h // 2)
        time.sleep(self._delay)

    # ── Teclado ───────────────────────────────────────────────────────

    def digitar(self, texto: str):
        time.sleep(self._delay)
        pyautogui.write(texto, interval=0.05)
        time.sleep(self._delay)

    def tecla(self, *teclas: str):
        time.sleep(0.2)
        pyautogui.hotkey(*teclas) if len(teclas) > 1 else pyautogui.press(teclas[0])
        time.sleep(0.3)

    def limpar_e_digitar(self, texto: str):
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        self.digitar(texto)

    # ── Utilitários ───────────────────────────────────────────────────

    def esperar(self, segundos: float):
        time.sleep(segundos)

    def screenshot(self, nome: str = "tela") -> Path:
        path = self._shots / f"{nome}_{int(time.time())}.png"
        ImageGrab.grab().save(str(path))
        return path

    def pausar_para_usuario(self, mensagem: str) -> bool:
        """Pausa a automação e pede Y/N ao usuário."""
        print(f"\n{'='*50}")
        print(f"  ⏸  PAUSA MANUAL")
        print(f"  {mensagem}")
        print(f"{'='*50}")
        while True:
            r = input("  Continuar? [y/n]: ").strip().lower()
            if r == "y": return True
            if r == "n": return False
