"""
browser.py
----------
Interface Selenium para o Chrome — já aberto pelo usuário.

Este módulo não abre o Chrome (o usuário já o abre manualmente com NBS logado).
Funciona apenas para "focar" a janela do Chrome (trazer para frente) antes
das automações usarem PyAutoGUI para clickar em elementos da tela.
"""

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.config import cfg
from src.logger import log


class Browser:

    def __init__(self):
        self.driver        = None
        self._aba_nbs      = None
        self._aba_whatsapp = None

    # ------------------------------------------------------------------ #
    #  INICIALIZAÇÃO                                                      #
    # ------------------------------------------------------------------ #

    def iniciar(self):
        """Conecta ao Chrome já aberto (não abre nova janela)."""
        log.info("Conectando ao Chrome...")
        opts = Options()
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--start-maximized")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver   = webdriver.Chrome(service=service, options=opts)
        self._aba_nbs = self.driver.current_window_handle
        log.info("✓ Chrome conectado.")

    # ------------------------------------------------------------------ #
    #  WHATSAPP WEB                                                       #
    # ------------------------------------------------------------------ #

    def abrir_whatsapp(self):
        """Abre WhatsApp Web em segunda aba e volta foco para o NBS."""
        log.info("Abrindo WhatsApp Web em segunda aba...")
        self.driver.execute_script("window.open('');")
        self._aba_whatsapp = self.driver.window_handles[-1]
        self.driver.switch_to.window(self._aba_whatsapp)
        self.driver.get(cfg("whatsapp.url", "https://web.whatsapp.com"))
        log.info("WhatsApp Web aberto.")
        self.focar_nbs()

    # ------------------------------------------------------------------ #
    #  CONTROLE DE ABAS                                                   #
    # ------------------------------------------------------------------ #

    def focar_nbs(self):
        if self._aba_nbs:
            self.driver.switch_to.window(self._aba_nbs)

    def focar_whatsapp(self):
        if self._aba_whatsapp:
            self.driver.switch_to.window(self._aba_whatsapp)

    # ------------------------------------------------------------------ #
    #  ENCERRAMENTO                                                       #
    # ------------------------------------------------------------------ #

    def fechar(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            log.info("Chrome fechado.")

    def _salvar_screenshot(self, nome: str):
        try:
            Path("data/screenshots").mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(
                f"data/screenshots/{nome}_{int(time.time())}.png"
            )
        except Exception:
            pass
