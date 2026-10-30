import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import calcular_indicadores, contexto_agregado, filtrar, ranking
from src.anomalies import detectar_iqr, serie_diaria
from src.cache import CacheDisco
from src.copilot import Copiloto, ler_prompt
from src.providers import ProvedorGemini, ProvedorSimulado
from src.reports import relatorio_markdown
from src.validation import validar_pedidos


st.set_page_config(page_title="Copiloto de Operações", layout="wide")
st.title("Copiloto de Operações do Mercado Exemplo")
st.caption("Demonstração com dados exclusivamente sintéticos.")
dados = validar_pedidos(pd.read_csv("data/amostra_pedidos.csv"))

with st.sidebar:
    modo = st.radio("Modo", ["simulado", "gemini"])
    regiao = st.selectbox("Região", ["Todos", *sorted(dados.regiao.unique())])
    categoria = st.selectbox("Categoria", ["Todos", *sorted(dados.categoria.unique())])
    canal = st.selectbox("Canal", ["Todos", *sorted(dados.canal.unique())])
    status = st.selectbox("Status", ["Todos", *sorted(dados.status.unique())])

recorte = filtrar(dados, regiao=regiao, categoria=categoria, canal=canal, status=status)
metricas = calcular_indicadores(recorte)
colunas = st.columns(6)
for coluna, (rotulo, valor) in zip(colunas, [
    ("Pedidos", metricas.pedidos), ("Faturamento fictício", metricas.faturamento),
    ("Ticket médio", metricas.ticket_medio), ("Atrasos %", metricas.percentual_atrasos),
    ("Cancelamento %", metricas.taxa_cancelamento), ("SLA %", metricas.cumprimento_sla),
]):
    coluna.metric(rotulo, "N/D" if valor is None else valor)

serie = serie_diaria(recorte)
st.plotly_chart(px.line(serie, x="data", y=["pedidos", "atrasos"], title="Série diária"), width="stretch")
st.plotly_chart(px.bar(pd.DataFrame(ranking(recorte, "regiao")), x="regiao", y="percentual_atrasos", title="Atrasos por região"), width="stretch")
st.write(f"Anomalias IQR encontradas: {len(detectar_iqr(recorte))}")

st.subheader("Copiloto")
pergunta = st.text_input("Pergunta", "Quais segmentos precisam de investigação?")
if st.button("Analisar"):
    modelo = os.getenv("GEMINI_MODEL", "CONFIGURE_UM_MODELO_FLASH")
    provedor = ProvedorSimulado() if modo == "simulado" else ProvedorGemini(modelo)
    agente = Copiloto(provedor, CacheDisco(Path("cache")), modelo)
    resposta = agente.perguntar(pergunta, contexto_agregado(recorte), ler_prompt(Path("prompts/copiloto.md")), modo)
    st.warning(f"Modo {modo.upper()}")
    st.json(resposta.model_dump())
    relatorio = relatorio_markdown(metricas, resposta)
    st.download_button("Baixar relatório Markdown", relatorio, "relatorio.md")
