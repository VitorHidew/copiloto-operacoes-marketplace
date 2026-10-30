import json
import re

from pydantic import ValidationError

from src.models import RespostaCopiloto


def numeros(texto: str) -> set[str]:
    return set(re.findall(r"(?<!\w)-?\d+(?:[.,]\d+)?%?", texto))


def parsear_resposta(texto: str, contexto_serializado: str, modo: str) -> RespostaCopiloto:
    try:
        dados = json.loads(texto)
        dados["modo"] = modo
        resposta = RespostaCopiloto.model_validate(dados)
    except (json.JSONDecodeError, ValidationError, TypeError) as erro:
        return RespostaCopiloto(
            resumo="Resposta inválida; indicadores determinísticos permanecem disponíveis.",
            limitacoes=["Revisão manual necessária.", f"Falha de formato: {type(erro).__name__}."],
            modo=modo,
            valido=False,
        )
    permitidos = numeros(contexto_serializado)
    citados = numeros(json.dumps(dados, ensure_ascii=False))
    inventados = citados - permitidos
    if inventados:
        resposta.valido = False
        resposta.limitacoes.append("A resposta incluiu números ausentes do contexto e requer revisão manual.")
    return resposta
