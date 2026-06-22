"""
menu.py — Menu interativo com setas ↑ ↓ no terminal. Zero dependências extras.

Compatível com Windows, Linux e macOS.
"""
import os

# ─────────────────────────────────────────────────────────────────────────────
#  Leitura de tecla — cross-platform
# ─────────────────────────────────────────────────────────────────────────────

try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    import tty       # type: ignore[import]
    import termios   # type: ignore[import]
    _WINDOWS = False


def _tecla_windows() -> str:
    """Lê uma tecla no Windows via msvcrt."""
    while True:
        ch = msvcrt.getch()

        if ch in (b'\x00', b'\xe0'):
            ch = msvcrt.getch()
            mapa = {
                b'H': "cima",
                b'P': "baixo",
                b'K': "esquerda",
                b'M': "direita",
                b'G': "home",
                b'O': "end",
                b'I': "pageup",
                b'Q': "pagedown",
            }
            return mapa.get(ch, "")

        if ch == b'\r':
            return "enter"
        if ch == b'\x1b':
            return "esc"
        if ch == b'\x03':
            raise KeyboardInterrupt

        return ch.decode("utf-8", errors="ignore")


def _tecla_unix() -> str:
    """Lê uma tecla no Linux/macOS via termios."""
    fd = 0  # stdin
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = os.read(fd, 1)

        if ch == b'\x1b':
            seq = os.read(fd, 2)
            mapa = {
                b'[A': "cima",
                b'[B': "baixo",
                b'[D': "esquerda",
                b'[C': "direita",
                b'[H': "home",
                b'[F': "end",
            }
            return mapa.get(seq, "esc")

        if ch == b'\r' or ch == b'\n':
            return "enter"
        if ch == b'\x03':
            raise KeyboardInterrupt

        return ch.decode("utf-8", errors="ignore")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def tecla() -> str:
    """Lê uma tecla especial ou caractere do teclado (cross-platform)."""
    if _WINDOWS:
        return _tecla_windows()
    return _tecla_unix()


# ─────────────────────────────────────────────────────────────────────────────
#  Menu visual
# ─────────────────────────────────────────────────────────────────────────────

ITENS = [
    "Relatório diário",
    "Fábrica",
    "Transferência",
    "Entrada CT-e",
    "Status",
    "Sair",
]


def _desenhar(itens: list[str], sel: int, agendador=None) -> None:
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


def rodar_menu(agente) -> None:
    """Exibe o menu interativo e despacha ações ao agente."""
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
            if escolha == "Sair":
                break
            elif escolha == "Relatório diário":
                print("  Gerando relatório...\n")
                agente.relatorio_diario()
            elif escolha == "Fábrica":
                agente.lancar_fabrica()
            elif escolha == "Transferência":
                agente.lancar_transferencia()
            elif escolha == "Entrada CT-e":
                agente.lancar_entrada_cte()
            elif escolha == "Status":
                if agente._agendador:
                    print(f"  ⏰ {agente._agendador.proximo_disparo()}")
            input("\n  Enter para voltar ao menu...")
        elif t.lower() == "q":
            break

    agente.encerrar()
    os.system("cls" if os.name == "nt" else "clear")
    print("Até mais!")


def pedir_notas(tipo: str) -> list[str]:
    """Solicita ao usuário uma ou mais notas separadas por vírgula."""
    print(f"\n  Nota(s) de {tipo}  (ex: 123456  ou  123456, 789012)")
    entrada = input("  Nota(s): ").strip()
    if not entrada:
        return []
    return [n.strip() for n in entrada.split(",") if n.strip()]
