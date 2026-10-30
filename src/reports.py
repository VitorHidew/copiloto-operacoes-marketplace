from src.models import RespostaCopiloto, ResultadoAnalitico


def relatorio_markdown(indicadores: ResultadoAnalitico, resposta: RespostaCopiloto) -> str:
    linhas = [
        "# Relatório operacional fictício",
        "",
        f"> Modo: **{resposta.modo.upper()}**. Dados exclusivamente sintéticos.",
        "",
        "## Indicadores calculados",
        "",
        f"- Pedidos: {indicadores.pedidos}",
        f"- Faturamento fictício: {indicadores.faturamento}",
        f"- Ticket médio: {indicadores.ticket_medio}",
        f"- Cancelamento: {indicadores.taxa_cancelamento}%",
        f"- Atrasos: {indicadores.percentual_atrasos}%",
        "",
        "## Interpretação assistida",
        "",
        resposta.resumo,
        "",
        "## Limitações",
        "",
        *[f"- {item}" for item in resposta.limitacoes],
    ]
    return "\n".join(linhas) + "\n"
