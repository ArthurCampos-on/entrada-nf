"""
tela.py — controla mouse e teclado via PyAutoGUI + OpenCV.
Localiza elementos pelo visual (template matching) em vez de coordenadas fixas.

Melhorias aplicadas:
  [1] digitar() usa typewrite (tecla a tecla) — campos que rejeitam Ctrl+V funcionam
  [2] digitar_clipboard() disponível para textos com acentos via Ctrl+V
  [3] pedir_formulario() coleta dados campo a campo no terminal;
      em modo dashboard o controlador substitui este método por um form web
  [4] encontrar() usa grayscale — até 3× mais rápido que colorido
  [5] aguardar() exige N confirmações consecutivas — evita falsos positivos
  [6] _resolver_caminho() testa .png, .jpeg e .jpg

Uso básico:
    from src.tela import Tela

    tela = Tela()
    tela.clicar("botao_incluir")
    tela.digitar("123456")        # tecla a tecla (sem Ctrl+V)
    tela.tecla("enter")
    tela.aguardar("confirmacao")
"""

from __future__ import annotations

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
pyautogui.PAUSE = 0.05


class Tela:

    def __init__(self) -> None:
        self._imgs       = Path(cfg("imagens.pasta", "imagens"))
        self._conf       = cfg("imagens.confianca", 0.8)
        self._delay      = cfg("automacao.delay_acao", 0.6)
        self._timeout    = cfg("automacao.timeout_elemento", 15)
        self._tentativas = cfg("automacao.tentativas", 3)
        self._shots      = Path("data/screenshots")
        self._shots.mkdir(parents=True, exist_ok=True)

    # ── Localização ───────────────────────────────────────────────────

    def _resolver_caminho(self, nome: str) -> Path | None:
        for ext in (".png", ".jpeg", ".jpg"):
            p = self._imgs / f"{nome}{ext}"
            if p.exists():
                return p
        return None

    def encontrar(self, nome: str) -> tuple[int, int] | None:
        """[4] Grayscale: até 3× mais rápido. Suporta .png/.jpeg/.jpg."""
        caminho = self._resolver_caminho(nome)
        if caminho is None:
            log.warning(f"Imagem não encontrada: imagens/{nome}.[png|jpeg|jpg]")
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
        """[5] Exige N confirmações consecutivas. Lança TimeoutError se não aparecer."""
        fim  = time.time() + (timeout or self._timeout)
        conf = 0
        ultima_pos: tuple[int, int] | None = None

        while time.time() < fim:
            pos = self.encontrar(nome)
            if pos:
                conf += 1
                ultima_pos = pos
                if conf >= self._tentativas:
                    return ultima_pos
            else:
                conf = 0
                ultima_pos = None
            time.sleep(0.5)

        self.screenshot(f"timeout_{nome}")
        raise TimeoutError(f"'{nome}' não apareceu em {timeout or self._timeout}s")

    def existe(self, nome: str) -> bool:
        return self.encontrar(nome) is not None

    # ── Mouse ─────────────────────────────────────────────────────────

    def clicar(self, nome: str, timeout: int | None = None) -> None:
        x, y = self.aguardar(nome, timeout)
        time.sleep(self._delay)
        pyautogui.click(x, y)
        time.sleep(self._delay)

    def clique_direito_centro_tela(self) -> None:
        w, h = pyautogui.size()
        time.sleep(self._delay)
        pyautogui.rightClick(w // 2, h // 2)
        time.sleep(self._delay)

    # ── Teclado ───────────────────────────────────────────────────────

    def digitar(self, texto: str) -> None:
        """
        [1] Digita caractere por caractere (typewrite) — sem Ctrl+V.

        Resolve o bug onde campos do NBS rejeitavam colagem via clipboard,
        fazendo com que valores anteriores ou incorretos fossem inseridos.
        Funciona em qualquer campo que aceite teclado.

        Nota: não suporta acentos (ã, ç, etc.).
        Para texto com acentos use digitar_clipboard().
        """
        intervalo = 0.05 if str(texto).replace(".", "").replace("-", "").replace(",", "").isdigit() else 0.08
        time.sleep(self._delay)
        pyautogui.typewrite(str(texto), interval=intervalo)
        time.sleep(self._delay)

    def digitar_clipboard(self, texto: str) -> None:
        """
        [2] Cola via Ctrl+V (clipboard) — use para textos com acentos.

        Necessário quando o campo aceita caracteres especiais (ã, ç, é, ô…)
        que o typewrite não consegue digitar.
        Se o campo rejeitar Ctrl+V, use digitar() com texto sem acentos.
        """
        pyperclip.copy(str(texto))
        time.sleep(self._delay)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self._delay)

    def digitar_teclado(self, texto: str, intervalo: float = 0.08) -> None:
        """Alias retrocompatível para digitar(). Mantido para não quebrar código existente."""
        self.digitar(texto)

    def tecla(self, *teclas: str) -> None:
        time.sleep(0.2)
        pyautogui.hotkey(*teclas) if len(teclas) > 1 else pyautogui.press(teclas[0])
        time.sleep(0.3)

    def limpar_e_digitar(self, texto: str) -> None:
        """Seleciona tudo (Ctrl+A) e digita texto."""
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        self.digitar(texto)

    # ── Interação manual ──────────────────────────────────────────────

    def pausar_para_usuario(self, mensagem: str) -> bool:
        """Pausa e aguarda Y/N no terminal. Em modo web, substituído pelo controlador."""
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
        """Exibe opções numeradas e retorna a escolha. Em modo web, substituído pelo controlador."""
        chaves = list(opcoes.keys())
        print(f"\n{'='*52}")
        print(f"  ⏸  {titulo}")
        for k, desc in opcoes.items():
            print(f"  {k} → {desc}")
        print(f"{'='*52}")
        while True:
            r = input(f"  Escolha [{'/'.join(chaves)}]: ").strip()
            if r in opcoes:
                return r
            print(f"  Opção inválida. Use: {', '.join(chaves)}")

    def pedir_formulario(self, titulo: str, campos: list[dict]) -> dict:
        """
        [3] Coleta dados campo a campo no terminal.
        Em modo dashboard, o controlador substitui este método por um formulário web.

        Estrutura de cada campo (dict):
            nome          str  — chave no dicionário retornado
            label         str  — rótulo exibido ao usuário
            tipo          str  — "texto" | "bool" | "opcao"
            opcoes        list — valores válidos (só para tipo "opcao")
            validacao     str  — "cnpj" | "chave_cte" (validação especial)
            maxlen        int  — valida comprimento exato (ex: UF = 2)
            placeholder   str  — texto de exemplo exibido entre parênteses
            condicional_em str — nome do campo bool que habilita este campo
            secao         str  — título de seção (apenas visual)

        Returns:
            dict {nome: valor}. Campos condicionais não exibidos retornam None/False.
        """
        resultado: dict = {}
        print(f"\n{'═'*52}")
        print(f"  📋 {titulo}")
        print(f"{'═'*52}")

        ultima_secao: str | None = None

        for campo in campos:
            nome  = campo["nome"]
            label = campo["label"]
            tipo  = campo["tipo"]

            # Seção visual separadora
            secao = campo.get("secao")
            if secao and secao != ultima_secao:
                ultima_secao = secao
                print(f"\n  ─── {secao} ───")

            # Campo condicional: pula se o campo pai for falso/None
            cond_em = campo.get("condicional_em")
            if cond_em and not resultado.get(cond_em):
                resultado[nome] = False if tipo == "bool" else None
                continue

            ph_str = (f" (ex: {campo['placeholder']})" if campo.get("placeholder") else "")

            if tipo == "bool":
                while True:
                    r = input(f"  {label} [s/n]: ").strip().lower()
                    if r in ("s", "n"):
                        resultado[nome] = (r == "s")
                        break
                    print("  ⚠ Digite s ou n.")

            elif tipo == "opcao":
                opcoes = campo.get("opcoes", [])
                while True:
                    r = input(f"  {label} ({'/'.join(opcoes)}): ").strip()
                    if r in opcoes:
                        resultado[nome] = r
                        break
                    print(f"  ⚠ Inválido. Opções: {', '.join(opcoes)}")

            elif campo.get("validacao") == "cnpj":
                while True:
                    r = input(f"  {label}{ph_str}: ").strip()
                    digits = r.replace(".", "").replace("/", "").replace("-", "")
                    if len(digits) == 14 and digits.isdigit():
                        resultado[nome] = r
                        break
                    print("  ⚠ CNPJ inválido. Digite 14 dígitos.")

            elif campo.get("validacao") == "chave_cte":
                while True:
                    r = input(f"  {label}: ").strip()
                    if len(r) == 44 and r.isdigit():
                        resultado[nome] = r
                        break
                    print(f"  ⚠ Chave inválida ({len(r)} dígitos). Digite exatamente 44 números.")

            elif campo.get("maxlen"):
                ml = campo["maxlen"]
                while True:
                    r = input(f"  {label}{ph_str}: ").strip().upper()
                    if r.isalpha() and len(r) == ml:
                        resultado[nome] = r
                        break
                    print(f"  ⚠ Digite exatamente {ml} letras.")

            else:
                resultado[nome] = input(f"  {label}{ph_str}: ").strip()

        return resultado

    # ── Utilitários ───────────────────────────────────────────────────

    def esperar(self, segundos: float) -> None:
        time.sleep(segundos)

    def screenshot(self, nome: str = "tela") -> Path:
        path = self._shots / f"{nome}_{int(time.time())}.png"
        ImageGrab.grab().save(str(path))
        log.debug(f"Screenshot salvo: {path}")
        return path
