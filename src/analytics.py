from typing import Any

import pandas as pd

from src.models import ResultadoAnalitico


def _percentual(numerador: int, denominador: int) -> float | None:
    return None if denominador == 0 else round(numerador / denominador * 100, 2)


def filtrar(frame: pd.DataFrame, **filtros: Any) -> pd.DataFrame:
    dados = frame.copy()
    for coluna in ("regiao", "categoria", "canal", "status"):
        valor = filtros.get(coluna)
        if valor and valor != "Todos":
            dados = dados[dados[coluna] == valor]
    inicio, fim = filtros.get("inicio"), filtros.get("fim")
    if inicio is not None:
        dados = dados[dados["data_hora_pedido"] >= pd.Timestamp(inicio)]
    if fim is not None:
        dados = dados[dados["data_hora_pedido"] <= pd.Timestamp(fim) + pd.Timedelta(days=1)]
    return dados.copy()


def calcular_indicadores(frame: pd.DataFrame, periodo: str = "selecionado") -> ResultadoAnalitico:
    total = len(frame)
    entregues = frame[frame["status"] == "entregue"].copy()
    cancelados = total - len(entregues)
    atrasados = entregues[entregues["tempo_real_min"] > entregues["tempo_estimado_min"]]
    tempos = pd.to_numeric(entregues["tempo_real_min"], errors="coerce").dropna()
    avaliacoes = pd.to_numeric(entregues["avaliacao_cliente"], errors="coerce").dropna()
    faturamento = float(frame.loc[frame["status"] != "cancelado", "valor_pedido"].sum())
    return ResultadoAnalitico(
        periodo=periodo,
        pedidos=total,
        faturamento=round(faturamento, 2),
        ticket_medio=None if len(entregues) == 0 else round(faturamento / len(entregues), 2),
        taxa_cancelamento=_percentual(cancelados, total),
        percentual_atrasos=_percentual(len(atrasados), len(entregues)),
        tempo_medio_entrega=None if tempos.empty else round(float(tempos.mean()), 2),
        mediana_tempo_entrega=None if tempos.empty else round(float(tempos.median()), 2),
        cumprimento_sla=_percentual(len(entregues) - len(atrasados), len(entregues)),
        avaliacao_media=None if avaliacoes.empty else round(float(avaliacoes.mean()), 2),
    )


def comparar_periodos(atual: ResultadoAnalitico, anterior: ResultadoAnalitico) -> dict[str, float | None]:
    resultado: dict[str, float | None] = {}
    for campo in ("pedidos", "faturamento", "ticket_medio", "taxa_cancelamento", "percentual_atrasos"):
        novo, antigo = getattr(atual, campo), getattr(anterior, campo)
        resultado[campo] = None if antigo in (None, 0) or novo is None else round((novo - antigo) / antigo * 100, 2)
    return resultado


def ranking(frame: pd.DataFrame, dimensao: str) -> list[dict[str, Any]]:
    if dimensao not in {"regiao", "categoria", "canal"}:
        raise ValueError("Dimensão não permitida.")
    linhas = []
    for nome, grupo in frame.groupby(dimensao, observed=True):
        metricas = calcular_indicadores(grupo, str(nome))
        linhas.append({dimensao: nome, **metricas.model_dump(exclude={"periodo"})})
    return sorted(linhas, key=lambda item: (item["percentual_atrasos"] or 0), reverse=True)


def contexto_agregado(frame: pd.DataFrame) -> dict[str, Any]:
    return {
        "indicadores": calcular_indicadores(frame).model_dump(),
        "por_regiao": ranking(frame, "regiao"),
        "por_categoria": ranking(frame, "categoria"),
        "aviso": "Dados exclusivamente sintéticos do Mercado Exemplo.",
    }
