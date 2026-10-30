import json
from pathlib import Path
from typing import Any

from src.cache import CacheDisco, chave_cache
from src.parser import parsear_resposta
from src.providers import LimiteChamadasError, Provedor


class Copiloto:
    def __init__(self, provedor: Provedor, cache: CacheDisco, modelo: str, limite: int = 10):
        self.provedor = provedor
        self.cache = cache
        self.modelo = modelo
        self.limite = limite
        self.chamadas = 0

    def perguntar(self, pergunta: str, contexto: dict[str, Any], prompt: str, modo: str):
        chave = chave_cache(self.modelo, prompt, pergunta, contexto)
        texto = self.cache.ler(chave)
        if texto is None:
            if self.chamadas >= self.limite:
                raise LimiteChamadasError("Limite de chamadas atingido; progresso preservado no cache.")
            texto = self.provedor.gerar(pergunta, contexto, prompt)
            self.cache.salvar(chave, texto)
            self.chamadas += 1
        return parsear_resposta(texto, json.dumps(contexto, ensure_ascii=False), modo)


def ler_prompt(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")
