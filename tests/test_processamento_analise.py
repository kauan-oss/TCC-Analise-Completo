"""Testes dos cálculos e dos principais casos de entrada."""

import io

import pandas as pd
import pytest

from analise import comparacao_perfis, estatisticas_escala, frequencias
from processamento import COLUNAS_PADRAO, aplicar_filtros, carregar_e_limpar


def base(perfis=("Aluno", "Professor")):
    """Cria uma pequena base determinística para os testes."""
    linhas = []
    for indice, perfil in enumerate(perfis, start=1):
        linhas.append({
            "data_resposta": f"2026-07-0{indice}",
            "perfil": perfil,
            "frequencia_uso": indice,
            "uso_pessoal": 3,
            "uso_profissional": 4,
            "uso_academico": 5,
            "ia_mais_utilizada": "ChatGPT",
            "ganho_produtividade": 4,
            "confianca_respostas": 3,
            "verifica_fontes": 2,
            "preocupacao_plagio": 5,
            "preocupacao_raciocinio_critico": 4,
        })
    return pd.DataFrame(linhas)


def como_csv(dados):
    """Converte DataFrame em bytes de CSV."""
    return dados.to_csv(index=False).encode("utf-8")


def test_csv_padronizado_e_estatisticas():
    tratados, relatorio = carregar_e_limpar(como_csv(base()), "teste.csv")
    resumo = estatisticas_escala(tratados, "ganho_produtividade")
    assert len(tratados) == 2
    assert resumo["media"] == 4
    assert resumo["percentual_4_5"] == 100
    assert relatorio["duplicadas"] == 0


def test_xlsx_e_multiplas_planilhas():
    memoria = io.BytesIO()
    with pd.ExcelWriter(memoria, engine="openpyxl") as escritor:
        base().to_excel(escritor, index=False, sheet_name="Respostas")
        base().to_excel(escritor, index=False, sheet_name="Outra")
    tratados, relatorio = carregar_e_limpar(memoria.getvalue(), "teste.xlsx")
    assert len(tratados) == 2
    assert "várias planilhas" in relatorio["avisos"][0]


@pytest.mark.parametrize("perfis", [("Aluno",), ("Professor",)])
def test_base_com_apenas_um_perfil(perfis):
    tratados, _ = carregar_e_limpar(como_csv(base(perfis)), "teste.csv")
    comparacao = comparacao_perfis(tratados)
    assert len(comparacao) == 9


def test_ausente_invalido_duplicata_e_filtro():
    dados = base(("Aluno", "Professor"))
    dados.loc[0, "confianca_respostas"] = None
    dados["verifica_fontes"] = dados["verifica_fontes"].astype("object")
    dados.loc[1, "verifica_fontes"] = "valor impossível"
    dados = pd.concat([dados, dados.iloc[[0]]], ignore_index=True)
    tratados, relatorio = carregar_e_limpar(como_csv(dados), "teste.csv")
    filtrados = aplicar_filtros(tratados, perfil="Aluno", incluir_duplicadas=False)
    assert relatorio["duplicadas"] == 1
    assert relatorio["valores_invalidos"]["verifica_fontes"] == 1
    assert len(filtrados) == 1


def test_coluna_ausente_e_arquivo_vazio():
    dados = base().drop(columns=["perfil"])
    with pytest.raises(ValueError, match="perfil"):
        carregar_e_limpar(como_csv(dados), "teste.csv")
    with pytest.raises(ValueError, match="vazio"):
        carregar_e_limpar(b"", "teste.csv")


def test_frequencias_mantem_cinco_categorias():
    tratados, _ = carregar_e_limpar(como_csv(base()), "teste.csv")
    tabela = frequencias(tratados, "frequencia_uso")
    assert tabela["categoria"].tolist() == [1, 2, 3, 4, 5]
    assert round(tabela["percentual"].sum(), 6) == 100
