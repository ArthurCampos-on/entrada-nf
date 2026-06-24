# NBS Agent — Como Usar

## 📋 Pré-requisitos

1. **Windows, Linux ou macOS** com Python 3.10+
2. **NBS aberto e logado** no monitor principal (Cloud Service + NBS Shortcut — feito manualmente)
3. Dependências instaladas: `python scripts/setup.py`

---

## 🚀 Execução

```bash
# Menu interativo
python __main__.py

# Comandos diretos (sem menu)
python __main__.py relatorio       # gera relatório do dia anterior
python __main__.py fabrica         # lança fábrica (vai perguntar notas)
python __main__.py transferencia   # lança transferência (vai perguntar notas)
python __main__.py entrada-cte     # lança CT-e (vai perguntar quantidade)
```

> **Importante:** o NBS já deve estar **aberto e visível no monitor principal** antes de executar.

---

## 📺 Menu Interativo

Ao executar `python __main__.py`, aparecerá um menu controlado pelas setas do teclado (↑ ↓):

```
╔════════════════════════════════════════╗
║           NBS Agent                    ║
╠════════════════════════════════════════╣
║  →  Relatório diário                   ║
║     Fábrica                            ║
║     Transferência                      ║
║     Entrada CT-e                       ║
║     Status                             ║
║     Sair                               ║
╠════════════════════════════════════════╣
║  ↑ ↓ navegar   Enter confirmar   Q sair║
╚════════════════════════════════════════╝
```

### Opções:
| Item | O que faz |
|---|---|
| **Relatório diário** | Gera e imprime o relatório de compras do dia anterior |
| **Fábrica** | Solicita notas e lança lançamentos de fábrica |
| **Transferência** | Solicita notas e lança lançamentos de transferência |
| **Entrada CT-e** | Solicita quantidade de notas e lança CT-e |
| **Status** | Mostra quando o próximo relatório será gerado automaticamente |
| **Sair** | Encerra o agente |

---

## ⚙️ Configuração

Edite `config/settings.yaml` para personalizar. Abaixo estão **todas as chaves válidas**:

```yaml
agendador:
  horario_diario: "08:00"      # horário do relatório automático diário

empresa:
  nome_filtro:   "Duna"        # texto digitado para filtrar a empresa
  nome_completo: "Duna Tubarão"

imagens:
  pasta:     "imagens"         # pasta das imagens de referência
  confianca: 0.85              # confiança para template matching (0–1)

automacao:
  delay_acao:       0.6        # pausa entre ações (segundos)
  timeout_elemento: 15         # tempo máximo esperando um elemento (segundos)
  tentativas:       3          # confirmações consecutivas para validar elemento

financeiro:
  entrada_dias:   60           # dias de entrada (boleto fábrica)
  intervalo_dias: 60           # intervalo entre parcelas
  total_parcelas: 1
  tipo_pagamento: "Boleto Bancario"

locacao:
  padrao:      "SL"
  tipo_fabrica: "PRINCIPAL(PEÇAS)"
  tipo_pecas:   "PRINCIPAL(PEÇAS)"

entrada_cte:
  faturamento_entrada_dias:   28   # dias de entrada CT-e
  faturamento_intervalo_dias: 28
  faturamento_parcelas:       1
  codigo_contabilizacao:     "40"  # código digitado na aba Contabilização

logging:
  nivel:   "INFO"              # DEBUG | INFO | WARNING | ERROR
  arquivo: "data/logs/nbs_agent.log"
```

> ⚠️ Não use chaves removidas em versões anteriores:
> `agendador.ativo`, `agendador.hora`, `agendador.fuso`,
> `whatsapp.url`, `automacao.atraso_minimo` — todas foram removidas.

---

## 📁 Estrutura

```
nbs-agent/
  __main__.py                 ← entrypoint (começa aqui)
  requirements.txt
  config/
    settings.yaml             ← configurações (edite aqui)
  src/
    agente.py                 ← orquestrador principal
    tela.py                   ← encontra e clica em imagens na tela
    menu.py                   ← menu interativo com setas (cross-platform)
    constantes.py             ← nomes canônicos de imagens e constantes
    mapeamento_imagens.py     ← fonte de verdade de todos os arquivos de imagem
    config.py                 ← lê e valida settings.yaml
    logger.py                 ← logs coloridos com rotação automática
    agendador.py              ← disparo automático do relatório
    rpa_relatorio.py          ← automação de relatórios (14 passos)
    rpa_fabrica.py            ← automação de fábrica (25 passos)
    rpa_transferencia.py      ← automação de transferência (16 passos)
    rpa_entrada_cte.py        ← automação de entrada CT-e
  imagens/                    ← imagens de referência dos botões
  data/
    logs/                     ← arquivos de log
    screenshots/              ← screenshots de erro (debug)
```

---

## 🐛 Troubleshooting rápido

**"Imagem não encontrada"**
→ Diminua `imagens.confianca` em `settings.yaml` ou recapture a imagem.
→ Veja o guia completo em [IMAGENS.md](IMAGENS.md).

**"Timeout esperando elemento"**
→ Aumente `automacao.timeout_elemento` em `settings.yaml`.
→ Verifique se o NBS está visível no monitor principal.

**Emojis quebrados no console (Windows)**
→ Já corrigido automaticamente. Se persistir: `chcp 65001` no cmd.exe antes de executar.

**Relatório não rodou no horário**
→ Verifique `agendador.horario_diario` no `settings.yaml` e consulte o log em `data/logs/`.

→ Para todos os outros problemas, veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## 📝 Logs

Todos os logs são salvos em `data/logs/nbs_agent.log` com timestamp e nível de detalhe.

Para mais detalhes durante uma execução, use `DEBUG`:

```yaml
logging:
  nivel: "DEBUG"
```
