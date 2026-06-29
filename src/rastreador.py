"""
rastreador.py
--------------
Rastreia execuções, calcula métricas e gerencia histórico de notas.

Função principal:
- Registra cada execução (RPA, tempo, status, notas)
- Organiza notas por dia em ordem crescente
- Calcula tempo médio por RPA
- Permite consultas de histórico
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional
from src.logger import log


@dataclass
class Execucao:
    """Representa uma execução individual de RPA."""
    id: str                          # hash único
    tipo: str                        # "relatorio", "fabrica", "transferencia", "entrada_cte"
    timestamp: str                   # ISO format
    data: str                        # YYYY-MM-DD
    hora_inicio: str                 # HH:MM:SS
    duracao_segundos: float          # tempo total
    status: str                      # "sucesso", "falha", "parcial"
    notas: list[str] = field(default_factory=list)  # números processados
    detalhes: dict = field(default_factory=dict)    # {"nota": True/False}
    erro: Optional[str] = None       # mensagem de erro, se houver


class Rastreador:
    """Gerencia histórico de execuções e cálculo de métricas."""

    def __init__(self, arquivo_historico: str = "data/logs/historico.json") -> None:
        self.arquivo = Path(arquivo_historico)
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self.execucoes: list[Execucao] = []
        self._carregar_historico()

    def _carregar_historico(self) -> None:
        """Carrega execuções do arquivo JSON."""
        if self.arquivo.exists():
            try:
                with open(self.arquivo, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.execucoes = [
                        Execucao(**ex) for ex in dados
                    ]
                log.debug(f"Carregadas {len(self.execucoes)} execuções do histórico")
            except Exception as e:
                log.warning(f"Erro ao carregar histórico: {e}")
                self.execucoes = []
        else:
            self.execucoes = []

    def _salvar_historico(self) -> None:
        """Salva execuções no arquivo JSON."""
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                dados = [asdict(ex) for ex in self.execucoes]
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log.error(f"Erro ao salvar histórico: {e}")

    def registrar_inicio(self, tipo: str) -> dict:
        """
        Marca o início de uma execução.
        Retorna um dict com os dados iniciais para usar no registrar_fim.
        """
        agora = datetime.now()
        return {
            "tipo": tipo,
            "timestamp": agora.isoformat(),
            "data": agora.strftime("%Y-%m-%d"),
            "hora_inicio": agora.strftime("%H:%M:%S"),
            "tempo_inicio": time.time(),
        }

    def registrar_fim(
        self,
        dados_inicio: dict,
        status: str,
        notas: Optional[list[str]] = None,
        detalhes: Optional[dict] = None,
        erro: Optional[str] = None,
    ) -> Execucao:
        """
        Registra o fim de uma execução.

        Parâmetros
        ----------
        dados_inicio:
            Dict retornado por registrar_inicio()
        status:
            "sucesso" | "falha" | "parcial"
        notas:
            Lista de números de notas processados
        detalhes:
            Dict com {"nota": True/False} para cada nota
        erro:
            Mensagem de erro se houver

        Returns
        -------
        Execucao
            Objeto com todos os dados registrados
        """
        duracao = time.time() - dados_inicio["tempo_inicio"]
        id_exec = f"{dados_inicio['data']}_{dados_inicio['hora_inicio'].replace(':', '')}"

        execucao = Execucao(
            id=id_exec,
            tipo=dados_inicio["tipo"],
            timestamp=dados_inicio["timestamp"],
            data=dados_inicio["data"],
            hora_inicio=dados_inicio["hora_inicio"],
            duracao_segundos=duracao,
            status=status,
            notas=notas or [],
            detalhes=detalhes or {},
            erro=erro,
        )

        self.execucoes.append(execucao)
        self._salvar_historico()

        log.info(
            f"[{execucao.tipo.upper()}] "
            f"{status} em {duracao:.1f}s | "
            f"Notas: {', '.join(execucao.notas) if execucao.notas else 'N/A'}"
        )

        return execucao

    # ========================================================================
    #  CONSULTAS E MÉTRICAS
    # ========================================================================

    def ultimas_execucoes(self, limite: int = 10) -> list[Execucao]:
        """Retorna as N últimas execuções em ordem reversa (mais recente primeiro)."""
        return sorted(
            self.execucoes,
            key=lambda x: x.timestamp,
            reverse=True,
        )[:limite]

    def execucoes_por_tipo(self, tipo: str) -> list[Execucao]:
        """Filtra execuções por tipo (relatorio, fabrica, transferencia, entrada_cte)."""
        return [ex for ex in self.execucoes if ex.tipo == tipo]

    def execucoes_por_data(self, data: str) -> list[Execucao]:
        """
        Filtra execuções de uma data específica.
        data: formato YYYY-MM-DD
        """
        return sorted(
            [ex for ex in self.execucoes if ex.data == data],
            key=lambda x: x.hora_inicio,
        )

    def tempo_medio_por_tipo(self) -> dict[str, float]:
        """
        Calcula o tempo médio de execução para cada tipo de RPA.

        Returns
        -------
        dict
            {"fabrica": 45.3, "transferencia": 32.1, ...}
        """
        tipos = set(ex.tipo for ex in self.execucoes)
        resultado = {}

        for tipo in tipos:
            execucoes = self.execucoes_por_tipo(tipo)
            if execucoes:
                media = sum(ex.duracao_segundos for ex in execucoes) / len(execucoes)
                resultado[tipo] = round(media, 1)

        return resultado

    def taxa_sucesso_por_tipo(self) -> dict[str, float]:
        """
        Calcula a taxa de sucesso (%) para cada tipo.

        Returns
        -------
        dict
            {"fabrica": 95.5, "transferencia": 100.0, ...}
        """
        tipos = set(ex.tipo for ex in self.execucoes)
        resultado = {}

        for tipo in tipos:
            execucoes = self.execucoes_por_tipo(tipo)
            if execucoes:
                sucessos = sum(1 for ex in execucoes if ex.status == "sucesso")
                taxa = (sucessos / len(execucoes)) * 100
                resultado[tipo] = round(taxa, 1)

        return resultado

    def historico_notas(self, dias: int = 7) -> dict[str, list[str]]:
        """
        Retorna as notas lançadas nos últimos N dias, organizadas por dia.

        Returns
        -------
        dict
            {
                "2025-01-10": ["123456", "234567", "345678"],  # ordem crescente
                "2025-01-09": ["111111"],
                ...
            }
        """
        limite = (datetime.now() - timedelta(days=dias)).date()
        resultado = {}

        for ex in self.execucoes:
            data_obj = datetime.fromisoformat(ex.data).date()
            if data_obj >= limite and ex.notas:
                if ex.data not in resultado:
                    resultado[ex.data] = []
                resultado[ex.data].extend(ex.notas)

        # Remove duplicatas e ordena crescente
        for data in resultado:
            resultado[data] = sorted(set(resultado[data]))

        # Ordena por data (decrescente)
        return dict(sorted(resultado.items(), reverse=True))

    def notas_por_tipo_e_data(self, dias: int = 7) -> dict[str, dict[str, list[str]]]:
        """
        Retorna notas organizadas por tipo de RPA e data.

        Returns
        -------
        dict
            {
                "2025-01-10": {
                    "fabrica": ["123456", "234567"],
                    "transferencia": ["345678"],
                },
                "2025-01-09": {...},
            }
        """
        limite = (datetime.now() - timedelta(days=dias)).date()
        resultado = {}

        for ex in self.execucoes:
            data_obj = datetime.fromisoformat(ex.data).date()
            if data_obj >= limite and ex.notas:
                if ex.data not in resultado:
                    resultado[ex.data] = {}
                if ex.tipo not in resultado[ex.data]:
                    resultado[ex.data][ex.tipo] = []
                resultado[ex.data][ex.tipo].extend(ex.notas)

        # Remove duplicatas e ordena
        for data in resultado:
            for tipo in resultado[data]:
                resultado[data][tipo] = sorted(set(resultado[data][tipo]))

        # Ordena por data (decrescente)
        return dict(sorted(resultado.items(), reverse=True))

    def resumo_execucoes_recentes(self, limite: int = 10) -> dict:
        """
        Retorna um resumo das últimas execuções para exibição rápida.

        Returns
        -------
        dict
            {
                "total_execucoes": 10,
                "taxa_sucesso_geral": 95.0,
                "tempo_medio_geral": 45.3,
                "ultima_execucao": "2025-01-10 14:35:22",
                "por_tipo": {
                    "fabrica": {
                        "execucoes": 5,
                        "taxa_sucesso": 100.0,
                        "tempo_medio": 50.2,
                    },
                    ...
                },
                "ultimas": [
                    {
                        "tipo": "fabrica",
                        "data": "2025-01-10",
                        "hora": "14:35:22",
                        "duracao": "50.2s",
                        "status": "sucesso",
                        "notas": "123456, 234567",
                    },
                    ...
                ],
            }
        """
        ultimas = self.ultimas_execucoes(limite)
        taxa_sucesso = sum(1 for ex in self.execucoes if ex.status == "sucesso")
        tempo_medio_geral = 0.0

        if self.execucoes:
            taxa_sucesso = (taxa_sucesso / len(self.execucoes)) * 100
            tempo_medio_geral = sum(
                ex.duracao_segundos for ex in self.execucoes
            ) / len(self.execucoes)

        tempo_por_tipo = self.tempo_medio_por_tipo()
        taxa_por_tipo = self.taxa_sucesso_por_tipo()

        por_tipo = {}
        for tipo in set(ex.tipo for ex in self.execucoes):
            execs = self.execucoes_por_tipo(tipo)
            por_tipo[tipo] = {
                "execucoes": len(execs),
                "taxa_sucesso": taxa_por_tipo.get(tipo, 0.0),
                "tempo_medio": tempo_por_tipo.get(tipo, 0.0),
            }

        ultima_exec = ultimas[0] if ultimas else None
        ultima_data = (
            f"{ultima_exec.data} {ultima_exec.hora_inicio}"
            if ultima_exec
            else "Nenhuma"
        )

        return {
            "total_execucoes": len(self.execucoes),
            "taxa_sucesso_geral": round(taxa_sucesso, 1),
            "tempo_medio_geral": round(tempo_medio_geral, 1),
            "ultima_execucao": ultima_data,
            "por_tipo": por_tipo,
            "ultimas": [
                {
                    "tipo": ex.tipo,
                    "data": ex.data,
                    "hora": ex.hora_inicio,
                    "duracao": f"{ex.duracao_segundos:.1f}s",
                    "status": ex.status,
                    "notas": ", ".join(ex.notas) if ex.notas else "N/A",
                }
                for ex in ultimas
            ],
        }

    def limpar_historico(self) -> None:
        """Remove todos os registros (use com cuidado!)."""
        self.execucoes = []
        self._salvar_historico()
        log.warning("Histórico de execuções foi limpo.")
