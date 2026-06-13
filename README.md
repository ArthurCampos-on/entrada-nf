# NBS Agent

Automação do sistema NBS para a empresa **Duna - Tubarão**.

Abre o Chrome com **aba NBS + aba WhatsApp Web**, faz login automático
e exibe um menu no terminal controlado pelas setas do teclado.
Às **8h todo dia** o relatório diário roda sozinho sem nenhuma ação sua.

---

## Como funciona

O NBS roda dentro de um **canvas RDP** no browser — não tem HTML clicável.
Por isso o sistema usa duas tecnologias em conjunto:

| Etapa | Tecnologia | Por quê |
|---|---|---|
| Login Cloud Service e WhatsApp | Selenium | Essa tela tem HTML normal |
| Tudo dentro do NBS | PyAutoGUI + OpenCV | O NBS é um canvas — só pixels |

O OpenCV localiza cada botão pelo visual (recortes de imagem que você salva
uma vez), então funciona em qualquer resolução.

---

## Estrutura do projeto

```
nbs-agent/
├── __main__.py              ← entrada: python __main__.py
├── requirements.txt
├── config/
│   └── settings.yaml        ← credenciais e configurações
├── imagens/                 ← recortes dos botões (63 já incluídos)
├── data/
│   ├── logs/                ← log de execução
│   └── screenshots/         ← capturas salvas em erros
├── src/
│   ├── agente.py            ← orquestrador principal
│   ├── menu.py              ← menu interativo com setas ↑ ↓
│   ├── browser.py           ← Chrome, login web, WhatsApp
│   ├── tela.py              ← PyAutoGUI, template matching
│   ├── rpa_login.py         ← login NBS Shortcut (canvas)
│   ├── rpa_relatorio.py     ← 14 passos do relatório diário
│   ├── rpa_fabrica.py       ← 24 passos do lançamento de fábrica
│   ├── rpa_transferencia.py ← 16 passos do lançamento de transferência
│   ├── agendador.py         ← disparo automático às 8h
│   ├── mapeamento_imagens.py← mapeia botões para arquivos de imagem
│   ├── config.py            ← lê settings.yaml
│   └── logger.py            ← logs com rotação automática
└── scripts/
    └── setup.py             ← instala dependências
```

---

## Setup (faça uma vez só)

### 1. Instalar dependências

```bash
python scripts/setup.py
```

Instala: `selenium`, `pyautogui`, `opencv-python`, `Pillow`, `pyyaml`,
`loguru`, `webdriver-manager`.

### 2. Configurar credenciais

Edite `config/settings.yaml`:

```yaml
nbs:
  url: "http://10.32.1.139:85/"
  cloud_usuario: "arthur.eugenio"   # login Cloud Service
  cloud_senha:   "SUA_SENHA"
  nbs_usuario:   "ARTHURE"          # login NBS Shortcut
  nbs_senha:     "4321"
```

### 3. Verificar as imagens

O projeto já vem com **63 imagens** extraídas e mapeadas automaticamente.
Para confirmar que cada imagem está correta visualmente, rode:

```bash
python src/mapeamento_imagens.py --visualizar
```

Isso abre cada imagem uma por uma para você confirmar.

Se alguma imagem estiver errada, recorte a correta com **Win+Shift+S**
e salve na pasta `imagens/` com o mesmo nome.

---

## Como usar

```bash
python __main__.py
```

Abre o Chrome com **duas abas** (NBS + WhatsApp Web), faz login automático
e exibe o menu no terminal:

```
╔══════════════════════════════════╗
║           NBS Agent              ║
╠══════════════════════════════════╣
║  →  Relatório diário             ║
║     Fábrica                      ║
║     Transferência                ║
║     Status                       ║
║     WhatsApp                     ║
║     NBS                          ║
║     Sair                         ║
╠══════════════════════════════════╣
║  ↑ ↓ navegar   Enter confirmar   ║
╚══════════════════════════════════╝
```

O menu usa **setas do teclado** — sem digitar comandos, sem janela extra,
zero consumo adicional de memória.

---

## Opções do menu

| Item | O que faz |
|---|---|
| Relatório diário | Gera o relatório de compras do dia anterior e imprime |
| Fábrica | Pergunta o(s) número(s) de nota e executa lançamento |
| Transferência | Pergunta o(s) número(s) de nota e executa lançamento |
| Status | Mostra quando vai rodar o próximo relatório automático |
| WhatsApp | Coloca o foco na aba do WhatsApp Web |
| NBS | Coloca o foco na aba do NBS |
| Sair | Fecha tudo e encerra |

### Lançamento de notas (Fábrica e Transferência)

Ao selecionar Fábrica ou Transferência, o sistema pergunta:

```
  Nota(s): _
```

- **Uma nota:** `123456`
- **Várias notas:** `123456, 789012, 345678`

O sistema detecta automaticamente quantas são pela vírgula e lança
uma por uma. Em alguns pontos haverá **pausas manuais** — o terminal
mostra uma mensagem e aguarda você digitar `y` para continuar ou `n`
para cancelar aquela nota.

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

## Modo de comando direto

Se quiser rodar uma ação sem abrir o menu:

```bash
python __main__.py relatorio
python __main__.py fabrica
python __main__.py transferencia
```

---

## Ajustes para PC lento

Se a automação estiver clicando rápido demais, aumente em
`config/settings.yaml`:

```yaml
automacao:
  delay_acao: 0.8        # pausa entre ações em segundos (padrão 0.6)
  timeout_elemento: 20   # tempo máximo esperando um elemento (padrão 15)

imagens:
  confianca: 0.75        # diminua se não encontrar botões (padrão 0.8)
```

---

## Fluxos automatizados

### Login (7 passos)
1. Abre `http://10.32.1.139:85/` no Chrome
2. Preenche usuário e senha no Cloud Service
3. Clica em Log on
4. Aguarda 8 segundos o sistema carregar
5. Preenche usuário no NBS Shortcut
6. Preenche senha
7. Clica em Confirmar

### Relatório diário (14 passos)
Seleciona empresa Duna Tubarão → preenche datas do dia anterior →
pesquisa → aba Nota → Imprimir Lista → Sim → Print → ícone impressora
→ Print no viewer → Ctrl+P → Enter.

### Fábrica (24 passos)
Incluir → Compra → Interface → digita nota → pesquisa →
⏸ pausa manual → aba CFOP → botão direito → Definir CFOP →
Tributados → OK → Aceitar → Cruzamento de Pedidos → seta direita →
Confirmar → OK → Recálculo → Locações → PRINCIPAL(PEÇAS) → SL →
Financeiro (60/60/1/Boleto) → Confirmar.

### Transferência (16 passos)
Incluir → Transferência → Interface → Interface de Saída →
Pesquisar → Aceitar → Confirmar → OK → Locações →
PRINCIPAL(PEÇAS) → SL → Sugestão → OK → Não → OK.

---

## Diagnóstico de erros

Quando algo falha o sistema salva um screenshot automaticamente em
`data/screenshots/` com o nome do erro. Os logs completos ficam em
`data/logs/nbs_agent.log`.

---

## O que ainda falta implementar

- **Entrada CTE** — fluxo ainda não documentado
- **Relatório de Rede** — fluxo ainda não documentado
