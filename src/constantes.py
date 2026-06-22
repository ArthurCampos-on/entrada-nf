"""
constantes.py — Constantes globais e nomes canônicos de imagens do NBS Agent.

Uso:
    from src.constantes import VERSAO, MENU_ITENS, ImgRelatorio, ImgFabrica

    print(VERSAO)
    self.tela.clicar(ImgRelatorio.EMPRESA_CAMPO)
"""

# ─────────────────────────────────────────────────────────────────────────────
#  Metadados do sistema
# ─────────────────────────────────────────────────────────────────────────────

VERSAO = "1.1.0"

# ─────────────────────────────────────────────────────────────────────────────
#  Itens do menu principal
# ─────────────────────────────────────────────────────────────────────────────

MENU_ITENS: list[str] = [
    "Relatório diário",
    "Fábrica",
    "Transferência",
    "Entrada CT-e",
    "Status",
    "Sair",
]

# ─────────────────────────────────────────────────────────────────────────────
#  Nomes canônicos de imagens por RPA
#  (devem bater 100% com os arquivos em imagens/)
# ─────────────────────────────────────────────────────────────────────────────


class ImgRelatorio:
    """Imagens usadas pelo RPA de relatório de compras."""

    EMPRESA_CAMPO      = "campo_empresa"
    EMPRESA_DUNA       = "empresa_duna_tubarao"
    DATA_ENTRADA       = "entrada_data_relatorio"
    DATA_EMISSAO       = "emissao_data_relatorio"
    BTN_PESQUISA       = "botao_pesquisa_relatorio"
    ABA_NOTA           = "botao_nota_relatorio"
    BTN_IMPRIMIR_LISTA = "btn_imprimir_lista"
    BTN_SIM            = "botao_sim"
    ICONE_IMPRESSAO    = "botao_icone_impressao_relatorio"
    ABA_IMPRESSAO      = "aba_ipressao_relatorio"   # nome real no disco (com "i")


class ImgTransferencia:
    """Imagens usadas pelo RPA de transferência."""

    BTN_INCLUIR        = "botao_incluir"
    BTN_TRANSFERENCIA  = "botao_transferencia"
    BTN_INTERFACE      = "btn_interface"
    BTN_SAIDA          = "btn_interface_saida"
    BTN_PESQUISAR      = "btn_pesquisar_transf"
    BTN_ACEITAR        = "btn_aceitar"
    ABA_LOCACAO        = "aba_locacao"
    CAMPO_LOCACAO      = "campo_locacao"
    PRINCIPAL_PECAS    = "principal_pecas"
    LOCACAO_PADRAO     = "locacao_padrao"
    BTN_CONFIRMAR      = "btn_confirmar"


class ImgFabrica:
    """Imagens usadas pelo RPA de fábrica."""

    BTN_INCLUIR        = "botao_incluir"
    BTN_COMPRA         = "botao_compra"
    BTN_INTERFACE      = "btn_interface"
    PLACEHOLDER_NOTA   = "placeholder_nota_fabrica"
    BTN_PESQUISAR      = "btn_pesquisar_nota"
    ABA_TRIBUTACAO     = "aba_definir_tributacao"
    AREA_CENTRO        = "area_centro"
    DEFINIR_CFOP       = "definir_cfop"
    CAMPO_TRIBUTADOS   = "campo_tributados"
    SELECAO_PECAS      = "selecao_pecas_acessorios"
    BTN_OK             = "btn_ok"
    BTN_ACEITAR        = "btn_aceitar"
    ABA_CRUZAMENTO     = "aba_cruzamento_pedidos"
    SETA_CRUZAMENTO    = "seta_cruzamento"
    BTN_CONF_PEDIDO    = "botao_confirmar"
    ABA_LOCACAO        = "aba_locacao"
    CAMPO_LOCACAO      = "campo_locacao"
    PRINCIPAL_PECAS    = "principal_pecas"
    LOCACAO_PADRAO     = "locacao_padrao"
    ABA_FINANCEIRO     = "aba_financeiro"
    BTN_CONF_FINAL     = "btn_confirmar_final"


class ImgEntradaCte:
    """Imagens usadas pelo RPA de entrada CT-e."""

    ADM_ABA            = "adm_aba"
    NBS_FISCAL         = "nbs_fiscal"
    ENTRADA_CTE        = "entrada_cte"
    INCLUIR_ICONE      = "incluir_icone"
    PERSONA            = "persona"
    ICONE_PESQUISA     = "icone_pesquisa"
    ACEITAR_ICONE      = "aceitar_icone"
    NUMERO_NOTA        = "numerode_nota"
    MODELO_FISCAL      = "modelo_fiscal"
    BARRA_MODELO       = "barra_modelo"
    CODIGO_57          = "codigo_57"
    BARRA_NATUREZA     = "barra_natureza"
    CFOPS              = "cfops"
    CODIGO_NATUREZA    = "codigo_natureza"
    TRIBUTAVEL         = "tributavel_codigo"
    NAO_TRIBUTAVEL     = "naotributavel_codigo"
    VERDE_ACEITAR      = "verde_aceitar"
    ADICAO             = "adicao"
    CONTABILIZACAO     = "contabilizacao"
    RAIO               = "raio"
    FATURAMENTO        = "faturamento"
    SETA_PRETA         = "seta_preta"
    CONFIRMAR          = "confirmar"
    CANCELAR           = "cancelar"   # pendente: capturar quando botão for adicionado
