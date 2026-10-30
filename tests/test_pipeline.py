import json
from pathlib import Path

import pandas as pd
import pytest

from src.analytics import calcular_indicadores, comparar_periodos, contexto_agregado, filtrar, ranking
from src.anomalies import detectar_iqr
from src.cache import CacheDisco, chave_cache
from src.copilot import Copiloto
from src.database import consultar_csv
from src.generator import gerar_pedidos
from src.parser import parsear_resposta
from src.providers import LimiteChamadasError, ProvedorSimulado
from src.validation import validar_pedidos


def dados(n=80):
    return validar_pedidos(gerar_pedidos(n, 42))


def test_geracao_reproduzivel():
    pd.testing.assert_frame_equal(gerar_pedidos(20, 7), gerar_pedidos(20, 7))


def test_validacao_rejeita_duplicidade_e_valor_negativo():
    frame = gerar_pedidos(5)
    frame.loc[1, "pedido_id"] = frame.loc[0, "pedido_id"]
    with pytest.raises(ValueError, match="duplicados"):
        validar_pedidos(frame)
    frame = gerar_pedidos(5)
    frame.loc[0, "valor_pedido"] = -1
    with pytest.raises(ValueError, match="valor_pedido"):
        validar_pedidos(frame)


def test_indicadores_filtros_ranking_e_comparacao():
    frame = dados()
    norte = filtrar(frame, regiao="Norte")
    atual, anterior = calcular_indicadores(norte), calcular_indicadores(frame)
    assert atual.pedidos == len(norte)
    assert ranking(frame, "regiao")
    assert "pedidos" in comparar_periodos(atual, anterior)


def test_amostra_vazia_e_pequena():
    vazio = dados().iloc[0:0]
    assert calcular_indicadores(vazio).ticket_medio is None
    assert detectar_iqr(dados(3)).empty


def test_parser_invalido_e_numero_inventado():
    assert not parsear_resposta("não-json", "{}", "simulado").valido
    texto = json.dumps({"resumo":"99", "fatos":[], "interpretacoes":[], "hipoteses":[], "acoes_sugeridas":[], "limitacoes":[]})
    assert not parsear_resposta(texto, '{"valor": 10}', "simulado").valido


def test_cache_retomada_e_limite(tmp_path):
    cache = CacheDisco(tmp_path)
    contexto = contexto_agregado(dados(20))
    agente = Copiloto(ProvedorSimulado(), cache, "simulado", limite=1)
    primeira = agente.perguntar("pergunta", contexto, "prompt", "simulado")
    segunda = agente.perguntar("pergunta", contexto, "prompt", "simulado")
    assert primeira == segunda
    with pytest.raises(LimiteChamadasError):
        agente.perguntar("outra", contexto, "prompt", "simulado")
    assert chave_cache("m", "p", "q", {}) == chave_cache("m", "p", "q", {})


def test_duckdb_select_e_bloqueio(tmp_path):
    arquivo = tmp_path / "dados.csv"
    gerar_pedidos(5).to_csv(arquivo, index=False)
    assert consultar_csv(arquivo, "SELECT count(*) AS total FROM pedidos").iloc[0, 0] == 5
    with pytest.raises(ValueError):
        consultar_csv(arquivo, "DELETE FROM pedidos")
