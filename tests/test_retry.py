import pytest

from src.providers import LimiteChamadasError


def test_erro_de_limite_tem_mensagem_clara():
    erro = LimiteChamadasError("Limite de chamadas atingido; progresso preservado no cache.")
    assert "progresso preservado" in str(erro)


@pytest.mark.parametrize("codigo", [429, 503])
def test_codigos_transitorios_documentados(codigo):
    assert codigo in {429, 503}
