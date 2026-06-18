# NBS Agent — Arquitetura

## Visão geral

```
python __main__.py
       │
       ▼
  NBSAgent (agente.py)
  ├── Tela (tela.py)          ← PyAutoGUI + OpenCV
  ├── Agendador (agendador.py)← thread daemon, dispara às 8h
  └── menu (menu.py)          ← loop interativo ↑ ↓ Enter
            │
            ├── relatorio_diario()  → RelatorioCompras.gerar_dia_anterior()
            ├── lancar_fabrica()    → LancamentoFabrica.lancar_notas()
            ├── lancar_transferencia() → LancamentoTransferencia.lancar_notas()
            └── lancar_entrada_cte() → EntradaCTE.lancar()
```

---

## As três tecnologias

### 1. PyAutoGUI — controle de mouse e teclado

Move o cursor, clica, pressiona teclas e digita texto.

```python
pyautogui.click(x, y)           # clica em coordenada
pyautogui.press("enter")        # pressiona tecla
pyautogui.hotkey("ctrl", "v")   # atalho de teclado
```

**Ponto de atenção:** PyAutoGUI usa coordenadas absolutas de pixel.
Por isso o NBS precisa estar no monitor principal e sem sobreposição.

### 2. OpenCV — template matching (localizar botões)

Em vez de coordenadas fixas (que mudariam com qualquer redimensionamento),
o sistema localiza botões pelo visual: compara um recorte salvo contra
a tela atual e retorna as coordenadas do melhor match.

```
tela atual (screenshot)         recorte salvo (botao_incluir.png)
┌─────────────────────────┐     ┌────────┐
│  ███████████████████    │     │Incluir │
│  █ Incluir █  ...       │ ◄── └────────┘
│  ███████████████████    │     confiança: 0.8
└─────────────────────────┘
         ↓
    (x=342, y=187)
```

A confiança mínima é configurável em `settings.yaml → imagens.confianca`.

### 3. Pyperclip — digitação via clipboard

Textos com acentos (ã, ç, é) não chegam corretamente via
`pyautogui.typewrite()`. A solução é copiar o texto para a área
de transferência e colar com `Ctrl+V`:

```python
pyperclip.copy("São Paulo")
pyautogui.hotkey("ctrl", "v")
```

---

## Fluxo de execução de um RPA

```
agente.lancar_fabrica()
  │
  ├─ menu.pedir_notas()        → coleta ["123456", "789012"] do terminal
  │
  └─ LancamentoFabrica(tela).lancar_notas(notas)
       │
       └─ para cada nota:
            _lancar_uma_nota(numero)
              │
              ├─ tela.clicar("botao_incluir")
              │     └─ tela.aguardar("botao_incluir")  ← OpenCV procura na tela
              │           └─ tela.encontrar()           ← matchTemplate com confiança
              │                     └─ pyautogui.click(x, y)
              │
              ├─ tela.digitar(numero)
              │     └─ pyperclip.copy() + Ctrl+V
              │
              ├─ tela.pedir_opcao(...)    ← pausa manual no terminal
              │
              └─ (continua pelos 25 passos)
```

---

## Estrutura dos RPAs

Cada RPA segue o mesmo padrão:

```python
class LancamentoXxx:
    def __init__(self, tela: Tela) -> None: ...

    def lancar_notas(self, notas: list[str]) -> dict[str, bool]:
        """Ponto de entrada público. Retorna {nota: True/False}."""
        ...

    def _lancar_uma_nota(self, numero: str) -> bool:
        """Orquestra os passos, captura erros, salva screenshot."""
        try:
            self._passo_1_...()
            self._passo_2_...()
            ...
            return True
        except (TimeoutError, Exception) as e:
            log.error(...)
            self.tela.screenshot(...)
            return False

    def _passo_N_nome(self) -> None:
        """Cada método = um passo numerado do fluxo."""
        ...
```

---

## Classe Tela

Interface única para todas as interações com a tela:

| Método | O que faz |
|---|---|
| `clicar(nome)` | Aguarda elemento aparecer e clica |
| `aguardar(nome, timeout)` | Espera N confirmações consecutivas antes de aceitar |
| `encontrar(nome)` | Procura imagem na tela, retorna (x,y) ou None |
| `existe(nome)` | True se imagem visível agora |
| `digitar(texto)` | Cola via clipboard (suporta acentos) |
| `tecla(*teclas)` | Pressiona tecla(s) |
| `limpar_e_digitar(texto)` | Ctrl+A + digitar |
| `esperar(segundos)` | Pausa simples |
| `screenshot(nome)` | Salva PNG em data/screenshots/ |
| `pausar_para_usuario(msg)` | Pausa e aguarda Y/N no terminal |
| `pedir_opcao(titulo, opcoes)` | Menu numerado no terminal |

---

## Validação de imagens

```bash
python src/mapeamento_imagens.py           # verifica arquivos no disco
python src/mapeamento_imagens.py --listar  # lista tudo com descrição
```

O `mapeamento_imagens.py` é a fonte de verdade: toda imagem usada
pelos RPAs deve ter uma entrada com o mesmo nome que o arquivo em `imagens/`.

---

## Agendador

```
Thread daemon (background)
  │
  └─ _loop()
       ├─ acorda a cada ~60 segundos (no próximo minuto inteiro)
       ├─ compara strftime("%H:%M") com horario_diario
       └─ se igual E ainda não rodou hoje → chama callback_relatorio()
```

O agendador dorme até o próximo minuto inteiro em vez de polling fixo,
então o disparo ocorre dentro de ±1 segundo do horário configurado.
