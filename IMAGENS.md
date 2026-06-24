# IMAGENS.md — Guia de Imagens do NBS Agent

> **Público:** usuários finais e quem mantém as capturas de tela.  
> Para visão técnica, veja [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Como funciona

O agente localiza botões e campos na tela comparando pequenas **imagens de referência** (PNGs/JPEGs salvos na pasta `imagens/`) com o que está sendo exibido no monitor.

Se uma imagem não for encontrada, o passo falha. A solução quase sempre é **recapturar** a imagem.

---

## Como recapturar uma imagem

| Sistema | Atalho | Ferramenta |
|---|---|---|
| Windows | `Win + Shift + S` | Ferramenta de Recorte |
| macOS | `Cmd + Shift + 4` | Screenshot |
| Linux | `PrtScn` ou ferramenta de sua distro | Varia |

**Dicas importantes:**
- Recorte **pequeno e preciso** — só o botão ou campo, sem bordas extras
- **Sem sombras** ao redor do elemento
- Capture com o **NBS no monitor principal**
- Se o elemento tiver estado (hover, selecionado), capture no **estado normal**
- Salve como `.png` na pasta `imagens/` com o **nome exato** da tabela abaixo

---

## Tabela completa de imagens

### RELATÓRIO (10 imagens)

| Arquivo | Onde aparece no NBS | Quando é usado |
|---|---|---|
| `campo_empresa.png` | Caixa de seleção da empresa | Passo 1: clica para abrir a lista |
| `empresa_duna_tubarao.png` | Opção "Duna-Tubarão" na lista | Passo 3: seleciona a empresa |
| `entrada_data_relatorio.png` | Campo data de entrada | Passos 4a/4c: clicar e confirmar |
| `emissao_data_relatorio.png` | Campo data de emissão | Passos 5a/5c: clicar e confirmar |
| `botao_pesquisa_relatorio.png` | Botão Pesquisar | Passo 6: dispara a consulta |
| `botao_nota_relatorio.png` | Coluna/aba "Nota" | Passo 7: ordena resultados por nota |
| `btn_imprimir_lista.png` | Botão Imprimir Lista | Passo 8: abre diálogo de impressão |
| `botao_sim.png` | Botão Sim (confirmação) | Passo 9: confirma impressão fiscal |
| `botao_icone_impressao_relatorio.png` | Ícone de impressão | Passo 11: abre o viewer do relatório |
| `aba_ipressao_relatorio.png` | Tela do relatório no browser | Passo 13: aguarda aparecer antes de Ctrl+P |

> ⚠️ O arquivo chama-se `aba_i**p**ressao_relatorio.png` (com "i") — é o nome real no disco.

---

### TRANSFERÊNCIA (11 imagens — algumas compartilhadas com Fábrica)

| Arquivo | Onde aparece no NBS | Quando é usado |
|---|---|---|
| `botao_incluir.png` | Botão Incluir em Compras | Passo 1: inicia novo lançamento |
| `botao_transferencia.png` | Opção Transferência | Passo 2: seleciona tipo |
| `btn_interface.png` | Botão Interface | Passo 3: carrega a nota |
| `btn_interface_saida.png` | Opção Interface de Saída | Passo 4: define direção da nota |
| `btn_pesquisar_transf.png` | Botão Pesquisar | Passo 5: busca a nota |
| `btn_aceitar.png` | Botão Aceitar | Passo 6: confirma a nota encontrada |
| `aba_locacao.png` | Aba Locações | Passo 8: abre seção de locação |
| `campo_locacao.png` | Placeholder tipo de locação | Passo 9: clica para abrir opções |
| `principal_pecas.png` | Opção PRINCIPAL(PEÇAS) | Passo 10: seleciona tipo de locação |
| `locacao_padrao.png` | Placeholder locação padrão | Passo 11: clica para digitar "SL" |
| `btn_confirmar.png` | Botão Confirmar/OK | Passo 13: salva o lançamento |

---

### FÁBRICA (15 imagens exclusivas + 7 compartilhadas acima)

| Arquivo | Onde aparece no NBS | Quando é usado |
|---|---|---|
| `botao_compra.png` | Opção Compra | Passo 2: seleciona tipo de lançamento |
| `placeholder_nota_fabrica.png` | Campo número da nota | Passo 4: clica antes de digitar a nota |
| `btn_pesquisar_nota.png` | Botão Pesquisar | Passo 6: busca a nota digitada |
| `aba_definir_tributacao.png` | Aba Definir Tributação/CFOP | Passo 7: abre tela de tributação |
| `area_centro.png` | Referência visual — centro da tela | Passo 8: onde fazer botão direito |
| `definir_cfop.png` | Opção "Definir CFOP" | Passo 9: menu de contexto após clique direito |
| `campo_tributados.png` | Dropdown Tributados | Passo 11: abre lista de tributação |
| `selecao_pecas_acessorios.png` | Opção COMPRA PEÇAS E ACESSÓRIOS | Passo 12: seleciona tipo de tributação |
| `btn_ok.png` | Botão OK | Passo 13: confirma tributação |
| `aba_cruzamento_pedidos.png` | Aba Cruzamento de Pedidos | Passo 15: abre cruzamento |
| `seta_cruzamento.png` | Seta → do cruzamento | Passo 16: tenta cruzamento automático |
| `botao_confirmar.png` | Botão Confirmar no cruzamento | Passo 16: confirma pedido cruzado |
| `aba_financeiro.png` | Aba Financeiro | Passo 22: abre campos financeiros |
| `btn_confirmar_final.png` | Botão Confirmar (final) | Passo 24: fecha o lançamento |
| *(compartilhadas)* | `botao_incluir`, `btn_interface`, `btn_aceitar`, `aba_locacao`, `campo_locacao`, `principal_pecas`, `locacao_padrao` | Mesmas imagens da transferência |

---

### ENTRADA CT-e (24 imagens)

| Arquivo | Onde aparece no NBS | Quando é usado |
|---|---|---|
| `adm_aba.png` | Aba ADM no topo | Abre o menu de módulos |
| `nbs_fiscal.png` | Ícone NBS Fiscal | Entra no módulo Fiscal |
| `entrada_cte.png` | Opção Entrada CT-e | Acessa a tela de entrada |
| `incluir_icone.png` | Ícone/botão Incluir | Inicia nova entrada |
| `persona.png` | Campo Persona/Fornecedor | Localiza o campo do fornecedor |
| `icone_pesquisa.png` | Ícone de lupa | Pesquisa fornecedor por CNPJ |
| `aceitar_icone.png` | Ícone aceitar | Confirma o fornecedor encontrado |
| `numerode_nota.png` | Campo Número da Nota | 1ª nota: preenche; 2ª+: limpa com Backspace |
| `modelo_fiscal.png` | Campo Modelo Fiscal | Abre o dropdown de modelos |
| `barra_modelo.png` | Barra de seleção do modelo | Localiza a seleção após abrir dropdown |
| `codigo_57.png` | Código 57 (CT-e) | Seleciona o modelo correto |
| `barra_natureza.png` | Campo Natureza da Operação | Localiza campo de natureza |
| `cfops.png` | Área de CFOPs | Abre seleção de código CFOP |
| `codigo_natureza.png` | Campo Código de Natureza | Digitar 1353 (entrada) ou 2353 (devolução) |
| `tributavel_codigo.png` | Opção Tributável | Seleciona tributação tributável |
| `naotributavel_codigo.png` | Opção Não Tributável | Seleciona tributação não tributável |
| `verde_aceitar.png` | Botão verde de aceitar | Confirma a tributação escolhida |
| `adicao.png` | Botão Adição | Confirma e avança na tributação |
| `contabilizacao.png` | Aba Contabilização | Acessa campos de contabilização |
| `raio.png` | Ícone Raio | Atalho de contabilização automática |
| `faturamento.png` | Aba Faturamento | Acessa campos de faturamento |
| `seta_preta.png` | Seta preta → | Avança para próxima etapa |
| `confirmar.png` | Botão Confirmar | Salva o lançamento CT-e |
| `cancelar.png` | Botão Cancelar/Fechar | ⏳ **Pendente** — capturar quando adicionado ao fluxo |

---

## Diagnóstico rápido

Para verificar quais imagens estão presentes e quais faltam:

```bash
python src/mapeamento_imagens.py           # resumo: OK / faltando
python src/mapeamento_imagens.py --listar  # lista completa com status
```

Saída esperada após configuração completa:
```
✓ Todas as 43 imagens ativas encontradas.  (cancelar.png é pendente conforme design)
```

---

## Problemas comuns

**Imagem encontrada no lugar errado (clica fora do botão)**  
→ Recapture com recorte menor e mais preciso.

**`confianca` muito alta (padrão 0.85) — elemento não é encontrado**  
→ Diminua em `config/settings.yaml`:
```yaml
imagens:
  confianca: 0.75
```

**Elemento mudou de aparência após atualização do NBS**  
→ Recapture a imagem. Não altere o nome do arquivo.

**Dúvida sobre onde está cada arquivo**  
→ Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para mais cenários.
