"""
tela.py — controla mouse e teclado via PyAutoGUI + OpenCV.
Localiza elementos pelo visual (template matching) em vez de coordenadas fixas.

Melhorias aplicadas:
  [1] digitar() usa pyperclip (clipboard) — suporta caracteres portugueses (ã, ç, é…)
  [2] encontrar() usa grayscale — até 3× mais rápido
  [3] aguardar() exige N confirmações consecutivas — evita falsos positivos por flicker
"""

import time
from pathlib import Path

import pyautogui
import pyperclip
import cv2
import numpy as np
from PIL import ImageGrab

from src.config import cfg
from src.logger import log

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


class Tela:

    def __init__(self):
        self._imgs       = Path(cfg("imagens.pasta", "imagens"))
        self._conf       = cfg("imagens.confianca", 0.8)
        self._delay      = cfg("automacao.delay_acao", 0.6)
        self._timeout    = cfg("automacao.timeout_elemento", 15)
        self._tentativas = cfg("automacao.tentativas", 3)   # [3]
        self._shots      = Path("data/screenshots")
        self._shots.mkdir(parents=True, exist_ok=True)

    # ── Localização ───────────────────────────────────────────────────

    def encontrar(self, nome: str) -> tuple[int, int] | None:
        """
        Procura imagem na tela. Retorna (x, y) do centro ou None.
        [2] Grayscale: 1 canal em vez de 3 — até 3× mais rápido.
        """
        caminho = self._imgs / f"{nome}.png"
        if not caminho.exists():
            log.warning(f"Imagem não encontrada: {caminho}")
            return None

        tela = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2GRAY)
        tmpl = cv2.imread(str(caminho), cv2.IMREAD_GRAYSCALE)
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
        """
        Aguarda elemento aparecer.
        [3] Exige N confirmações consecutivas antes de considerar válido.
        Lança TimeoutError se não aparecer dentro do timeout.
        """
        confirmacoes_necessarias = self._tentativas
        fim  = time.time() + (timeout or self._timeout)
        conf = 0
        ultima_pos: tuple[int, int] | None = None

        while time.time() < fim:
            pos = self.encontrar(nome)
            if pos:
                conf += 1
                ultima_pos = pos
                if conf >= confirmacoes_necessarias:
                    return ultima_pos
            else:
                conf       = 0
                ultima_pos = None
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
        """Clica com botão direito no centro geométrico da tela."""
        w, h = pyautogui.size()
        time.sleep(self._delay)
        pyautogui.rightClick(w // 2, h // 2)
        time.sleep(self._delay)

    # ── Teclado ───────────────────────────────────────────────────────

    def digitar(self, texto: str):
        """
        [1] Usa clipboard (pyperclip + Ctrl+V).
        Suporta qualquer caractere — ã, ç, é, ô, etc.
        """
        time.sleep(self._delay)
        pyperclip.copy(str(texto))
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self._delay)

    def tecla(self, *teclas: str):
        time.sleep(0.2)
        pyautogui.hotkey(*teclas) if len(teclas) > 1 else pyautogui.press(teclas[0])
        time.sleep(0.3)

    def limpar_e_digitar(self, texto: str):
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        self.digitar(texto)

    # ── Interação manual ──────────────────────────────────────────────

    def pausar_para_usuario(self, mensagem: str) -> bool:
        """
        Pausa a automação, exibe mensagem e aguarda Y/N no terminal.
        Retorna True para continuar, False para cancelar.
        """
        print(f"\n{'='*52}")
        print(f"  ⏸  PAUSA MANUAL")
        print(f"  {mensagem}")
        print(f"{'='*52}")
        while True:
            r = input("  Continuar? [y/n]: ").strip().lower()
            if r == "y":
                return True
            if r == "n":
                return False

    def pedir_opcao(self, titulo: str, opcoes: dict[str, str]) -> str:
        """
        Exibe opções numeradas no terminal e retorna a escolha do usuário.

        Exemplo:
            escolha = tela.pedir_opcao(
                "Cruzamento de pedidos",
                {"1": "Cruzar automaticamente",
                 "2": "Ir direto para Locações",
                 "3": "Pular esta nota"}
            )
        """
        chaves = list(opcoes.keys())
        print(f"\n{'='*52}")
        print(f"  ⏸  {titulo}")
        for k, desc in opcoes.items():
            print(f"  {k} → {desc}")
        print(f"{'='*52}")
        prompt = f"  Escolha [{'/'.join(chaves)}]: "
        while True:
            r = input(prompt).strip()
            if r in opcoes:
                return r
            print(f"  Opção inválida. Use: {', '.join(chaves)}")

    # ── Utilitários ───────────────────────────────────────────────────

    def esperar(self, segundos: float):
        time.sleep(segundos)

    def screenshot(self, nome: str = "tela") -> Path:
        path = self._shots / f"{nome}_{int(time.time())}.png"
        ImageGrab.grab().save(str(path))
        return path
