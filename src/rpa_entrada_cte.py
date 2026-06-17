"""
rpa_entrada_cte.py
------------------
RPA de entrada em notas de CT-e (Conhecimento de Transporte Eletrônico).

Fluxo geral
~~~~~~~~~~~
1. O usuário informa quantas notas têm o mesmo fornecedor.
2. Para a **primeira nota** executa o fluxo completo:
   navegação pelo NBS → Fiscal → Entrada CTE → preenchimento → confirmação.
3. Para as **notas adicionais** (mesmo fornecedor) reutiliza a tela já aberta
   e pula as etapas de navegação e de pesquisa de CNPJ.

Imagens necessárias (pasta imagens/)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
adm_aba · nbs_fiscal · entrada_cte · incluir_icone · persona
icone_pesquisa · aceitar_icone · numerode_nota · modelo_fiscal
barra_modelo · codigo_57 · barra_natureza · cfops · codigo_natureza
tributavel_codigo · naotributavel_codigo · verde_aceitar · adicao
contabilizacao · raio · faturamento · seta_preta · confirmar
"""

from __future__ import annotations

from src.tela   import Tela
from src.logger import log


# ═══════════════════════════════════════════════════════════════════════════
#  Tipos auxiliares
# ═══════════════════════════════════════════════════════════════════════════

class DadosNota:
    """Dados de uma única nota CT-e coletados do usuário."""

    def __init__(
        self,
        numero:          str,
        serie:           str,
        emissao:         str,
        modificar_entrada: bool,
        numero_entrada:  str | None,
        valor_total:     str,
        nf_valor:        str,
        chave_cte:       str,
        numero_natureza: str,
        cidade_saida:    str,
        uf_saida:        str,
        cidade_chegada:  str,
        uf_chegada:      str,
        tem_icms:        bool,
        porcentagem_icms: str | None,
        tem_outros:      bool,
        valor_outros:    str | None,
    ) -> None:
        self.numero           = numero
        self.serie            = serie
        self.emissao          = emissao
        self.modificar_entrada = modificar_entrada
        self.numero_entrada   = numero_entrada
        self.valor_total      = valor_total
        self.nf_valor         = nf_valor
        self.chave_cte        = chave_cte
        self.numero_natureza  = numero_natureza
        self.cidade_saida     = cidade_saida
        self.uf_saida         = uf_saida
        self.cidade_chegada   = cidade_chegada
        self.uf_chegada       = uf_chegada
        self.tem_icms         = tem_icms
        self.porcentagem_icms = porcentagem_icms
        self.tem_outros       = tem_outros
        self.valor_outros     = valor_outros


# ═══════════════════════════════════════════════════════════════════════════
#  RPA principal
# ═══════════════════════════════════════════════════════════════════════════

class EntradaCTE:
    """Automatiza a entrada de notas CT-e no módulo Fiscal do NBS."""

    def __init__(self, tela: Tela) -> None:
        self.tela = tela

    # ------------------------------------------------------------------ #
    #  Ponto de entrada público                                           #
    # ------------------------------------------------------------------ #

    def lancar(self, quantidade: int) -> dict[str, bool]:
        """
        Lança `quantidade` notas CT-e do mesmo fornecedor.

        Retorna dict mapeando número da nota (1-indexed) → True/False.
        """
        resultados: dict[str, bool] = {}

        cnpj = self._pedir_cnpj()

        for i in range(1, quantidade + 1):
            log.info(f"Iniciando CT-e nota {i}/{quantidade}")
            dados = self._pedir_dados_nota(i, quantidade)

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

    # ------------------------------------------------------------------ #
    #  Fluxos por tipo de nota                                            #
    # ------------------------------------------------------------------ #

    def _lancar_primeira_nota(self, cnpj: str, dados: DadosNota) -> None:
        """Fluxo completo: navegação + CNPJ + preenchimento + confirmação."""
        self._navegar_para_modulo()
        self._abrir_nova_entrada(cnpj)
        self._preencher_dados_nota(dados)
        self._preencher_cfop_e_icms(dados)
        self._contabilizacao_primeira_nota()
        self._finalizar()

    def _lancar_nota_adicional(self, dados: DadosNota) -> None:
        """
        Fluxo reduzido (mesmo fornecedor):
        pula navegação e pesquisa de CNPJ.
        """
        # Abre nova entrada reaproveitando o fornecedor já selecionado
        self.tela.clicar("incluir_icone")
        self.tela.clicar("numerode_nota")
        self.tela.tecla("backspace")

        self._preencher_dados_nota(dados)
        self._preencher_cfop_e_icms(dados)
        self._contabilizacao_nota_adicional()
        self._finalizar()

    # ------------------------------------------------------------------ #
    #  Passos compartilhados                                              #
    # ------------------------------------------------------------------ #

    def _navegar_para_modulo(self) -> None:
        """
        Navega até a tela de Entrada CT-e dentro do NBS Fiscal.
        Executa ao iniciar a PRIMEIRA nota.
        """
        log.info("Navegando para NBS Fiscal → Entrada CT-e")

        self.tela.clicar("adm_aba")
        self.tela.clicar("nbs_fiscal")

        # NBS Fiscal demora para abrir — aguarda 5 s e confirma telas
        self.tela.esperar(5)
        for _ in range(3):
            self.tela.tecla("enter")
        self.tela.esperar(2)
        self.tela.tecla("enter")
        self.tela.esperar(1)
        self.tela.tecla("enter")

        self.tela.clicar("entrada_cte")

    def _abrir_nova_entrada(self, cnpj: str) -> None:
        """
        Clica em Incluir, seleciona Persona e preenche o CNPJ do fornecedor.
        Executado apenas na primeira nota.
        """
        log.info(f"Abrindo nova entrada CT-e (CNPJ: {cnpj})")

        self.tela.clicar("incluir_icone")
        self.tela.clicar("persona")

        # Dois tabs avançam até o campo de CNPJ
        self.tela.tecla("tab")
        self.tela.tecla("tab")

        self.tela.digitar(cnpj)
        self.tela.tecla("enter")

        self.tela.clicar("icone_pesquisa")
        self.tela.clicar("aceitar_icone")

        # Um tab posiciona no campo Número da Nota
        self.tela.tecla("tab")

    def _preencher_dados_nota(self, dados: DadosNota) -> None:
        """
        Preenche número, série, emissão, valor total, NF,
        modelo fiscal (código 57) e chave CT-e.
        """
        log.info(f"Preenchendo dados da nota {dados.numero}")

        # ── Número, Série, Emissão ────────────────────────────────────
        self.tela.digitar(dados.numero)
        self.tela.tecla("tab")

        self.tela.digitar(dados.serie)
        self.tela.tecla("tab")

        self.tela.digitar(dados.emissao)
        self.tela.tecla("tab")

        # ── Número de entrada (opcional) ──────────────────────────────
        # Cursor está no campo Número de Entrada.
        # Se o usuário quis modificar, preenche; caso contrário deixa o padrão.
        if dados.modificar_entrada and dados.numero_entrada:
            self.tela.digitar(dados.numero_entrada)

        # 9 tabs avançam até o campo Valor Total
        for _ in range(9):
            self.tela.tecla("tab")

        # ── Valor total ───────────────────────────────────────────────
        self.tela.digitar(dados.valor_total)

        # 6 tabs avançam até o campo NF
        for _ in range(6):
            self.tela.tecla("tab")

        # ── NF (prefixo "nf " + valor) ────────────────────────────────
        self.tela.digitar(f"nf {dados.nf_valor}")

        # ── Modelo fiscal → código 57 ─────────────────────────────────
        self.tela.clicar("modelo_fiscal")
        self.tela.clicar("barra_modelo")
        self.tela.clicar("codigo_57")

        # 3 tabs posicionam no campo Chave CT-e
        for _ in range(3):
            self.tela.tecla("tab")

        self.tela.digitar(dados.chave_cte)

    def _preencher_cfop_e_icms(self, dados: DadosNota) -> None:
        """
        Preenche Natureza da Operação, cidades, CFOP e tributação (ICMS).
        """
        log.info("Preenchendo CFOP, cidades e tributação")

        # ── Natureza da operação ──────────────────────────────────────
        self.tela.clicar("barra_natureza")
        self.tela.digitar(dados.numero_natureza)
        self.tela.tecla("tab")

        self.tela.digitar("0")
        self.tela.tecla("tab")

        # ── Cidades ───────────────────────────────────────────────────
        self.tela.digitar(dados.cidade_saida)
        self.tela.tecla("tab")
        self.tela.digitar(dados.uf_saida)
        self.tela.tecla("tab")
        self.tela.digitar(dados.cidade_chegada)
        self.tela.tecla("tab")
        self.tela.digitar(dados.uf_chegada)
        self.tela.tecla("tab")

        # ── CFOP: 1353 (mesmo estado) ou 2353 (estados diferentes) ───
        self.tela.clicar("cfops")
        self.tela.clicar("codigo_natureza")
        cfop = "1353" if dados.uf_saida == dados.uf_chegada else "2353"
        log.info(f"CFOP selecionado: {cfop}")
        self.tela.digitar(cfop)

        # ── Tributação ────────────────────────────────────────────────
        if dados.tem_icms:
            self._preencher_com_icms(dados)
        else:
            self._preencher_sem_icms(dados)

    def _preencher_com_icms(self, dados: DadosNota) -> None:
        """Preenche tributação quando a nota tem ICMS."""
        log.info("Tributação: COM ICMS")

        self.tela.clicar("tributavel_codigo")
        self.tela.clicar("verde_aceitar")

        self.tela.tecla("tab")
        self.tela.tecla("tab")

        self.tela.digitar(dados.valor_total)
        self.tela.tecla("tab")

        self.tela.digitar(dados.porcentagem_icms or "")
        self.tela.tecla("enter")

        # Outros (ex: PIS/COFINS sobre CT-e)
        if dados.tem_outros and dados.valor_outros:
            log.info("Preenchendo campo Outros")
            self.tela.tecla("enter")
            self.tela.digitar(dados.valor_outros)

        self.tela.clicar("adicao")

    def _preencher_sem_icms(self, dados: DadosNota) -> None:
        """Preenche tributação quando a nota NÃO tem ICMS."""
        log.info("Tributação: SEM ICMS")

        self.tela.clicar("naotributavel_codigo")
        self.tela.clicar("verde_aceitar")

        self.tela.tecla("tab")
        self.tela.tecla("tab")

        self.tela.digitar(dados.valor_total)

        self.tela.clicar("adicao")

    def _contabilizacao_primeira_nota(self) -> None:
        """
        Preenche a aba Contabilização.
        Na primeira nota inclui passos extras (2× Tab + código 40 + Enter).
        """
        log.info("Preenchendo Contabilização (primeira nota)")

        self.tela.clicar("contabilizacao")

        self.tela.tecla("tab")
        self.tela.tecla("tab")
        self.tela.digitar("40")
        self.tela.tecla("enter")

        self.tela.clicar("raio")
        self.tela.clicar("faturamento")

    def _contabilizacao_nota_adicional(self) -> None:
        """
        Preenche a aba Contabilização para notas adicionais.
        Pula o Tab/40/Enter — vai direto para Raio e Faturamento.
        """
        log.info("Preenchendo Contabilização (nota adicional)")

        self.tela.clicar("contabilizacao")
        self.tela.clicar("raio")
        self.tela.clicar("faturamento")

    def _finalizar(self) -> None:
        """
        Preenche Faturamento, pausa para revisão manual e confirma o lançamento.
        Compartilhado entre primeira nota e notas adicionais.
        """
        log.info("Preenchendo Faturamento e confirmando lançamento")

        # 4 tabs + campos fixos de faturamento
        for _ in range(4):
            self.tela.tecla("tab")

        self.tela.digitar("28")
        self.tela.tecla("tab")
        self.tela.digitar("28")
        self.tela.tecla("tab")
        self.tela.digitar("1")

        # Pausa para o usuário revisar os dados na tela antes de confirmar
        self.tela.pausar_para_usuario(
            "Revise os dados na tela. Digite Y para confirmar o lançamento."
        )

        self.tela.clicar("seta_preta")
        self.tela.clicar("confirmar")

        self.tela.tecla("left")   # seta esquerda (navega diálogo de confirmação)
        self.tela.tecla("enter")  # confirma seleção
        self.tela.tecla("enter")  # segunda confirmação
        self.tela.esperar(3)
        self.tela.clicar("cancelar")  # fecha tela após lançamento

        log.info("Lançamento CT-e confirmado")

    # ------------------------------------------------------------------ #
    #  Coleta de dados do usuário                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _pedir_cnpj() -> str:
        """Pede o CNPJ do fornecedor (único para todas as notas do lote)."""
        print("\n" + "═" * 52)
        print("  📋 ENTRADA CT-e — Dados do Fornecedor")
        print("═" * 52)
        return input("  CNPJ do fornecedor: ").strip()

    @staticmethod
    def _pedir_dados_nota(numero_nota: int, total: int) -> DadosNota:
        """
        Coleta interativamente todos os dados necessários para uma nota.
        As perguntas são feitas ANTES de iniciar a automação desta nota,
        para não exigir atenção no terminal durante o preenchimento.
        """
        print("\n" + "═" * 52)
        print(f"  📋 NOTA {numero_nota} de {total}")
        print("═" * 52)

        numero = input("  Número da nota: ").strip()
        serie  = input("  Série: ").strip()
        emissao = input("  Data de emissão (DD/MM/AAAA): ").strip()

        mod_str = input("  Modificar número de entrada? [s/n]: ").strip().lower()
        modificar_entrada = mod_str == "s"
        numero_entrada: str | None = None
        if modificar_entrada:
            numero_entrada = input("  Número de entrada: ").strip()

        valor_total = input("  Valor total da nota: ").strip()
        nf_valor    = input("  Valor NF: ").strip()
        chave_cte   = input("  Chave CT-e (44 dígitos): ").strip()

        numero_natureza = ""
        while numero_natureza not in ("2", "3"):
            numero_natureza = input("  Número de natureza (2 ou 3): ").strip()

        print("  Cidade de saída:")
        cidade_saida = input("    Nome: ").strip()
        uf_saida = ""
        while len(uf_saida) != 2 or not uf_saida.isalpha():
            uf_saida = input("    UF (2 letras): ").strip().upper()

        print("  Cidade de chegada:")
        cidade_chegada = input("    Nome: ").strip()
        uf_chegada = ""
        while len(uf_chegada) != 2 or not uf_chegada.isalpha():
            uf_chegada = input("    UF (2 letras): ").strip().upper()

        icms_str  = input("  Tem ICMS? [s/n]: ").strip().lower()
        tem_icms  = icms_str == "s"
        porcentagem_icms: str | None = None
        tem_outros = False
        valor_outros: str | None = None

        if tem_icms:
            porcentagem_icms = input("  Porcentagem do ICMS (ex: 12): ").strip()
            outros_str = input("  Tem Outros? [s/n]: ").strip().lower()
            tem_outros = outros_str == "s"
            if tem_outros:
                valor_outros = input("  Valor de Outros: ").strip()

        return DadosNota(
            numero            = numero,
            serie             = serie,
            emissao           = emissao,
            modificar_entrada = modificar_entrada,
            numero_entrada    = numero_entrada,
            valor_total       = valor_total,
            nf_valor          = nf_valor,
            chave_cte         = chave_cte,
            numero_natureza   = numero_natureza,
            cidade_saida      = cidade_saida,
            uf_saida          = uf_saida,
            cidade_chegada    = cidade_chegada,
            uf_chegada        = uf_chegada,
            tem_icms          = tem_icms,
            porcentagem_icms  = porcentagem_icms,
            tem_outros        = tem_outros,
            valor_outros      = valor_outros,
        )
