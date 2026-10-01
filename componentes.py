"""Componentes visuais reutilizáveis da dashboard NiceGUI."""

from __future__ import annotations

import pandas as pd
from nicegui import ui

from analise import formatar, frequencias, tabela_estatisticas
from processamento import ROTULOS_ESCALA, TITULOS


def cartao(titulo: str, valor: object, observacao: str = "") -> None:
    """Exibe um indicador de destaque."""
    with ui.card().classes("w-full p-4 border-t-4 border-blue-700 shadow-sm"):
        ui.label(titulo).classes("text-sm text-slate-600")
        ui.label(str(valor)).classes("text-2xl font-bold text-slate-900")
        if observacao:
            ui.label(observacao).classes("text-xs text-slate-500")


def alerta(texto: str, cor: str = "amber") -> None:
    """Exibe uma mensagem visual discreta."""
    ui.label(texto).classes(
        f"w-full p-3 rounded bg-{cor}-50 text-{cor}-900 border border-{cor}-200"
    )


def tabela_dataframe(dados: pd.DataFrame, titulo: str | None = None, paginacao: int = 10) -> None:
    """Converte um DataFrame em tabela NiceGUI."""
    if titulo:
        ui.label(titulo).classes("text-xl font-semibold mt-4")
    exibicao = dados.copy()
    for coluna in exibicao.columns:
        exibicao[coluna] = exibicao[coluna].map(
            lambda valor: formatar(valor) if isinstance(valor, float) else (
                "" if pd.isna(valor) else str(valor)
            )
        )
    colunas = [
        {"name": coluna, "label": coluna.replace("_", " ").title(), "field": coluna, "align": "left"}
        for coluna in exibicao.columns
    ]
    ui.table(columns=colunas, rows=exibicao.to_dict("records"), pagination=paginacao).classes("w-full")


def grafico_barras(dados: pd.DataFrame, coluna: str, percentual: bool = False) -> None:
    """Cria gráfico de barras com título, eixos e rótulos."""
    tabela = frequencias(dados, coluna)
    campo = "percentual" if percentual else "frequencia"
    eixo = "Percentual (%)" if percentual else "Quantidade"
    opcoes = {
        "title": {"text": f"{TITULOS[coluna]} (n={int(dados[coluna].notna().sum())})", "left": "center", "top": 8},
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 55, "right": 25, "top": 90, "bottom": 90},
        "xAxis": {"type": "category", "data": tabela["resposta"].tolist(), "axisLabel": {"rotate": 25}},
        "yAxis": {
            "type": "value", "name": eixo,
            "axisLabel": {":formatter": "valor => Number(valor).toLocaleString('pt-BR', {maximumFractionDigits: 2})"},
        },
        "series": [{
            "type": "bar",
            "name": eixo,
            "data": tabela[campo].round(2).tolist(),
            "label": {"show": True, "position": "top"},
            "itemStyle": {"color": "#1d4ed8"},
        }],
    }
    if percentual:
        opcoes["tooltip"][":valueFormatter"] = "valor => Number(valor).toFixed(2).replace('.', ',') + '%'"
        opcoes["series"][0]["label"][":formatter"] = "item => Number(item.value).toFixed(2).replace('.', ',') + '%'"
    ui.echart(opcoes).classes("w-full h-[26rem]")
    ui.label(
        f"Distribuição de {TITULOS[coluna].lower()} entre as respostas válidas."
    ).classes("text-sm text-slate-500")


def grafico_empilhado(dados: pd.DataFrame, colunas: list[str]) -> None:
    """Cria barras horizontais empilhadas em 100%."""
    series = []
    for codigo in range(1, 6):
        valores = []
        for coluna in colunas:
            validas = dados[coluna].dropna()
            valores.append(round(float(validas.eq(codigo).mean() * 100), 2) if len(validas) else 0)
        series.append({
            "name": f"{codigo} — {ROTULOS_ESCALA[colunas[0]][codigo]}",
            "type": "bar", "stack": "total", "data": valores,
            "label": {"show": True, ":formatter": "item => Number(item.value).toFixed(2).replace('.', ',') + '%'"},
        })
    ui.echart({
        "title": {"text": "Distribuição percentual das escalas", "left": "center", "top": 8},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            ":valueFormatter": "valor => Number(valor).toFixed(2).replace('.', ',') + '%'",
        },
        "legend": {"top": 60},
        "grid": {"left": 250, "right": 30, "top": 120, "bottom": 170},
        "xAxis": {
            "type": "value", "max": 100, "name": "Percentual (%)",
            "axisLabel": {":formatter": "valor => Number(valor).toLocaleString('pt-BR', {maximumFractionDigits: 2})"},
        },
        "yAxis": {
            "type": "category", "data": [TITULOS[coluna] for coluna in colunas],
            "axisLabel": {"rotate": 20, "margin": 36, "align": "right", "verticalAlign": "bottom", "interval": 0},
        },
        "series": series,
    }).classes("w-full h-[42rem]")


def secao_escalas(dados: pd.DataFrame, colunas: list[str]) -> None:
    """Apresenta gráficos e estatísticas para um grupo de escalas."""
    grafico_empilhado(dados, colunas)
    tabela_dataframe(tabela_estatisticas(dados, colunas), "Estatísticas descritivas")
    for coluna in colunas:
        with ui.expansion(TITULOS[coluna]).classes("w-full"):
            grafico_barras(dados, coluna, percentual=True)
