# NBS Agent — Troubleshooting

## Imagem não encontrada na tela

**Sintoma:** `WARNING — Imagem não encontrada: imagens/xxx.png`

**Causas e soluções:**

1. **NBS não está no monitor principal**
   → Mova a janela do NBS para o monitor 1 antes de executar.

2. **Zoom ou resolução diferente do esperado**
   → Recapture a imagem com Win+Shift+S na mesma configuração de tela que será usada.

3. **Confiança muito alta**
   → Diminua em `config/settings.yaml`:
   ```yaml
   imagens:
     confianca: 0.72
   ```

4. **Arquivo da imagem não existe**
   → Verifique com `python src/mapeamento_imagens.py`.
   → Recorte e salve em `imagens/` com o nome exato.

---

## Timeout esperando elemento

**Sintoma:** `TimeoutError: 'xxx' não apareceu em 15s`

**Soluções:**

- Aumente o timeout em `settings.yaml`:
  ```yaml
  automacao:
    timeout_elemento: 25
  ```

- Verifique se o NBS está na tela certa (sem janela bloqueando).

- Se a falha for numa etapa específica, aumente o `delay_acao`:
  ```yaml
  automacao:
    delay_acao: 1.0
  ```

---

## Automação clica no lugar errado

**Causas:**

- NBS não está no monitor principal.
- Outra janela abriu por cima do NBS entre um passo e outro.
- Imagem de referência desatualizada (botão mudou de aparência com update do NBS).

**Solução:** recapture a imagem com Win+Shift+S, salve com o mesmo nome em `imagens/`.

---

## Emojis ou acentos quebrados no console

O código já força UTF-8 no Windows automaticamente. Se ainda aparecer `?` ou `█`:

```cmd
chcp 65001
python __main__.py
```

---

## Relatório automático não roda no horário

1. Verifique se o programa está de fato rodando (menu visível no terminal).
2. Confira o horário em `settings.yaml`:
   ```yaml
   agendador:
     horario_diario: "08:00"
   ```
3. Use `Status` no menu para ver quanto tempo falta.
4. Verifique o log em `data/logs/nbs_agent.log` para erros anteriores.

---

## Erro de digitação de texto com acento (ã, ç, é)

O sistema usa clipboard (`Ctrl+V`) para digitar, o que suporta qualquer
caractere. Se o texto não aparecer correto:

- Verifique se o campo de destino no NBS aceita o caractere.
- Tente aumentar o `delay_acao` para dar mais tempo ao clipboard:
  ```yaml
  automacao:
    delay_acao: 0.8
  ```

---

## Nota não encontrada no sistema

No fluxo de Fábrica e Transferência, se o número de nota não existir
no NBS a pesquisa retorna lista vazia. O sistema vai aguardar o elemento
de confirmação e estourar `TimeoutError`. Um screenshot é salvo em
`data/screenshots/` para diagnóstico.

---

## Screenshot de erro

Toda falha salva automaticamente uma imagem em `data/screenshots/`.
O nome inclui o contexto (`erro_fabrica_123456_1700000000.png`).

Abra essa imagem para ver exatamente o estado da tela no momento da falha.

---

## Pausa manual não responde

As pausas (`pausar_para_usuario`) aguardam `y` ou `n` no **terminal**,
não na tela do NBS. Clique no terminal antes de digitar.

---

## Log com muitos detalhes / poucos detalhes

Altere o nível em `settings.yaml`:

```yaml
logging:
  nivel: "DEBUG"    # mais detalhes
  nivel: "WARNING"  # só erros e avisos
```
