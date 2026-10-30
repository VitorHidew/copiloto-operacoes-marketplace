import pandas as pd


COLUNAS = {
    "pedido_id", "data_hora_pedido", "regiao", "categoria", "canal",
    "valor_pedido", "distancia_km", "tempo_estimado_min", "tempo_real_min",
    "status", "motivo_cancelamento", "avaliacao_cliente",
    "entregador_id_ficticio", "estabelecimento_id_ficticio",
}
REGIOES = {"Norte", "Sul", "Leste", "Oeste"}
CATEGORIAS = {"Mercado", "Casa", "Papelaria", "Cuidados"}
STATUS = {"entregue", "cancelado"}


def validar_pedidos(frame: pd.DataFrame) -> pd.DataFrame:
    faltantes = COLUNAS - set(frame.columns)
    if faltantes:
        raise ValueError(f"Colunas ausentes: {', '.join(sorted(faltantes))}")
    dados = frame.copy()
    if dados["pedido_id"].duplicated().any():
        raise ValueError("Há pedidos duplicados.")
    if not dados["pedido_id"].astype(str).str.startswith("PED-FICT-").all():
        raise ValueError("Todos os identificadores devem ser fictícios.")
    dados["data_hora_pedido"] = pd.to_datetime(dados["data_hora_pedido"], errors="coerce")
    if dados["data_hora_pedido"].isna().any():
        raise ValueError("Há datas inválidas.")
    for coluna in ("valor_pedido", "distancia_km", "tempo_estimado_min"):
        if pd.to_numeric(dados[coluna], errors="coerce").isna().any() or (dados[coluna] < 0).any():
            raise ValueError(f"Valores inválidos em {coluna}.")
    if not set(dados["regiao"]).issubset(REGIOES):
        raise ValueError("Há regiões desconhecidas.")
    if not set(dados["categoria"]).issubset(CATEGORIAS):
        raise ValueError("Há categorias desconhecidas.")
    if not set(dados["status"]).issubset(STATUS):
        raise ValueError("Há status desconhecidos.")
    return dados.sort_values("data_hora_pedido").reset_index(drop=True)
