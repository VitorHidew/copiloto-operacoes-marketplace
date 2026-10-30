import argparse
import json
import os
from pathlib import Path

import pandas as pd

from src.analytics import contexto_agregado
from src.cache import CacheDisco
from src.copilot import Copiloto, ler_prompt
from src.providers import ProvedorGemini, ProvedorSimulado
from src.validation import validar_pedidos


def main() -> int:
    parser = argparse.ArgumentParser(description="Copiloto de operações do Mercado Exemplo.")
    parser.add_argument("--dados", type=Path, default=Path("data/amostra_pedidos.csv"))
    parser.add_argument("--pergunta", default="Quais segmentos precisam de investigação?")
    parser.add_argument("--simulado", action="store_true")
    parser.add_argument("--pausa", type=float, default=0)
    parser.add_argument("--limite-chamadas", type=int, default=10)
    args = parser.parse_args()
    dados = validar_pedidos(pd.read_csv(args.dados))
    contexto = contexto_agregado(dados)
    modelo = os.getenv("GEMINI_MODEL", "CONFIGURE_UM_MODELO_FLASH")
    provedor = ProvedorSimulado() if args.simulado else ProvedorGemini(modelo, pausa=args.pausa)
    copiloto = Copiloto(provedor, CacheDisco(Path("cache")), modelo, args.limite_chamadas)
    prompt = ler_prompt(Path("prompts/copiloto.md"))
    resposta = copiloto.perguntar(args.pergunta, contexto, prompt, "simulado" if args.simulado else "gemini")
    print(json.dumps(resposta.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
