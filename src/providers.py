import json
import os
import time
from typing import Any, Protocol

from src.models import RespostaCopiloto


class LimiteChamadasError(RuntimeError):
    pass


class Provedor(Protocol):
    def gerar(self, pergunta: str, contexto: dict[str, Any], prompt: str) -> str: ...


class ProvedorSimulado:
    def gerar(self, pergunta: str, contexto: dict[str, Any], prompt: str) -> str:
        indicadores = contexto["indicadores"]
        maior = contexto["por_regiao"][0] if contexto["por_regiao"] else {}
        resposta = {
            "resumo": "Análise simulada baseada somente nos indicadores calculados.",
            "fatos": [{
                "indicador": "percentual_atrasos",
                "valor": str(indicadores["percentual_atrasos"]),
                "segmento": str(maior.get("regiao", "geral")),
                "periodo": str(indicadores["periodo"]),
            }],
            "interpretacoes": ["O segmento no topo do ranking merece investigação."],
            "hipoteses": ["Capacidade operacional e distância podem ser verificadas; não há causalidade comprovada."],
            "acoes_sugeridas": ["Revisar a série temporal e comparar segmentos equivalentes."],
            "limitacoes": ["Resposta simulada; não representa desempenho de um modelo real."],
        }
        return json.dumps(resposta, ensure_ascii=False)


class ProvedorGemini:
    def __init__(self, modelo: str, tentativas: int = 3, pausa: float = 0):
        self.modelo = modelo
        self.tentativas = tentativas
        self.pausa = pausa

    def gerar(self, pergunta: str, contexto: dict[str, Any], prompt: str) -> str:
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY não configurada; use o modo simulado.")
        from google import genai
        from google.genai import errors, types

        cliente = genai.Client()
        conteudo = f"{prompt}\nPERGUNTA:\n{pergunta}\nCONTEXTO JSON:\n{json.dumps(contexto, ensure_ascii=False)}"
        try:
            for tentativa in range(self.tentativas):
                try:
                    if self.pausa:
                        time.sleep(self.pausa)
                    resposta = cliente.models.generate_content(
                        model=self.modelo,
                        contents=conteudo,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=RespostaCopiloto,
                        ),
                    )
                    return resposta.text
                except errors.APIError as erro:
                    if getattr(erro, "code", None) != 429 or tentativa + 1 >= self.tentativas:
                        raise
                    time.sleep(2 ** tentativa)
        finally:
            cliente.close()
        raise RuntimeError("A geração não foi concluída.")
