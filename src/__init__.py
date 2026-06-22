"""
src — Pacote principal do NBS Agent.

Módulos
-------
agente             Orquestrador: une RPAs, agendador e menu
tela               Controle de mouse/teclado via PyAutoGUI + OpenCV
config             Leitura do settings.yaml com validação
logger             Log colorido no terminal e em arquivo
agendador          Disparo automático do relatório diário
menu               Menu interativo com setas ↑ ↓ (cross-platform)
constantes         Constantes globais e nomes canônicos de imagens
mapeamento_imagens Fonte de verdade de todos os arquivos de imagem
rpa_relatorio      Geração do relatório de compras (14 passos)
rpa_fabrica        Lançamento de notas de fábrica (25 passos)
rpa_transferencia  Lançamento de notas de transferência (16 passos)
rpa_entrada_cte    Entrada de notas CT-e (fluxo CTE1 + CTE2)
"""
