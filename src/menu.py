"""menu.py — menu interativo com setas ↑ ↓ no terminal. Zero dependências extras."""
import os
import msvcrt



def tecla() -> str:
    while True:
        ch = msvcrt.getch()

        # Teclas especiais
        if ch in (b'\x00', b'\xe0'):
            ch = msvcrt.getch()

            teclas = {
                b'H': "cima",
                b'P': "baixo",
                b'K': "esquerda",
                b'M': "direita",
                b'G': "home",
                b'O': "end",
                b'I': "pageup",
                b'Q': "pagedown",
            }

            return teclas.get(ch, "")

        # Enter
        if ch == b'\r':
            return "enter"

        # ESC
        if ch == b'\x1b':
            return "esc"

        # Ctrl+C
        if ch == b'\x03':
            raise KeyboardInterrupt

        return ch.decode("utf-8", errors="ignore")

def _desenhar(itens, sel, agendador=None):
    os.system("cls" if os.name == "nt" else "clear")
    larg = max(len(i) for i in itens) + 12
    print(f"╔{'═'*larg}╗")
    print(f"║{'NBS Agent'.center(larg)}║")
    print(f"╠{'═'*larg}╣")
    for i, item in enumerate(itens):
        linha = f"  →  {item}" if i == sel else f"     {item}"
        print(f"║{linha.ljust(larg)}║")
    print(f"╠{'═'*larg}╣")
    print(f"║{'↑ ↓ navegar   Enter confirmar   Q sair'.center(larg)}║")
    print(f"╚{'═'*larg}╝")
    if agendador:
        print(f"\n  ⏰ Próximo relatório: {agendador.proximo_disparo()}")

ITENS = ["Relatório diário", "Fábrica", "Transferência", "Status", "WhatsApp", "NBS", "Sair"]

def rodar_menu(agente):
    sel = 0
    while True:
        _desenhar(ITENS, sel, agente._agendador)
        t = tecla()
        if t == "cima":
            sel = (sel - 1) % len(ITENS)
        elif t == "baixo":
            sel = (sel + 1) % len(ITENS)
        elif t == "enter":
            escolha = ITENS[sel]
            os.system("cls" if os.name == "nt" else "clear")
            if escolha == "Sair": break
            elif escolha == "Relatório diário":
                print("  Gerando relatório...\n")
                agente.relatorio_diario()
            elif escolha == "Fábrica":       agente.lancar_fabrica()
            elif escolha == "Transferência": agente.lancar_transferencia()
            elif escolha == "Status":
                if agente._agendador:
                    print(f"  ⏰ {agente._agendador.proximo_disparo()}")
            elif escolha == "WhatsApp":
                agente.browser.focar_whatsapp()
                print("  → WhatsApp em foco.")
            elif escolha == "NBS":
                agente.browser.focar_nbs()
                print("  → NBS em foco.")
            input("\n  Enter para voltar ao menu...")
        elif t.lower() == "q":
            break
    agente.encerrar()
    os.system("cls" if os.name == "nt" else "clear")
    print("Até mais!")

def pedir_notas(tipo: str) -> list[str]:
    print(f"\n  Nota(s) de {tipo}  (ex: 123456  ou  123456, 789012)")
    entrada = input("  Nota(s): ").strip()
    if not entrada:
        return []
    return [n.strip() for n in entrada.split(",") if n.strip()]
