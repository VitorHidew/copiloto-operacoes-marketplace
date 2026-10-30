import hashlib
import json
from pathlib import Path
from typing import Any


def chave_cache(modelo: str, prompt: str, pergunta: str, contexto: dict[str, Any]) -> str:
    conteudo = json.dumps([modelo, prompt, pergunta, contexto], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(conteudo.encode()).hexdigest()


class CacheDisco:
    def __init__(self, diretorio: Path):
        self.diretorio = diretorio
        self.diretorio.mkdir(parents=True, exist_ok=True)

    def ler(self, chave: str) -> str | None:
        arquivo = self.diretorio / f"{chave}.json"
        return arquivo.read_text(encoding="utf-8") if arquivo.exists() else None

    def salvar(self, chave: str, conteudo: str) -> None:
        temporario = self.diretorio / f"{chave}.tmp"
        temporario.write_text(conteudo, encoding="utf-8")
        temporario.replace(self.diretorio / f"{chave}.json")
