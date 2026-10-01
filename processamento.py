"""Leitura, reconhecimento e limpeza das respostas do questionário."""

from __future__ import annotations

import csv
import io
import re
import unicodedata
from pathlib import Path

import pandas as pd


COLUNAS_PADRAO = [
    "data_resposta",
    "perfil",
    "frequencia_uso",
    "uso_pessoal",
    "uso_profissional",
    "uso_academico",
    "ia_mais_utilizada",
    "ganho_produtividade",
    "confianca_respostas",
    "verifica_fontes",
    "preocupacao_plagio",
    "preocupacao_raciocinio_critico",
]

COLUNAS_OBRIGATORIAS = COLUNAS_PADRAO[1:]

COLUNAS_ESCALA = [
    "frequencia_uso",
    "uso_pessoal",
    "uso_profissional",
    "uso_academico",
    "ganho_produtividade",
    "confianca_respostas",
    "verifica_fontes",
    "preocupacao_plagio",
    "preocupacao_raciocinio_critico",
]

TITULOS = {
    "data_resposta": "Data da resposta",
    "perfil": "Perfil",
    "frequencia_uso": "Frequência geral de uso",
    "uso_pessoal": "Uso para fins pessoais",
    "uso_profissional": "Uso para fins profissionais",
    "uso_academico": "Uso para fins acadêmicos",
    "ia_mais_utilizada": "Ferramenta de IA mais utilizada",
    "ganho_produtividade": "Ganho de produtividade percebido",
    "confianca_respostas": "Confiança nas respostas",
    "verifica_fontes": "Verificação das fontes",
    "preocupacao_plagio": "Preocupação com plágio",
    "preocupacao_raciocinio_critico": "Preocupação com o raciocínio crítico",
}

ROTULOS_ESCALA = {
    "frequencia_uso": {
        1: "Nunca ou raramente", 2: "Poucas vezes", 3: "Às vezes",
        4: "Frequentemente", 5: "Muito frequentemente",
    },
    "uso_pessoal": {
        1: "Nunca ou raramente", 2: "Poucas vezes", 3: "Às vezes",
        4: "Frequentemente", 5: "Muito frequentemente",
    },
    "uso_profissional": {
        1: "Nunca ou raramente", 2: "Poucas vezes", 3: "Às vezes",
        4: "Frequentemente", 5: "Muito frequentemente",
    },
    "uso_academico": {
        1: "Nunca ou raramente", 2: "Poucas vezes", 3: "Às vezes",
        4: "Frequentemente", 5: "Muito frequentemente",
    },
    "ganho_produtividade": {
        1: "Muito baixo", 2: "Baixo", 3: "Moderado",
        4: "Alto", 5: "Muito alto",
    },
    "confianca_respostas": {
        1: "Não confio", 2: "Confio pouco", 3: "Confio moderadamente",
        4: "Confio muito", 5: "Confio totalmente",
    },
    "verifica_fontes": {
        1: "Nunca ou raramente", 2: "Poucas vezes", 3: "Às vezes",
        4: "Frequentemente", 5: "Muito frequentemente",
    },
    "preocupacao_plagio": {
        1: "Nada preocupado", 2: "Pouco preocupado",
        3: "Moderadamente preocupado", 4: "Muito preocupado",
        5: "Extremamente preocupado",
    },
    "preocupacao_raciocinio_critico": {
        1: "Nada preocupado", 2: "Pouco preocupado",
        3: "Moderadamente preocupado", 4: "Muito preocupado",
        5: "Extremamente preocupado",
    },
}

FERRAMENTAS = [
    "ChatGPT", "Claude", "DeepSeek", "Perplexity", "Gemini",
    "Nenhuma dessas opções",
]

PALAVRAS_COLUNAS = {
    "data_resposta": [["carimbo", "data"], ["timestamp"], ["data", "hora"]],
    "perfil": [["aluno", "professor"], ["vinculo", "instituicao"], ["perfil"]],
    "frequencia_uso": [["frequencia", "algum", "inteligencia"], ["media", "vezes", "dia"]],
    "uso_pessoal": [["fins", "pessoais"], ["uso", "pessoal"]],
    "uso_profissional": [["fins", "profissionais"], ["uso", "profissional"]],
    "uso_academico": [["fins", "academicos"], ["uso", "academico"]],
    "ia_mais_utilizada": [["ferramenta", "maior", "frequencia"], ["ia", "mais", "utilizada"]],
    "ganho_produtividade": [["ganho", "produtividade"], ["aumenta", "produtividade"]],
    "confianca_respostas": [["confianca", "respostas"], ["nivel", "confianca"]],
    "verifica_fontes": [["verifica", "fontes"], ["confirma", "informacoes"]],
    "preocupacao_plagio": [["preocupacao", "plagio"]],
    "preocupacao_raciocinio_critico": [["preocupacao", "raciocinio", "critico"]],
}


def normalizar_texto(valor: object) -> str:
    """Cria texto comparável sem alterar o valor exibido ao usuário."""
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    texto = texto.casefold()
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def ler_csv(conteudo: bytes) -> pd.DataFrame:
    """Lê CSV tentando codificações e separadores comuns."""
    ultimo_erro: Exception | None = None
    for codificacao in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            texto = conteudo.decode(codificacao)
            amostra = texto[:100_000]
            try:
                separador = csv.Sniffer().sniff(amostra, delimiters=",;\t").delimiter
            except csv.Error:
                separador = ";" if amostra.count(";") > amostra.count(",") else ","
            return pd.read_csv(io.StringIO(texto), sep=separador)
        except (UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as erro:
            ultimo_erro = erro
    raise ValueError(f"Não foi possível ler o CSV: {ultimo_erro}")


def ler_arquivo(origem: str | Path | bytes, nome: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Lê CSV ou XLSX e devolve a tabela com avisos de leitura."""
    avisos: list[str] = []
    if isinstance(origem, bytes):
        conteudo = origem
        sufixo = Path(nome or "").suffix.lower()
    else:
        caminho = Path(origem)
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        conteudo = caminho.read_bytes()
        sufixo = caminho.suffix.lower()
    if not conteudo:
        raise ValueError("O arquivo está vazio.")
    if sufixo == ".csv":
        return ler_csv(conteudo), avisos
    if sufixo == ".xlsx":
        try:
            planilhas = pd.ExcelFile(io.BytesIO(conteudo))
            primeira = planilhas.sheet_names[0]
            if len(planilhas.sheet_names) > 1:
                avisos.append(f"O Excel possui várias planilhas; foi usada '{primeira}'.")
            return pd.read_excel(planilhas, sheet_name=primeira), avisos
        except ImportError as erro:
            raise ValueError("Instale openpyxl para ler arquivos XLSX.") from erro
    raise ValueError("Formato não aceito. Envie um arquivo CSV ou XLSX.")


def reconhecer_colunas(dados: pd.DataFrame) -> tuple[dict[str, str], list[str], list[str]]:
    """Identifica colunas por nome padronizado ou conjuntos de palavras-chave."""
    mapa: dict[str, str] = {}
    usadas: set[str] = set()
    for original in dados.columns:
        normalizada = normalizar_texto(original)
        for padrao, alternativas in PALAVRAS_COLUNAS.items():
            if padrao in mapa:
                continue
            nome_exato = normalizada == normalizar_texto(padrao)
            palavras_encontradas = any(
                all(palavra in normalizada for palavra in conjunto)
                for conjunto in alternativas
            )
            if nome_exato or palavras_encontradas:
                mapa[padrao] = str(original)
                usadas.add(str(original))
                break
    ausentes = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in mapa]
    nao_reconhecidas = [str(coluna) for coluna in dados.columns if str(coluna) not in usadas]
    return mapa, ausentes, nao_reconhecidas


def _codigo_inicial(valor: object) -> int | None:
    texto = str(valor).strip()
    correspondencia = re.match(r"^([1-9]\d*)\s*(?:[-—–.)]|$)", texto)
    return int(correspondencia.group(1)) if correspondencia else None


def _converter_escala(valor: object, coluna: str) -> int | pd._libs.missing.NAType:
    if pd.isna(valor) or not str(valor).strip():
        return pd.NA
    codigo = _codigo_inicial(valor)
    if codigo in range(1, 6):
        return codigo
    texto = normalizar_texto(valor)
    mapas_comuns = {
        1: ["nunca", "nenhuma vez", "nao confio", "muito baixo", "nada preocupado"],
        2: ["raramente", "poucas vezes", "pouco ganho", "baixo", "confio pouco", "pouco preocupado"],
        3: ["as vezes", "mais ou menos", "ganho razoavel", "moderado", "moderadamente"],
        4: ["frequentemente", "ganho bom", "alto", "confio muito", "muito preocupado"],
        5: ["grande frequencia", "muito frequentemente", "sempre", "muito ganho", "muito alto",
            "confio totalmente", "extremamente preocupado", "mais de 10 vezes"],
    }
    for numero, expressoes in mapas_comuns.items():
        if any(expressao in texto for expressao in expressoes):
            return numero
    return pd.NA


def _converter_perfil(valor: object) -> str | pd._libs.missing.NAType:
    if pd.isna(valor) or not str(valor).strip():
        return pd.NA
    codigo = _codigo_inicial(valor)
    texto = normalizar_texto(valor)
    if codigo == 1 or "aluno" in texto:
        return "Aluno"
    if codigo == 2 or "professor" in texto:
        return "Professor"
    return pd.NA


def _converter_ferramenta(valor: object, formulario_antigo: bool = False) -> object:
    if pd.isna(valor) or not str(valor).strip():
        return pd.NA
    texto = normalizar_texto(valor)
    codigo = _codigo_inicial(valor)
    mapa_codigo_novo = {1: "ChatGPT", 2: "Claude", 3: "DeepSeek", 4: "Perplexity", 5: "Gemini", 6: "Nenhuma dessas opções"}
    mapa_codigo_antigo = {1: "ChatGPT", 2: "Gemini", 5: "Claude", 6: "DeepSeek", 7: "Perplexity"}
    for ferramenta in FERRAMENTAS[:-1]:
        if normalizar_texto(ferramenta) in texto:
            return ferramenta
    if any(termo in texto for termo in ("nenhuma", "nao utiliz", "outra ferramenta", "copilot", "meta ai", "grok", "canva")):
        return "Nenhuma dessas opções"
    if formulario_antigo and codigo in mapa_codigo_antigo:
        return mapa_codigo_antigo[codigo]
    if codigo in mapa_codigo_novo:
        return mapa_codigo_novo[codigo]
    return pd.NA


def limpar_dados(dados: pd.DataFrame, avisos_iniciais: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    """Padroniza valores e produz um relatório detalhado de qualidade."""
    avisos = list(avisos_iniciais or [])
    dados = dados.copy()
    dados.columns = [re.sub(r"\s+", " ", str(coluna)).strip() for coluna in dados.columns]
    mapa, ausentes, nao_reconhecidas = reconhecer_colunas(dados)
    if ausentes:
        nomes = ", ".join(ausentes)
        raise ValueError(f"Colunas obrigatórias não encontradas: {nomes}.")
    tratados = pd.DataFrame(index=dados.index)
    invalidos: dict[str, int] = {}
    for coluna in COLUNAS_PADRAO:
        if coluna not in mapa:
            tratados[coluna] = pd.NaT if coluna == "data_resposta" else pd.NA
            continue
        serie_original = dados[mapa[coluna]]
        ausente_original = serie_original.isna() | serie_original.astype(str).str.strip().eq("")
        if coluna == "data_resposta":
            convertida = pd.to_datetime(serie_original, errors="coerce", utc=True)
        elif coluna == "perfil":
            convertida = serie_original.map(_converter_perfil)
        elif coluna == "ia_mais_utilizada":
            cabecalho = normalizar_texto(mapa[coluna])
            formulario_antigo = "copilot" in cabecalho or "11" in cabecalho
            convertida = serie_original.map(
                lambda valor: _converter_ferramenta(valor, formulario_antigo)
            )
        else:
            convertida = serie_original.map(lambda valor: _converter_escala(valor, coluna)).astype("Int64")
        tratados[coluna] = convertida
        invalidos[coluna] = int((~ausente_original & convertida.isna()).sum())
        if invalidos[coluna]:
            avisos.append(f"{TITULOS[coluna]}: {invalidos[coluna]} valor(es) inválido(s).")
    for coluna in COLUNAS_ESCALA:
        tratados[f"{coluna}_rotulo"] = tratados[coluna].map(ROTULOS_ESCALA[coluna])
    duplicadas = dados.duplicated(keep="first")
    tratados["_duplicada"] = duplicadas
    relatorio = {
        "linhas_originais": len(dados),
        "colunas_reconhecidas": {padrao: original for padrao, original in mapa.items()},
        "colunas_nao_reconhecidas": nao_reconhecidas,
        "valores_invalidos": invalidos,
        "ausentes": {coluna: int(tratados[coluna].isna().sum()) for coluna in COLUNAS_PADRAO},
        "duplicadas": int(duplicadas.sum()),
        "avisos": avisos,
    }
    return tratados, relatorio


def carregar_e_limpar(origem: str | Path | bytes, nome: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Executa leitura e limpeza em uma única chamada."""
    dados, avisos = ler_arquivo(origem, nome)
    return limpar_dados(dados, avisos)


def aplicar_filtros(
    dados: pd.DataFrame,
    perfil: str = "Todos",
    ferramenta: str = "Todas",
    data_inicial: str | None = None,
    data_final: str | None = None,
    incluir_duplicadas: bool = True,
) -> pd.DataFrame:
    """Aplica os filtros globais sem modificar a base tratada."""
    filtrados = dados.copy()
    if perfil != "Todos":
        filtrados = filtrados[filtrados["perfil"] == perfil]
    if ferramenta != "Todas":
        filtrados = filtrados[filtrados["ia_mais_utilizada"] == ferramenta]
    if not incluir_duplicadas:
        filtrados = filtrados[~filtrados["_duplicada"]]
    if data_inicial:
        inicio = pd.to_datetime(data_inicial, errors="coerce", utc=True)
        if not pd.isna(inicio):
            filtrados = filtrados[filtrados["data_resposta"] >= inicio]
    if data_final:
        fim = pd.to_datetime(data_final, errors="coerce", utc=True)
        if not pd.isna(fim):
            filtrados = filtrados[filtrados["data_resposta"] < fim + pd.Timedelta(days=1)]
    return filtrados
