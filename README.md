# Copiloto de Operações de Marketplace

Ferramenta de portfólio AI Builder que transforma pedidos sintéticos do **Mercado Exemplo** em indicadores, anomalias, perguntas em linguagem natural e relatório executivo.

> Todos os dados são fictícios. O projeto não representa nem utiliza informações internas de empresas reais.

## Arquitetura e responsabilidades

Python, Pandas e DuckDB calculam métricas, filtros, rankings e anomalias. A IA recebe somente agregações e pode resumir, interpretar e sugerir investigações. Ela não calcula nem altera indicadores. Veja [arquitetura](docs/arquitetura.md).

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Dados sintéticos

```powershell
python -m src.generator --quantidade 80 --semente 42 --saida data/amostra_pedidos.csv
```

A quantidade é configurável; não existe alegação de escala real. A anomalia controlada aumenta atrasos fictícios na região Oeste no trecho final da amostra.

## Modo simulado

```powershell
python -m src.cli --simulado --pergunta "Quais segmentos precisam de investigação?"
streamlit run dashboard/app.py
```

O simulador é determinístico, não usa API e nunca deve ser interpretado como desempenho do Gemini.

## Gemini opcional

O projeto usa o SDK oficial `google-genai`. Obtenha uma chave no [Google AI Studio](https://aistudio.google.com/) e defina `GEMINI_API_KEY` e `GEMINI_MODEL` apenas no ambiente do processo. Use `.env.example` somente como referência e escolha um modelo pequeno da linha Flash disponível em sua conta. Os limites gratuitos variam por modelo e conta; confira-os no AI Studio.

O `.env` não é versionado nem lido automaticamente. O código envia somente indicadores agregados, usa saída JSON, cache em disco, limite de chamadas e tratamento de erro 429. Chamadas reais ao Gemini **não foram verificadas durante o desenvolvimento**.

## Testes

```powershell
python -m pytest -q -p no:cacheprovider
```

## Perguntas suportadas

- Quais regiões lideram atrasos?
- Qual categoria apresenta maior cancelamento?
- Quais indicadores merecem investigação?
- Quais hipóteses podem ser verificadas?

## Privacidade e uso responsável

- somente dados sintéticos e IDs com prefixos fictícios;
- fatos calculados são separados de hipóteses;
- números ausentes do contexto invalidam a resposta;
- resultados exigem revisão humana;
- o projeto não demonstra causalidade nem substitui análise operacional.

## Resultados

| Indicador | Resultado |
|---|---|
| Casos avaliados | [PREENCHER] |
| JSON válido | [PREENCHER] |
| Fatos preservados | [PREENCHER] |
| Tempo manual | [PREENCHER] |
| Tempo com a ferramenta | [PREENCHER] |

## Próximos passos

- avaliação real com API e amostra rotulada;
- autenticação e observabilidade para implantação;
- alertas opcionais via n8n;
- experimentos com outras técnicas explicáveis de anomalia.

## Licença

MIT. Consulte `LICENSE`.
