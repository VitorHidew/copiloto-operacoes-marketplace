from typing import Literal

from pydantic import BaseModel, Field


class Fato(BaseModel):
    indicador: str
    valor: str
    segmento: str
    periodo: str


class RespostaCopiloto(BaseModel):
    resumo: str
    fatos: list[Fato] = Field(default_factory=list)
    interpretacoes: list[str] = Field(default_factory=list)
    hipoteses: list[str] = Field(default_factory=list)
    acoes_sugeridas: list[str] = Field(default_factory=list)
    limitacoes: list[str] = Field(default_factory=list)
    modo: Literal["simulado", "gemini"]
    valido: bool = True


class ResultadoAnalitico(BaseModel):
    periodo: str
    pedidos: int
    faturamento: float
    ticket_medio: float | None
    taxa_cancelamento: float | None
    percentual_atrasos: float | None
    tempo_medio_entrega: float | None
    mediana_tempo_entrega: float | None
    cumprimento_sla: float | None
    avaliacao_media: float | None


class ConfiguracaoConsulta(BaseModel):
    modo: Literal["simulado", "gemini"] = "simulado"
    modelo: str
    versao_prompt: str = "v1"
    pausa: float = Field(default=0, ge=0)
    limite_chamadas: int = Field(default=10, ge=1)
    tentativas: int = Field(default=3, ge=1, le=5)
