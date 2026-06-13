"""
__main__.py
-----------
Ponto de entrada do NBS Agent.

Uso:
  python __main__.py            → abre o sistema completo com menu
  python __main__.py relatorio  → gera relatório direto e fecha
  python __main__.py fabrica    → lança nota(s) direto e fecha
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agente import NBSAgent
from src.menu   import rodar_menu


def main():
    agente = NBSAgent()

    # ── Comando direto via argumento ──────────────────────────────────
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        agente.iniciar()

        if cmd == "relatorio":
            agente.relatorio_diario()
            input("\nPressione Enter para fechar...")

        elif cmd == "fabrica":
            agente.lancar_fabrica()
            input("\nPressione Enter para fechar...")

        elif cmd == "transferencia":
            agente.lancar_transferencia()
            input("\nPressione Enter para fechar...")

        else:
            print(f"Comando desconhecido: '{cmd}'")
            print("Disponíveis: relatorio | fabrica | transferencia")

        agente.encerrar()
        return

    # ── Modo normal: abre tudo e exibe o menu de setas ────────────────
    agente.iniciar()
    agente.iniciar_agendador()
    rodar_menu(agente)   # menu interativo com ↑ ↓ Enter


if __name__ == "__main__":
    main()
