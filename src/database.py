from pathlib import Path

import duckdb
import pandas as pd


def consultar_csv(caminho: Path, sql: str) -> pd.DataFrame:
    normalizado = sql.strip().lower()
    if not normalizado.startswith("select") or ";" in normalizado.rstrip(";"):
        raise ValueError("Somente uma consulta SELECT é permitida.")
    with duckdb.connect(":memory:") as conexao:
        conexao.read_csv(str(caminho)).create_view("pedidos")
        return conexao.execute(sql).fetch_df()
