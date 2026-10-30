import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


REGIOES = ("Norte", "Sul", "Leste", "Oeste")
CATEGORIAS = ("Mercado", "Casa", "Papelaria", "Cuidados")
CANAIS = ("aplicativo", "web")
MOTIVOS = ("indisponibilidade", "endereco_incompleto", "desistencia")


def gerar_pedidos(quantidade: int, semente: int = 42, anomalia: bool = True) -> pd.DataFrame:
    if quantidade < 1:
        raise ValueError("A quantidade deve ser positiva.")
    rng = random.Random(semente)
    inicio = datetime(2026, 1, 1, 8)
    pedidos: list[dict] = []
    for indice in range(quantidade):
        data = inicio + timedelta(hours=12 * indice)
        regiao = rng.choice(REGIOES)
        categoria = rng.choice(CATEGORIAS)
        canal = rng.choice(CANAIS)
        estimado = rng.randint(20, 55)
        atraso_extra = rng.randint(-8, 18)
        if anomalia and indice >= int(quantidade * 0.8) and regiao == "Oeste":
            atraso_extra += 25
        cancelado = rng.random() < (0.18 if categoria == "Casa" else 0.08)
        status = "cancelado" if cancelado else "entregue"
        real = None if cancelado else max(8, estimado + atraso_extra)
        pedidos.append(
            {
                "pedido_id": f"PED-FICT-{indice + 1:05d}",
                "data_hora_pedido": data.isoformat(),
                "regiao": regiao,
                "categoria": categoria,
                "canal": canal,
                "valor_pedido": round(rng.uniform(18, 240), 2),
                "distancia_km": round(rng.uniform(0.8, 18), 2),
                "tempo_estimado_min": estimado,
                "tempo_real_min": real,
                "status": status,
                "motivo_cancelamento": rng.choice(MOTIVOS) if cancelado else None,
                "avaliacao_cliente": None if cancelado else rng.randint(1, 5),
                "entregador_id_ficticio": f"ENT-FICT-{rng.randint(1, 20):03d}",
                "estabelecimento_id_ficticio": f"EST-FICT-{rng.randint(1, 12):03d}",
            }
        )
    return pd.DataFrame(pedidos)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera pedidos sintéticos do Mercado Exemplo.")
    parser.add_argument("--quantidade", type=int, default=80)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=Path("data/amostra_pedidos.csv"))
    parser.add_argument("--sem-anomalia", action="store_true")
    args = parser.parse_args()
    frame = gerar_pedidos(args.quantidade, args.semente, not args.sem_anomalia)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.saida, index=False)
    print(f"Amostra sintética criada em {args.saida}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
