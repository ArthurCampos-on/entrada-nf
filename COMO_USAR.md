# NBS Agent — Como Usar

## 📋 Pré-requisitos

1. **Windows** com Python 3.10+
2. **Chrome** já aberto com o **NBS logado** (Cloud Service + NBS Shortcut)
3. Dependências instaladas: `pip install -r requirements.txt`

## 🚀 Execução

```bash
# Menu interativo
python __main__.py

# Ou comando direto (sem menu)
python __main__.py relatorio       # Gera relatório do dia anterior
python __main__.py fabrica         # Lança fábrica (vai perguntar notas)
python __main__.py transferencia   # Lança transferência (vai perguntar notas)
```

> **Importante**: O Chrome já deve estar **aberto e com NBS logado** antes de executar!

## 📺 Menu Interativo

Ao executar `python __main__.py`, aparecerá um menu com setas (↑ ↓):

```
╔════════════════════════════════════════╗
║           NBS Agent                    ║
╠════════════════════════════════════════╣
║  →  Relatório diário                   ║
║     Fábrica                            ║
║     Transferência                      ║
║     Status                             ║
║     NBS                                ║
║     Sair                               ║
╠════════════════════════════════════════╣
║  ↑ ↓ navegar   Enter confirmar   Q sair║
╚════════════════════════════════════════╝
```

### Opções:
- **Relatório diário**: Extrai dados do dia anterior e gera relatório
- **Fábrica**: Solicita notas e lança lançamentos de fábrica
- **Transferência**: Solicita notas e lança lançamentos de transferência  
- **Status**: Mostra quando o próximo relatório será gerado (se agendado)
- **NBS**: Traz a janela do NBS para foco
- **Sair**: Encerra o agente (Chrome continua aberto)

## ⚙️ Configuração

Edite `config/settings.yaml` para personalizar:

```yaml
agendador:
  ativo: true                 # Ativa geração automática de relatórios
  hora: "08:00"              # Horário para gerar relatório
  fuso: "America/Sao_Paulo"

logging:
  nivel: "INFO"              # DEBUG | INFO | WARNING | ERROR
  arquivo: "data/logs/nbs_agent.log"

whatsapp:
  url: "https://web.whatsapp.com"

imagens:
  pasta: "imagens"
  confianca: 0.85            # Confiança para match de template (0-1)

automacao:
  timeout_elemento: 15       # Timeout para encontrar elementos (segundos)
  atraso_minimo: 0.3         # Pausa mínima entre cliques
```

## 📁 Estrutura

```
nbs-agent/
  __main__.py                 ← Entrypoint (começa aqui)
  requirements.txt
  config/
    settings.yaml             ← Configurações
  src/
    agente.py                 ← Orquestrador principal
    browser.py                ← Controla Chrome (focar janela)
    tela.py                   ← Encontra/clica em imagens na tela
    menu.py                   ← Menu interativo
    rpa_relatorio.py          ← Automação de relatórios
    rpa_fabrica.py            ← Automação de fábrica
    rpa_transferencia.py      ← Automação de transferência
    agendador.py              ← Geração automática de relatórios
  imagens/                    ← Templates para template matching
  data/
    logs/                     ← Arquivos de log (.log)
    screenshots/              ← Screenshots de erro (debug)
```

## 🐛 Troubleshooting

**"Imagem não encontrada"**
- Certifique-se de que a janela do NBS está focada e visível
- Ajuste a `confianca` em `settings.yaml` (valores mais baixos = menos rigoroso)
- Capture um novo screenshot da imagem e coloque em `imagens/`

**"Timeout esperando elemento"**
- Aumente `timeout_elemento` em `settings.yaml`
- Verifique se está no local correto do sistema

**Emojis quebrados no console**
- Já está corrigido no código (força UTF-8 automaticamente)
- Se ainda tiver problemas, execute: `chcp 65001` no cmd.exe antes

## 📝 Logs

Todos os logs são salvos em `data/logs/nbs_agent.log` com timestamp e nível de detalhe.

Execute com `logging.nivel: "DEBUG"` para mais detalhes.
