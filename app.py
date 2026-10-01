"""Dashboard interativa do TCC sobre uso de Inteligência Artificial."""

from __future__ import annotations

import io
import os
from pathlib import Path

import pandas as pd
from nicegui import events, ui

from analise import (
    comparacao_perfis,
    formatar,
    frequencias,
    indicadores,
    resumo_categorica,
    tabela_estatisticas,
    texto_resultado,
)
from componentes import (
    alerta,
    cartao,
    grafico_barras,
    grafico_empilhado,
    secao_escalas,
    tabela_dataframe,
)
from processamento import (
    COLUNAS_ESCALA,
    COLUNAS_PADRAO,
    FERRAMENTAS,
    TITULOS,
    aplicar_filtros,
    carregar_e_limpar,
)


PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_DADOS = PASTA_PROJETO / "dados"
ARQUIVO_PADRAO = PASTA_DADOS / "respostas.csv"

ESTADO = {
    "dados": pd.DataFrame(),
    "relatorio": {},
    "nome_arquivo": "",
    "erro": "",
    "perfil": "Todos",
    "ferramenta": "Todas",
    "data_inicial": None,
    "data_final": None,
    "incluir_duplicadas": True,
    "mostrar_dados": True,
    "pesquisa": "",
}


def carregar_base_padrao() -> None:
    """Carrega respostas.csv ao iniciar e registra erros sem derrubar o servidor."""
    try:
        dados, relatorio = carregar_e_limpar(ARQUIVO_PADRAO)
        ESTADO.update({
            "dados": dados,
            "relatorio": relatorio,
            "nome_arquivo": ARQUIVO_PADRAO.name,
            "erro": "",
        })
    except (FileNotFoundError, ValueError, OSError) as erro:
        ESTADO["erro"] = str(erro)


async def receber_upload(evento: events.UploadEventArguments) -> None:
    """Lê o upload em memória e atualiza toda a dashboard."""
    try:
        conteudo = await evento.file.read()
        dados, relatorio = carregar_e_limpar(conteudo, evento.file.name)
        ESTADO.update({
            "dados": dados,
            "relatorio": relatorio,
            "nome_arquivo": evento.file.name,
            "erro": "",
        })
        ui.notify("Arquivo carregado e analisado.", type="positive")
    except (ValueError, OSError) as erro:
        ESTADO["erro"] = str(erro)
        ui.notify(str(erro), type="negative", multi_line=True)
    conteudo_dashboard.refresh()


def dados_filtrados() -> pd.DataFrame:
    """Obtém o recorte correspondente aos controles globais."""
    if ESTADO["dados"].empty:
        return ESTADO["dados"].copy()
    return aplicar_filtros(
        ESTADO["dados"],
        ESTADO["perfil"],
        ESTADO["ferramenta"],
        ESTADO["data_inicial"],
        ESTADO["data_final"],
        ESTADO["incluir_duplicadas"],
    )


def alterar_filtro(chave: str, valor: object) -> None:
    """Grava uma opção de filtro e redesenha o conteúdo."""
    ESTADO[chave] = valor
    conteudo_dashboard.refresh()


def limpar_filtros() -> None:
    """Restaura todos os filtros ao estado inicial."""
    ESTADO.update({
        "perfil": "Todos",
        "ferramenta": "Todas",
        "data_inicial": None,
        "data_final": None,
        "incluir_duplicadas": True,
    })
    controles_filtros.refresh()
    conteudo_dashboard.refresh()


def baixar_csv(dados: pd.DataFrame, nome: str) -> None:
    """Entrega uma cópia CSV da tabela escolhida."""
    exportacao = dados.drop(columns=["_duplicada"], errors="ignore").to_csv(
        index=False, encoding="utf-8-sig"
    )
    ui.download(exportacao.encode("utf-8-sig"), nome)


def baixar_estatisticas(dados: pd.DataFrame) -> None:
    """Gera uma pasta de trabalho XLSX com tabelas estatísticas."""
    try:
        memoria = io.BytesIO()
        with pd.ExcelWriter(memoria, engine="openpyxl") as escritor:
            tabela_estatisticas(dados).to_excel(escritor, sheet_name="Escalas", index=False)
            comparacao_perfis(dados).to_excel(escritor, sheet_name="Comparacao", index=False)
            frequencias(dados, "perfil").to_excel(escritor, sheet_name="Perfil", index=False)
            frequencias(dados, "ia_mais_utilizada").to_excel(
                escritor, sheet_name="Ferramentas", index=False
            )
        ui.download(memoria.getvalue(), "tabelas_estatisticas.xlsx")
    except ImportError:
        ui.notify("Instale openpyxl para exportar XLSX.", type="negative")


@ui.refreshable
def controles_filtros() -> None:
    """Cria os filtros globais da aplicação."""
    with ui.card().classes("w-full p-4 bg-slate-50"):
        ui.label("Filtros globais").classes("text-lg font-semibold")
        with ui.row().classes("w-full gap-3 items-end"):
            ui.select(
                ["Todos", "Aluno", "Professor"],
                value=ESTADO["perfil"],
                label="Perfil",
                on_change=lambda evento: alterar_filtro("perfil", evento.value),
            ).classes("w-44")
            ui.select(
                ["Todas"] + FERRAMENTAS,
                value=ESTADO["ferramenta"],
                label="Ferramenta",
                on_change=lambda evento: alterar_filtro("ferramenta", evento.value),
            ).classes("w-64")
            ui.input(
                "Data inicial",
                value=ESTADO["data_inicial"],
                on_change=lambda evento: alterar_filtro("data_inicial", evento.value),
            ).props("type=date").classes("w-44")
            ui.input(
                "Data final",
                value=ESTADO["data_final"],
                on_change=lambda evento: alterar_filtro("data_final", evento.value),
            ).props("type=date").classes("w-44")
            ui.switch(
                "Incluir duplicadas",
                value=ESTADO["incluir_duplicadas"],
                on_change=lambda evento: alterar_filtro("incluir_duplicadas", evento.value),
            )
            ui.button("Limpar filtros", on_click=limpar_filtros, icon="filter_alt_off").props("outline")


def pagina_visao_geral(dados: pd.DataFrame) -> None:
    """Monta cartões e resumo automático da amostra."""
    valores = indicadores(dados)
    with ui.grid().classes("w-full grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"):
        cartao("Total de participantes", valores["total"])
        cartao("Alunos", valores["alunos"])
        cartao("Professores", valores["professores"])
        cartao("Ferramenta mais utilizada", valores["ferramenta"])
        cartao("Mediana da frequência", formatar(valores["mediana_frequencia"]))
        cartao("Média complementar", formatar(valores["media_frequencia"]))
        cartao("Uso frequente (4 ou 5)", f"{formatar(valores['uso_frequente'])}%")
        cartao("Produtividade percebida alta", f"{formatar(valores['produtividade_alta'])}%")
        cartao("Verificação frequente", f"{formatar(valores['verificacao_frequente'])}%")
    total = valores["total"]
    percentual_alunos = valores["alunos"] / total * 100 if total else 0
    percentual_professores = valores["professores"] / total * 100 if total else 0
    alerta(
        f"A amostra filtrada contém {total} participante(s): "
        f"{percentual_alunos:.1f}% aluno(s) e {percentual_professores:.1f}% professor(es). "
        f"A ferramenta modal foi {valores['ferramenta']}. "
        f"A mediana da frequência geral foi {formatar(valores['mediana_frequencia'])}.",
        "blue",
    )


def pagina_perfil(dados: pd.DataFrame) -> None:
    """Mostra composição da amostra."""
    resumo = resumo_categorica(dados, "perfil")
    ui.label(
        f"Respostas válidas: {resumo['total_valido']} | Ausentes: {resumo['total_ausente']} | "
        f"Moda: {resumo['moda']}"
    )
    grafico_barras(dados, "perfil", percentual=True)
    tabela_dataframe(resumo["frequencias"], "Frequências do perfil")


def pagina_frequencia(dados: pd.DataFrame) -> None:
    """Mostra frequência e finalidades de uso."""
    colunas = ["frequencia_uso", "uso_pessoal", "uso_profissional", "uso_academico"]
    secao_escalas(dados, colunas)
    tabela_dataframe(comparacao_perfis(dados).iloc[:4], "Comparação por perfil")


def pagina_ferramentas(dados: pd.DataFrame) -> None:
    """Mostra as ferramentas utilizadas no total e por perfil."""
    resumo = resumo_categorica(dados, "ia_mais_utilizada")
    aluno = resumo_categorica(dados[dados["perfil"] == "Aluno"], "ia_mais_utilizada")
    professor = resumo_categorica(dados[dados["perfil"] == "Professor"], "ia_mais_utilizada")
    with ui.grid().classes("w-full grid-cols-1 md:grid-cols-3 gap-4"):
        cartao("Mais utilizada no total", resumo["moda"])
        cartao("Mais utilizada por alunos", aluno["moda"])
        cartao("Mais utilizada por professores", professor["moda"])
    grafico_barras(dados, "ia_mais_utilizada", percentual=True)
    tabela = resumo["frequencias"].sort_values("frequencia", ascending=False)
    tabela_dataframe(tabela, "Detalhamento das ferramentas")


def pagina_produtividade(dados: pd.DataFrame) -> None:
    """Mostra produtividade percebida e confiança."""
    secao_escalas(dados, ["ganho_produtividade", "confianca_respostas"])
    alerta(texto_resultado(dados, "ganho_produtividade", "ganho de produtividade percebido"), "blue")
    alerta(texto_resultado(dados, "confianca_respostas", "confiança nas respostas"), "blue")


def pagina_uso_responsavel(dados: pd.DataFrame) -> None:
    """Mostra comportamentos declarados relacionados ao uso responsável."""
    colunas = ["verifica_fontes", "preocupacao_plagio", "preocupacao_raciocinio_critico"]
    secao_escalas(dados, colunas)
    for coluna in colunas:
        alerta(texto_resultado(dados, coluna, TITULOS[coluna].lower()), "blue")


def pagina_comparacao(dados: pd.DataFrame) -> None:
    """Mostra a comparação descritiva consolidada."""
    alerta(
        "A comparação é descritiva e não demonstra diferença na população nem relação causal.",
        "amber",
    )
    contagens = dados["perfil"].value_counts()
    if any(contagens.get(perfil, 0) < 5 for perfil in ("Aluno", "Professor")):
        alerta("Um dos grupos possui menos de cinco respostas; interprete as diferenças com cautela.")
    tabela = comparacao_perfis(dados)
    tabela_dataframe(tabela, "Tabela consolidada")
    ui.echart({
        "title": {"text": "Médias complementares por perfil", "left": "center", "top": 8},
        "tooltip": {
            "trigger": "axis",
            ":valueFormatter": "valor => Number(valor).toFixed(2).replace('.', ',')",
        },
        "legend": {"top": 60},
        "grid": {"left": 250, "right": 30, "top": 110, "bottom": 170},
        "xAxis": {
            "type": "value", "min": 1, "max": 5, "name": "Média",
            "axisLabel": {":formatter": "valor => Number(valor).toLocaleString('pt-BR', {maximumFractionDigits: 2})"},
        },
        "yAxis": {
            "type": "category", "data": tabela["questao"].tolist(),
            "axisLabel": {"rotate": 20, "margin": 36, "align": "right", "verticalAlign": "bottom", "interval": 0},
        },
        "series": [
            {"name": "Alunos", "type": "bar", "data": tabela["media_alunos"].fillna(0).round(2).tolist()},
            {"name": "Professores", "type": "bar", "data": tabela["media_professores"].fillna(0).round(2).tolist()},
        ],
    }).classes("w-full h-[46rem]")


def pagina_qualidade(dados: pd.DataFrame) -> None:
    """Apresenta o relatório de limpeza e completude."""
    relatorio = ESTADO["relatorio"]
    linhas = []
    base = ESTADO["dados"]
    for coluna in COLUNAS_PADRAO:
        ausentes = relatorio.get("ausentes", {}).get(coluna, 0)
        preenchimento = (1 - ausentes / len(base)) * 100 if len(base) else 0
        linhas.append({
            "coluna": coluna,
            "ausentes": ausentes,
            "invalidos": relatorio.get("valores_invalidos", {}).get(coluna, 0),
            "preenchimento_percentual": preenchimento,
        })
    with ui.grid().classes("w-full grid-cols-1 md:grid-cols-3 gap-4"):
        cartao("Registros antes dos filtros", relatorio.get("linhas_originais", 0))
        cartao("Registros após os filtros", len(dados))
        cartao("Linhas duplicadas", relatorio.get("duplicadas", 0))
    tabela_dataframe(pd.DataFrame(linhas), "Completude por variável")
    ui.label("Colunas reconhecidas").classes("text-xl font-semibold mt-4")
    for padrao, original in relatorio.get("colunas_reconhecidas", {}).items():
        ui.label(f"{padrao} ← {original}").classes("text-sm")
    nao_reconhecidas = relatorio.get("colunas_nao_reconhecidas", [])
    alerta("Colunas não reconhecidas: " + (", ".join(nao_reconhecidas) or "nenhuma"), "slate")
    for aviso in relatorio.get("avisos", []):
        alerta(aviso)


def pagina_dados(dados: pd.DataFrame) -> None:
    """Oferece pesquisa, visualização e exportações."""
    with ui.row().classes("items-center"):
        ui.input(
            "Pesquisar nos dados",
            value=ESTADO["pesquisa"],
            on_change=lambda evento: alterar_filtro("pesquisa", evento.value),
        ).props("clearable").classes("w-72")
        ui.switch(
            "Mostrar dados",
            value=ESTADO["mostrar_dados"],
            on_change=lambda evento: alterar_filtro("mostrar_dados", evento.value),
        )
        ui.button("CSV tratado", on_click=lambda: baixar_csv(ESTADO["dados"], "dados_tratados.csv"))
        ui.button("CSV filtrado", on_click=lambda: baixar_csv(dados, "dados_filtrados.csv"))
        ui.button("Estatísticas XLSX", on_click=lambda: baixar_estatisticas(dados))
    exibicao = dados.copy()
    pesquisa = normalizar_pesquisa(ESTADO["pesquisa"])
    if pesquisa:
        mascara = exibicao.astype(str).apply(
            lambda coluna: coluna.str.casefold().str.contains(pesquisa, regex=False)
        ).any(axis=1)
        exibicao = exibicao[mascara]
    if ESTADO["mostrar_dados"]:
        tabela_dataframe(exibicao.drop(columns=["_duplicada"], errors="ignore"), paginacao=15)
    else:
        alerta("A tabela de dados brutos está oculta.", "slate")


def normalizar_pesquisa(valor: object) -> str:
    """Prepara a pesquisa textual sem modificar os dados."""
    return str(valor or "").strip().casefold()


@ui.refreshable
def conteudo_dashboard() -> None:
    """Redesenha todas as páginas depois de upload ou filtro."""
    if ESTADO["erro"]:
        alerta(ESTADO["erro"], "red")
        return
    dados = dados_filtrados()
    ui.label(
        f"Arquivo: {ESTADO['nome_arquivo']} | Registros no recorte: {len(dados)}"
    ).classes("text-sm text-slate-600")
    if dados.empty:
        alerta("Nenhum registro corresponde aos filtros atuais.", "amber")
        return
    with ui.tabs().classes("w-full text-blue-900") as abas:
        nomes = [
            "Visão geral", "Perfil", "Frequência e finalidade", "Ferramentas",
            "Produtividade e confiança", "Uso responsável", "Comparação",
            "Qualidade dos dados", "Dados e exportação",
        ]
        componentes_abas = [ui.tab(nome) for nome in nomes]
    with ui.tab_panels(abas, value=componentes_abas[0]).classes("w-full bg-transparent"):
        funcoes = [
            pagina_visao_geral, pagina_perfil, pagina_frequencia, pagina_ferramentas,
            pagina_produtividade, pagina_uso_responsavel, pagina_comparacao,
            pagina_qualidade, pagina_dados,
        ]
        for aba, funcao in zip(componentes_abas, funcoes):
            with ui.tab_panel(aba):
                funcao(dados)


def criar_interface() -> None:
    """Constrói o cabeçalho, os controles, o conteúdo e a nota metodológica."""
    ui.page_title("Análise do Uso de Inteligência Artificial")
    ui.colors(primary="#1d4ed8", secondary="#475569", accent="#0f766e")
    with ui.header().classes("bg-slate-900 text-white p-4"):
        with ui.column().classes("gap-0"):
            ui.label("Análise do Uso de Inteligência Artificial entre Alunos e Professores").classes(
                "text-xl md:text-2xl font-bold"
            )
            ui.label("Dashboard de estatística descritiva das respostas coletadas na comunidade escolar")
    with ui.column().classes("w-full max-w-[1600px] mx-auto p-4 gap-4"):
        ui.upload(
            label="Carregar CSV ou XLSX",
            auto_upload=True,
            on_upload=receber_upload,
        ).props('accept=".csv,.xlsx"').classes("w-full")
        controles_filtros()
        conteudo_dashboard()
        ui.separator()
        ui.label(
            "Nota metodológica: os resultados descrevem somente a amostra e as percepções "
            "declaradas. As escalas são ordinais; médias são complementares. Diferenças entre "
            "grupos não demonstram causalidade nem podem ser generalizadas automaticamente."
        ).classes("text-sm text-slate-600 pb-6")


carregar_base_padrao()
criar_interface()

if __name__ in {"__main__", "__mp_main__"}:
    porta = int(os.environ.get("PORTA_APP", "8080"))
    ui.run(title="Análise do Uso de IA", reload=False, show=False, port=porta)
