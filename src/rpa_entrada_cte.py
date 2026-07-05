"""
rpa_entrada_cte.py
------------------
RPA de entrada em notas de CT-e (Conhecimento de Transporte Eletrônico).

Fluxo geral
~~~~~~~~~~~
1. Pede CNPJ do fornecedor via tela.pedir_formulario() — aparece no dashboard.
2. Para cada nota: pede dados via tela.pedir_formulario() — aparece no dashboard.
3. Executa a automação com os dados coletados (sem mais interação do usuário).

Mudança em relação à versão anterior:
  Todos os input() foram substituídos por self.tela.pedir_formulario().
  Em modo terminal funciona igual (pergunta campo a campo).
  Em modo dashboard exibe um formulário visual no browser.

Imagens necessárias (pasta imagens/)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
adm_aba · nbs_fiscal · entrada_cte · incluir_icone · persona
icone_pesquisa · aceitar_icone · numerode_nota · modelo_fiscal
barra_modelo · codigo_57 · barra_natureza · cfops · codigo_natureza
tributavel_codigo · naotributavel_codigo · verde_aceitar · adicao
contabilizacao · raio · faturamento · seta_preta · confirmar
"""

from __future__ import annotations

from dataclasses import dataclass

from src.tela   import Tela
from src.config import cfg
from src.logger import log


# ═══════════════════════════════════════════════════════════════════════════
#  Tipos auxiliares
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DadosNota:
    """Dados de uma única nota CT-e coletados do usuário."""
    numero:            str
    serie:             str
    emissao:           str
    modificar_entrada: bool
    numero_entrada:    str | None
    valor_total:       str
    nf_valor:          str
    chave_cte:         str
    numero_natureza:   str
    cidade_saida:      str
    uf_saida:          str
    cidade_chegada:    str
    uf_chegada:        str
    tem_icms:          bool
    porcentagem_icms:  str | None
    tem_outros:        bool
    valor_outros:      str | None


# ═══════════════════════════════════════════════════════════════════════════
#  Campos do formulário (definidos uma vez, usados no pedir_formulario)
# ═══════════════════════════════════════════════════════════════════════════

_CAMPOS_CNPJ = [
    {
        "nome":        "cnpj",
        "label":       "CNPJ do fornecedor",
        "tipo":        "texto",
        "placeholder": "00.000.000/0001-00",
        "validacao":   "cnpj",
    },
]

_CAMPOS_NOTA = [
    # ── Identificação ────────────────────────────────────────────────────
    {"nome": "numero",            "label": "Número da nota",              "tipo": "texto",
     "secao": "Identificação"},
    {"nome": "serie",             "label": "Série",                        "tipo": "texto"},
    {"nome": "emissao",           "label": "Data de emissão",              "tipo": "texto",
     "placeholder": "DD/MM/AAAA"},
    {"nome": "modificar_entrada", "label": "Modificar número de entrada?", "tipo": "bool"},
    {"nome": "numero_entrada",    "label": "Número de entrada",            "tipo": "texto",
     "condicional_em": "modificar_entrada"},

    # ── Valores ──────────────────────────────────────────────────────────
    {"nome": "valor_total",       "label": "Valor total da nota",          "tipo": "texto",
     "secao": "Valores", "placeholder": "1234.56"},
    {"nome": "nf_valor",          "label": "Valor NF",                     "tipo": "texto",
     "placeholder": "1234.56"},
    {"nome": "chave_cte",         "label": "Chave CT-e (44 dígitos)",      "tipo": "texto",
     "validacao": "chave_cte"},

    # ── Natureza ─────────────────────────────────────────────────────────
    {"nome": "numero_natureza",   "label": "Número de natureza",           "tipo": "opcao",
     "secao": "Natureza", "opcoes": ["2", "3"]},

    # ── Origem ───────────────────────────────────────────────────────────
    {"nome": "cidade_saida",      "label": "Cidade de saída",              "tipo": "texto",
     "secao": "Origem"},
    {"nome": "uf_saida",          "label": "UF de saída",                  "tipo": "texto",
     "placeholder": "SC", "maxlen": 2},

    # ── Destino ──────────────────────────────────────────────────────────
    {"nome": "cidade_chegada",    "label": "Cidade de chegada",            "tipo": "texto",
     "secao": "Destino"},
    {"nome": "uf_chegada",        "label": "UF de chegada",                "tipo": "texto",
     "placeholder": "SP", "maxlen": 2},

    # ── Tributação ───────────────────────────────────────────────────────
    {"nome": "tem_icms",          "label": "Tem ICMS?",                    "tipo": "bool",
     "secao": "Tributação"},
    {"nome": "porcentagem_icms",  "label": "Porcentagem do ICMS",          "tipo": "texto",
     "placeholder": "12", "condicional_em": "tem_icms"},
    {"nome": "tem_outros",        "label": "Tem Outros?",                  "tipo": "bool",
     "condicional_em": "tem_icms"},
    {"nome": "valor_outros",      "label": "Valor de Outros",              "tipo": "texto",
     "placeholder": "56.78", "condicional_em": "tem_outros"},
]


# ═══════════════════════════════════════════════════════════════════════════
#  RPA principal
# ═══════════════════════════════════════════════════════════════════════════

class EntradaCTE:
    """Automatiza a entrada de notas CT-e no módulo Fiscal do NBS."""

    def __init__(self, tela: Tela) -> None:
        self.tela = tela
        self._fat_entrada   = str(cfg("entrada_cte.faturamento_entrada_dias",   28))
        self._fat_intervalo = str(cfg("entrada_cte.faturamento_intervalo_dias", 28))
        self._fat_parcelas  = str(cfg("entrada_cte.faturamento_parcelas",        1))
        self._cod_contab    = str(cfg("entrada_cte.codigo_contabilizacao",     "40"))

    # ── Ponto de entrada público ──────────────────────────────────────

    def lancar(self, quantidade: int) -> dict[str, bool]:
        """
        Lança `quantidade` notas CT-e do mesmo fornecedor.

        Todos os dados são coletados via tela.pedir_formulario():
        - No terminal: campos aparecem um a um (comportamento anterior).
        - No dashboard: aparece um formulário visual no browser.

        Returns:
            {"1": True, "2": False, ...}
        """
        resultados: dict[str, bool] = {}

        cnpj = self._pedir_cnpj()

        for i in range(1, quantidade + 1):
            log.info(f"Coletando dados CT-e nota {i}/{quantidade}")
            dados = self._pedir_dados_nota(i, quantidade)

            log.info(f"Iniciando automação da nota {i}/{quantidade}")
            try:
                if i == 1:
                    self._lancar_primeira_nota(cnpj, dados)
                else:
                    self._lancar_nota_adicional(dados)

                resultados[str(i)] = True
                log.info(f"✓ Nota {i} lançada com sucesso")

            except Exception as exc:
                log.error(f"✗ Falha na nota {i}: {exc}")
                self.tela.screenshot(f"erro_cte_nota_{i}")
                resultados[str(i)] = False

                if i < quantidade:
                    continuar = self.tela.pausar_para_usuario(
                        f"Erro na nota {i}. Deseja tentar a próxima?"
                    )
                    if not continuar:
                        break

        return resultados

    # ── Coleta de dados via formulário ────────────────────────────────

    def _pedir_cnpj(self) -> str:
        """Pede CNPJ do fornecedor via dashboard ou terminal."""
        resultado = self.tela.pedir_formulario("CT-e — Fornecedor", _CAMPOS_CNPJ)
        return resultado["cnpj"]

    def _pedir_dados_nota(self, numero_nota: int, total: int) -> DadosNota:
        """
        Coleta todos os dados de uma nota via dashboard ou terminal.
        No dashboard exibe um formulário com seções e campos condicionais.
        """
        titulo = f"CT-e — Nota {numero_nota} de {total}"
        raw = self.tela.pedir_formulario(titulo, _CAMPOS_NOTA)

        return DadosNota(
            numero            = raw.get("numero", ""),
            serie             = raw.get("serie", ""),
            emissao           = raw.get("emissao", ""),
            modificar_entrada = bool(raw.get("modificar_entrada")),
            numero_entrada    = raw.get("numero_entrada") or None,
            valor_total       = raw.get("valor_total", ""),
            nf_valor          = raw.get("nf_valor", ""),
            chave_cte         = raw.get("chave_cte", ""),
            numero_natureza   = raw.get("numero_natureza", "2"),
            cidade_saida      = raw.get("cidade_saida", ""),
            uf_saida          = (raw.get("uf_saida") or "").upper(),
            cidade_chegada    = raw.get("cidade_chegada", ""),
            uf_chegada        = (raw.get("uf_chegada") or "").upper(),
            tem_icms          = bool(raw.get("tem_icms")),
            porcentagem_icms  = raw.get("porcentagem_icms") or None,
            tem_outros        = bool(raw.get("tem_outros")),
            valor_outros      = raw.get("valor_outros") or None,
        )

    # ── Fluxos por tipo de nota ───────────────────────────────────────

    def _lancar_primeira_nota(self, cnpj: str, dados: DadosNota) -> None:
        self._navegar_para_modulo()
        self._abrir_nova_entrada(cnpj)
        self._preencher_dados_nota(dados)
        self._preencher_cfop_e_icms(dados)
        self._contabilizacao_primeira_nota()
        self._finalizar()

    def _lancar_nota_adicional(self, dados: DadosNota) -> None:
        self.tela.clicar("incluir_icone")
        self.tela.clicar("numerode_nota")
        self.tela.tecla("backspace")

        self._preencher_dados_nota(dados)
        self._preencher_cfop_e_icms(dados)
        self._contabilizacao_nota_adicional()
        self._finalizar()

    # ── Passos de automação ───────────────────────────────────────────

    def _navegar_para_modulo(self) -> None:
        log.info("Navegando para NBS Fiscal → Entrada CT-e")
        self.tela.clicar("adm_aba")
        self.tela.clicar("nbs_fiscal")
        self.tela.esperar(5)
        for _ in range(3):
            self.tela.tecla("enter")
        self.tela.esperar(2)
        self.tela.tecla("enter")
        self.tela.esperar(1)
        self.tela.tecla("enter")
        self.tela.clicar("entrada_cte")

    def _abrir_nova_entrada(self, cnpj: str) -> None:
        log.info(f"Abrindo nova entrada CT-e (CNPJ: {cnpj})")
        self.tela.clicar("incluir_icone")
        self.tela.clicar("persona")
        self.tela.tecla("tab")
        self.tela.tecla("tab")
        self.tela.digitar(cnpj)
        self.tela.tecla("enter")
        self.tela.clicar("icone_pesquisa")
        self.tela.clicar("aceitar_icone")
        self.tela.tecla("tab")

    def _preencher_dados_nota(self, dados: DadosNota) -> None:
        log.info(f"Preenchendo dados da nota {dados.numero}")

        self.tela.digitar(dados.numero)
        self.tela.tecla("tab")
        self.tela.digitar(dados.serie)
        self.tela.tecla("tab")
        self.tela.digitar(dados.emissao)
        self.tela.tecla("tab")

        if dados.modificar_entrada and dados.numero_entrada:
            self.tela.digitar(dados.numero_entrada)

        for _ in range(9):
            self.tela.tecla("tab")

        self.tela.digitar(dados.valor_total)

        for _ in range(6):
            self.tela.tecla("tab")

        self.tela.digitar(f"nf {dados.nf_valor}")

        self.tela.clicar("modelo_fiscal")
        self.tela.clicar("barra_modelo")
        self.tela.clicar("codigo_57")

        for _ in range(3):
            self.tela.tecla("tab")

        self.tela.digitar(dados.chave_cte)

    def _preencher_cfop_e_icms(self, dados: DadosNota) -> None:
        log.info("Preenchendo CFOP, cidades e tributação")

        self.tela.clicar("barra_natureza")
        self.tela.digitar(dados.numero_natureza)
        self.tela.tecla("tab")
        self.tela.digitar("0")
        self.tela.tecla("tab")

        self.tela.digitar(dados.cidade_saida)
        self.tela.tecla("tab")
        self.tela.digitar(dados.uf_saida)
        self.tela.tecla("tab")
        self.tela.digitar(dados.cidade_chegada)
        self.tela.tecla("tab")
        self.tela.digitar(dados.uf_chegada)
        self.tela.tecla("tab")

        self.tela.clicar("cfops")
        self.tela.clicar("codigo_natureza")
        cfop = "1353" if dados.uf_saida == dados.uf_chegada else "2353"
        log.info(f"CFOP selecionado: {cfop}")
        self.tela.digitar(cfop)

        if dados.tem_icms:
            self._preencher_com_icms(dados)
        else:
            self._preencher_sem_icms(dados)

    def _preencher_com_icms(self, dados: DadosNota) -> None:
        log.info("Tributação: COM ICMS")
        self.tela.clicar("tributavel_codigo")
        self.tela.clicar("verde_aceitar")
        self.tela.tecla("tab")
        self.tela.tecla("tab")
        self.tela.digitar(dados.valor_total)
        self.tela.tecla("tab")
        self.tela.digitar(dados.porcentagem_icms or "")
        self.tela.tecla("enter")

        if dados.tem_outros and dados.valor_outros:
            log.info("Preenchendo campo Outros")
            self.tela.tecla("enter")
            self.tela.digitar(dados.valor_outros)

        self.tela.clicar("adicao")

    def _preencher_sem_icms(self, dados: DadosNota) -> None:
        log.info("Tributação: SEM ICMS")
        self.tela.clicar("naotributavel_codigo")
        self.tela.clicar("verde_aceitar")
        self.tela.tecla("tab")
        self.tela.tecla("tab")
        self.tela.digitar(dados.valor_total)
        self.tela.clicar("adicao")

    def _contabilizacao_primeira_nota(self) -> None:
        log.info("Preenchendo Contabilização (primeira nota)")
        self.tela.clicar("contabilizacao")
        self.tela.tecla("tab")
        self.tela.tecla("tab")
        self.tela.digitar(self._cod_contab)
        self.tela.tecla("enter")
        self.tela.clicar("raio")
        self.tela.clicar("faturamento")

    def _contabilizacao_nota_adicional(self) -> None:
        log.info("Preenchendo Contabilização (nota adicional)")
        self.tela.clicar("contabilizacao")
        self.tela.clicar("raio")
        self.tela.clicar("faturamento")

    def _finalizar(self) -> None:
        log.info("Preenchendo Faturamento e confirmando lançamento")

        for _ in range(4):
            self.tela.tecla("tab")

        self.tela.digitar(self._fat_entrada)
        self.tela.tecla("tab")
        self.tela.digitar(self._fat_intervalo)
        self.tela.tecla("tab")
        self.tela.digitar(self._fat_parcelas)

        self.tela.pausar_para_usuario(
            "Revise os dados na tela. Clique em Continuar para confirmar o lançamento."
        )

        self.tela.clicar("seta_preta")
        self.tela.clicar("confirmar")
        self.tela.tecla("left")
        self.tela.tecla("enter")
        self.tela.tecla("enter")
        self.tela.esperar(3)
        self.tela.clicar("cancelar")

        log.info("Lançamento CT-e confirmado")
