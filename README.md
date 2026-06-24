# NBS Agent

Automação do sistema NBS para a empresa **Duna - Tubarão**.

Exibe um **menu no terminal** controlado pelas setas do teclado.
Às **8h todo dia** o relatório diário roda sozinho sem nenhuma ação sua.

> ✅ O usuário já deve estar **logado no NBS** (Cloud Service + NBS Shortcut)
> antes de iniciar o agente. O login não é automatizado.

---

## Como funciona

O NBS roda dentro de um **canvas RDP** no browser — não tem HTML clicável.
Por isso o sistema usa duas tecnologias em conjunto:

| Etapa | Tecnologia | Por quê |
|---|---|---|
| Localizar botões e campos | OpenCV (template matching) | O NBS é um canvas — só pixels |
| Clicar e digitar | PyAutoGUI | Simula mouse e teclado |

O OpenCV compara pequenas **imagens de referência** (recortes salvos em `imagens/`)
com o que está na tela, então funciona em qualquer resolução.

---

## Estrutura do projeto

```
nbs-agent/
├── __main__.py              ← entrada: python __main__.py
├── requirements.txt
├── config/
│   └── settings.yaml        ← configurações
├── imagens/                 ← recortes dos botões
├── data/
│   ├── logs/                ← log de execução
│   └── screenshots/         ← capturas salvas em erros
├── src/
│   ├── agente.py            ← orquestrador principal
│   ├── menu.py              ← menu interativo (↑ ↓, cross-platform)
│   ├── tela.py              ← PyAutoGUI + OpenCV (mouse, teclado, template matching)
│   ├── constantes.py        ← nomes canônicos de imagens e constantes globais
│   ├── mapeamento_imagens.py← fonte de verdade de todos os arquivos de imagem
│   ├── config.py            ← lê e valida settings.yaml
│   ├── logger.py            ← logs coloridos com rotação automática
│   ├── agendador.py         ← disparo automático do relatório
│   ├── rpa_relatorio.py     ← 14 passos do relatório diário
│   ├── rpa_fabrica.py       ← 25 passos do lançamento de fábrica
│   ├── rpa_transferencia.py ← 16 passos do lançamento de transferência
│   └── rpa_entrada_cte.py   ← fluxo CT-e (CTE1 + CTE2)
└── scripts/
    └── setup.py             ← instala dependências e exibe checklist
```

---

## Setup (faça uma vez só)

### 1. Instalar dependências

```bash
python scripts/setup.py
```

Instala: `pyautogui`, `opencv-python`, `Pillow`, `pyyaml`, `loguru`, `pyperclip`.

### 2. Configurar settings.yaml

Edite `config/settings.yaml` com os valores do seu ambiente:

```yaml
agendador:
  horario_diario: "08:00"

empresa:
  nome_filtro:   "Duna"
  nome_completo: "Duna Tubarão"

imagens:
  pasta:     "imagens"
  confianca: 0.85

automacao:
  delay_acao:        0.6
  timeout_elemento:  15
  tentativas:        3
```

### 3. Verificar as imagens

Confirme que as imagens de referência estão presentes:

```bash
python src/mapeamento_imagens.py
```

Se alguma faltar, recorte com **Win+Shift+S** e salve em `imagens/`
com o nome exato listado em [IMAGENS.md](IMAGENS.md).

---

## Como usar

```bash
python __main__.py
```

O NBS já deve estar **aberto e visível no monitor principal**. Após o comando
será exibido o menu no terminal:

```
╔══════════════════════════════════╗
║           NBS Agent              ║
╠══════════════════════════════════╣
║  →  Relatório diário             ║
║     Fábrica                      ║
║     Transferência                ║
║     Entrada CT-e                 ║
║     Status                       ║
║     Sair                         ║
╠══════════════════════════════════╣
║  ↑ ↓ navegar   Enter confirmar   ║
╚══════════════════════════════════╝
```

O menu usa **setas do teclado** — sem digitar comandos, sem janela extra.

---

## Opções do menu

| Item | O que faz |
|---|---|
| Relatório diário | Gera o relatório de compras do dia anterior e imprime |
| Fábrica | Pergunta o(s) número(s) de nota e executa lançamento |
| Transferência | Pergunta o(s) número(s) de nota e executa lançamento |
| Entrada CT-e | Pergunta quantidade de notas e executa lançamento CT-e |
| Status | Mostra quando vai rodar o próximo relatório automático |
| Sair | Encerra o agente |

### Lançamento de notas (Fábrica e Transferência)

Ao selecionar Fábrica ou Transferência, o sistema pergunta:

```
  Nota(s): _
```

- **Uma nota:** `123456`
- **Várias notas:** `123456, 789012, 345678`

O sistema lança uma por uma. Em alguns pontos haverá **pausas manuais** —
o terminal exibe uma mensagem e aguarda `y` para continuar ou `n` para
cancelar aquela nota.

---

## Modo de comando direto

Para rodar uma ação sem abrir o menu:

```bash
python __main__.py relatorio
python __main__.py fabrica
python __main__.py transferencia
python __main__.py entrada-cte
```

---

## Relatório automático das 8h

Basta deixar o programa rodando. Todo dia às 8h o relatório do dia
anterior é gerado e impresso automaticamente.

Para mudar o horário, edite `config/settings.yaml`:

```yaml
agendador:
  horario_diario: "08:00"
```

---

## Ajustes para PC lento

Se a automação estiver clicando rápido demais, aumente em `config/settings.yaml`:

```yaml
automacao:
  delay_acao:       0.8   # pausa entre ações em segundos (padrão 0.6)
  timeout_elemento: 20    # tempo máximo esperando um elemento (padrão 15)

imagens:
  confianca: 0.75         # diminua se não encontrar botões (padrão 0.85)
```

---

## Diagnóstico de erros

Quando algo falha, o sistema salva um screenshot em `data/screenshots/`
e registra o erro em `data/logs/nbs_agent.log`.

Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para os problemas mais comuns.

---

## Documentação

| Documento | Conteúdo |
|---|---|
| [COMO_USAR.md](COMO_USAR.md) | Guia passo a passo para o usuário final |
| [IMAGENS.md](IMAGENS.md) | Tabela completa de imagens e como recapturá-las |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Visão técnica: fluxo, módulos e classe Tela |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problemas comuns e soluções |
