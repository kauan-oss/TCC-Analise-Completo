"""Cálculos descritivos usados pela dashboard."""

from __future__ import annotations

import pandas as pd

from processamento import COLUNAS_ESCALA, ROTULOS_ESCALA, TITULOS


def formatar(valor: object, casas: int = 2) -> str:
    """Formata números e preserva a indicação de dado ausente."""
    if valor is None or pd.isna(valor):
        return "Sem dados"
    return f"{float(valor):.{casas}f}".replace(".", ",")


def modas(serie: pd.Series) -> list:
    """Retorna todas as modas, inclusive quando há empate."""
    validos = serie.dropna()
    return [] if validos.empty else validos.mode().tolist()


def frequencias(dados: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Calcula frequências absoluta, relativa e percentual."""
    validos = dados[coluna].dropna()
    if coluna in ROTULOS_ESCALA:
        categorias = list(range(1, 6))
        nomes = ROTULOS_ESCALA[coluna]
    else:
        categorias = validos.value_counts().index.tolist()
        nomes = {categoria: str(categoria) for categoria in categorias}
    total = len(validos)
    linhas = []
    for categoria in categorias:
        quantidade = int((validos == categoria).sum())
        relativa = quantidade / total if total else 0.0
        linhas.append({
            "categoria": categoria,
            "resposta": nomes[categoria],
            "frequencia": quantidade,
            "frequencia_relativa": relativa,
            "percentual": relativa * 100,
        })
    return pd.DataFrame(linhas)


def estatisticas_escala(dados: pd.DataFrame, coluna: str) -> dict:
    """Resume uma variável ordinal e trata amostras pequenas."""
    serie = dados[coluna].dropna().astype(float)
    total = len(dados)
    validas = len(serie)
    resultado = {
        "questao": TITULOS[coluna],
        "validas": validas,
        "ausentes": total - validas,
        "media": serie.mean() if validas else pd.NA,
        "mediana": serie.median() if validas else pd.NA,
        "moda": " / ".join(str(int(valor)) for valor in modas(serie)) or "Sem dados",
        "minimo": serie.min() if validas else pd.NA,
        "maximo": serie.max() if validas else pd.NA,
        "amplitude": serie.max() - serie.min() if validas else pd.NA,
        "variancia": serie.var(ddof=1) if validas > 1 else pd.NA,
        "desvio_padrao": serie.std(ddof=1) if validas > 1 else pd.NA,
        "q1": serie.quantile(0.25) if validas else pd.NA,
        "q3": serie.quantile(0.75) if validas else pd.NA,
        "percentual_4_5": float(serie.ge(4).mean() * 100) if validas else pd.NA,
    }
    resultado["intervalo_interquartil"] = (
        resultado["q3"] - resultado["q1"] if validas else pd.NA
    )
    resultado["denominador_4_5"] = validas
    return resultado


def resumo_categorica(dados: pd.DataFrame, coluna: str) -> dict:
    """Resume uma variável nominal sem calcular média."""
    serie = dados[coluna].dropna()
    valores_moda = modas(serie)
    return {
        "total_valido": len(serie),
        "total_ausente": int(dados[coluna].isna().sum()),
        "moda": " / ".join(str(valor) for valor in valores_moda) or "Sem dados",
        "frequencias": frequencias(dados, coluna),
    }


def tabela_estatisticas(dados: pd.DataFrame, colunas: list[str] | None = None) -> pd.DataFrame:
    """Cria a tabela consolidada das escalas selecionadas."""
    linhas = [estatisticas_escala(dados, coluna) for coluna in (colunas or COLUNAS_ESCALA)]
    return pd.DataFrame(linhas)


def comparacao_perfis(dados: pd.DataFrame) -> pd.DataFrame:
    """Compara alunos e professores apenas de forma descritiva."""
    linhas = []
    for coluna in COLUNAS_ESCALA:
        aluno = estatisticas_escala(dados[dados["perfil"] == "Aluno"], coluna)
        professor = estatisticas_escala(dados[dados["perfil"] == "Professor"], coluna)
        diferenca = pd.NA
        if not pd.isna(aluno["media"]) and not pd.isna(professor["media"]):
            diferenca = abs(aluno["media"] - professor["media"])
        linhas.append({
            "questao": TITULOS[coluna],
            "media_alunos": aluno["media"],
            "media_professores": professor["media"],
            "mediana_alunos": aluno["mediana"],
            "mediana_professores": professor["mediana"],
            "moda_alunos": aluno["moda"],
            "moda_professores": professor["moda"],
            "desvio_alunos": aluno["desvio_padrao"],
            "desvio_professores": professor["desvio_padrao"],
            "percentual_4_5_alunos": aluno["percentual_4_5"],
            "percentual_4_5_professores": professor["percentual_4_5"],
            "diferenca_absoluta_medias": diferenca,
        })
    return pd.DataFrame(linhas)


def indicadores(dados: pd.DataFrame) -> dict:
    """Calcula os indicadores dos cartões da visão geral."""
    frequencia = estatisticas_escala(dados, "frequencia_uso")
    produtividade = estatisticas_escala(dados, "ganho_produtividade")
    fontes = estatisticas_escala(dados, "verifica_fontes")
    ferramenta = resumo_categorica(dados, "ia_mais_utilizada")
    return {
        "total": len(dados),
        "alunos": int(dados["perfil"].eq("Aluno").sum()),
        "professores": int(dados["perfil"].eq("Professor").sum()),
        "ferramenta": ferramenta["moda"],
        "mediana_frequencia": frequencia["mediana"],
        "media_frequencia": frequencia["media"],
        "uso_frequente": frequencia["percentual_4_5"],
        "produtividade_alta": produtividade["percentual_4_5"],
        "verificacao_frequente": fontes["percentual_4_5"],
    }


def texto_resultado(dados: pd.DataFrame, coluna: str, descricao: str) -> str:
    """Produz uma frase neutra para respostas 4 ou 5."""
    resumo = estatisticas_escala(dados, coluna)
    if not resumo["validas"]:
        return f"Não há respostas válidas para {descricao} no recorte atual."
    percentual = formatar(resumo["percentual_4_5"])
    return (
        f"Entre as {resumo['validas']} respostas válidas para {descricao}, "
        f"{percentual}% foram classificadas nas categorias 4 ou 5."
    )
