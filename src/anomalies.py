import pandas as pd


def detectar_iqr(frame: pd.DataFrame, coluna: str = "tempo_real_min") -> pd.DataFrame:
    valores = pd.to_numeric(frame[coluna], errors="coerce").dropna()
    if len(valores) < 4:
        return frame.iloc[0:0].copy()
    q1, q3 = valores.quantile([0.25, 0.75])
    iqr = q3 - q1
    inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return frame[(frame[coluna] < inferior) | (frame[coluna] > superior)].copy()


def serie_diaria(frame: pd.DataFrame) -> pd.DataFrame:
    dados = frame.copy()
    dados["data"] = dados["data_hora_pedido"].dt.date
    dados["atrasado"] = (dados["status"] == "entregue") & (dados["tempo_real_min"] > dados["tempo_estimado_min"])
    return dados.groupby("data", as_index=False).agg(pedidos=("pedido_id", "count"), atrasos=("atrasado", "sum"))
