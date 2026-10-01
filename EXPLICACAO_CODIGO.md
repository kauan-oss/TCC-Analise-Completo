# Explicação completa do código

Este guia acompanha a implementação em ordem. As linhas em branco apenas
separam blocos; linhas de comentário começam com `#` e explicam a decisão logo
ao lado do código. Docstrings entre aspas triplas explicam cada módulo e função.

## Como ler cada linha Python

- `import ...` disponibiliza um módulo; `from ... import ...` traz nomes
  específicos.
- Uma atribuição com `=` guarda o valor da direita no nome da esquerda.
- `def nome(...):` inicia uma função; as linhas indentadas pertencem a ela.
- `return` devolve o resultado da função.
- `if`, `elif` e `else` escolhem um caminho.
- `for` repete o bloco para cada item.
- `with` abre um contexto que é encerrado automaticamente.
- Colchetes criam listas ou selecionam colunas; chaves criam dicionários.
- Chamadas terminadas em `.classes(...)` ou `.props(...)` configuram a
  aparência/comportamento do componente NiceGUI criado na mesma linha.

## `processamento.py`, linha por linha e por bloco

1. A docstring inicial define a responsabilidade do módulo.
2. `from __future__ import annotations` permite referências de tipos modernas.
3. `csv`, `io`, `re`, `unicodedata` e `Path` tratam arquivo, memória, padrões,
   acentos e caminhos; `pandas as pd` manipula as tabelas.
4. `COLUNAS_PADRAO` lista, na ordem, todos os nomes internos exigidos.
5. `COLUNAS_OBRIGATORIAS = COLUNAS_PADRAO[1:]` considera a data opcional.
6. `COLUNAS_ESCALA` lista somente variáveis ordinais, impedindo média de perfil
   ou ferramenta.
7. `TITULOS` liga cada nome interno ao texto curto mostrado na tela.
8. `ROTULOS_ESCALA` liga cada código de 1 a 5 ao rótulo correto de cada questão.
9. `FERRAMENTAS` define as seis categorias nominais aceitas.
10. `PALAVRAS_COLUNAS` define alternativas de palavras-chave. Cada lista interna
    precisa estar integralmente presente no cabeçalho.
11. `normalizar_texto` transforma ausência em vazio, decompõe acentos, remove
    marcas de acento, usa minúsculas comparáveis e reduz espaços. O valor
    original não é sobrescrito.
12. `ler_csv` tenta três codificações. `Sniffer` procura o separador; a contagem
    de vírgulas e ponto e vírgula é o plano alternativo. `pd.read_csv` cria o
    DataFrame e o último erro é incluído na mensagem se todas as tentativas
    falharem.
13. `ler_arquivo` distingue bytes de caminho, rejeita vazio, encaminha CSV para
    `ler_csv` e XLSX para `pd.ExcelFile`. A primeira planilha é lida e as demais
    geram aviso.
14. `reconhecer_colunas` percorre cada cabeçalho e cada padrão. `nome_exato`
    cobre o modelo padronizado; `palavras_encontradas` cobre perguntas longas.
    O retorno contém mapa, obrigatórias ausentes e não reconhecidas.
15. `_codigo_inicial` usa expressão regular para ler códigos como `1`,
    `1 - Aluno` e `1 — Aluno`.
16. `_converter_escala` mantém 1 a 5, reconhece rótulos novos e antigos e
    devolve `pd.NA` para qualquer valor inválido.
17. `_converter_perfil` reconhece código ou palavra `aluno`/`professor`.
18. `_converter_ferramenta` reconhece o nome antes do número. Isso evita
    ambiguidades. Também mantém compatibilidade com a versão antiga do
    questionário detectada no próprio cabeçalho.
19. `limpar_dados` copia a entrada, limpa espaços dos cabeçalhos, exige as
    colunas obrigatórias e cria uma tabela tratada.
20. Dentro do `for`, cada coluna usa o conversor adequado. A expressão
    `~ausente_original & convertida.isna()` conta valor preenchido que se tornou
    ausente, portanto inválido.
21. As colunas `_rotulo` preservam textos próprios para apresentação.
22. `duplicated(keep="first")` marca somente repetições posteriores, sem excluir
    nada automaticamente.
23. `relatorio` reúne linhas, reconhecimento, inválidos, ausentes, duplicadas e
    avisos.
24. `carregar_e_limpar` encadeia leitura e limpeza.
25. `aplicar_filtros` começa com cópia, restringe perfil, ferramenta, duplicatas
    e datas apenas quando cada controle foi preenchido, e devolve o recorte.

## `analise.py`, linha por linha e por bloco

1. Os imports trazem pandas e as definições compartilhadas do processamento.
2. `formatar` detecta ausência e usa vírgula decimal.
3. `modas` remove ausentes e devolve todas as categorias empatadas.
4. `frequencias` escolhe categorias 1 a 5 para escalas e categorias observadas
   para nominais. Para cada categoria calcula quantidade, proporção e
   percentual, depois cria um DataFrame.
5. `estatisticas_escala` remove ausentes e calcula quantidade válida, ausente,
   média, mediana, moda, extremos, amplitude, variância e desvio amostrais,
   quartis e percentual 4–5. As condições `if validas` e `if validas > 1`
   impedem cálculos inválidos.
6. O intervalo interquartil é `q3 - q1`; o denominador de 4–5 é guardado
   explicitamente.
7. `resumo_categorica` calcula apenas total, ausentes, moda e frequências.
8. `tabela_estatisticas` chama a função de escala para todas as questões
   escolhidas.
9. `comparacao_perfis` filtra cada perfil, calcula os mesmos resumos e só calcula
   diferença absoluta quando ambas as médias existem.
10. `indicadores` escolhe os nove números/textos usados nos cartões.
11. `texto_resultado` gera frase neutra, mostra respostas válidas e percentual e
    não atribui causa.

## `componentes.py`, linha por linha e por bloco

1. Os imports trazem pandas, NiceGUI e as funções de análise.
2. `cartao` abre `ui.card`; as três `ui.label` exibem título, valor e observação.
3. `alerta` cria uma caixa com classes de cor passadas no argumento.
4. `tabela_dataframe` copia os dados, converte ausências para vazio, formata
   números, cria a descrição de cada coluna e envia os registros à `ui.table`.
5. `grafico_barras` calcula frequências, escolhe quantidade ou percentual e
   monta o dicionário ECharts. `xAxis` recebe rótulos, `yAxis` recebe a medida e
   `series` recebe os valores.
6. `grafico_empilhado` repete códigos 1 a 5; em cada questão calcula a parcela
   do código e cria séries com `stack="total"`, formando 100%.
7. `secao_escalas` combina gráfico empilhado, tabela descritiva e expansões com
   gráficos individuais.

## `app.py`, linha por linha e por bloco

1. Os imports trazem memória, variáveis de ambiente, caminhos, pandas,
   eventos/UI e funções dos três módulos locais.
2. `PASTA_PROJETO`, `PASTA_DADOS` e `ARQUIVO_PADRAO` montam caminhos portáveis.
3. `ESTADO` guarda base, relatório, arquivo, erro e valores dos controles.
4. `carregar_base_padrao` tenta carregar `dados/respostas.csv`; erros esperados
   são guardados para aparecer na interface.
5. `receber_upload` precisa de `async` porque a API do NiceGUI lê o arquivo sem
   bloquear o servidor. `await evento.file.read()` obtém os bytes; depois a
   mesma limpeza da base padrão é usada e `refresh()` redesenha tudo.
6. `dados_filtrados` centraliza a aplicação dos cinco filtros.
7. `alterar_filtro` muda uma chave e atualiza o conteúdo.
8. `limpar_filtros` restaura os padrões e atualiza controles e páginas.
9. `baixar_csv` remove a coluna técnica e entrega bytes UTF-8 com BOM.
10. `baixar_estatisticas` abre um Excel em memória; cada `to_excel` cria uma
    planilha e `ui.download` entrega o resultado.
11. `@ui.refreshable` faz a função poder ser reconstruída. Em
    `controles_filtros`, cada `ui.select`, `ui.input` e `ui.switch` chama
    `alterar_filtro` com seu novo valor.
12. Cada função `pagina_...` representa uma das nove áreas. Ela recebe sempre o
    mesmo recorte filtrado e combina cartões, gráficos, tabelas e textos.
13. Na visão geral, divisões percentuais só ocorrem quando `total` é diferente
    de zero.
14. Em comparação, `value_counts` conta grupos e o aviso aparece se algum tiver
    menos de cinco casos.
15. Em qualidade, o `for` cria uma linha por variável e o preenchimento é
    `1 - ausentes/total`.
16. Em dados, os três botões capturam a base tratada, filtrada ou estatísticas.
    A pesquisa converte as células para texto e combina com `.any(axis=1)`.
17. `conteudo_dashboard` interrompe com mensagem se há erro ou recorte vazio.
    Caso contrário cria nove `ui.tab` e liga, na mesma ordem, cada aba à função.
18. `criar_interface` define título/cores, cabeçalho, upload, filtros, conteúdo
    e rodapé metodológico.
19. As duas chamadas finais carregam a base e constroem os componentes.
20. O teste de `__name__` inicia o servidor somente quando o arquivo é executado
    diretamente. `PORTA_APP` permite trocar a porta sem editar o código;
    `reload=False` evita processo duplicado e `show=False` não força a abertura
    do navegador.

## `tests/test_processamento_analise.py`

1. Os imports trazem memória, pandas, pytest e funções testadas.
2. `base` cria dados fixos; não usa números aleatórios.
3. `como_csv` converte a tabela em bytes, simulando upload.
4. Cada função iniciada por `test_` é descoberta pelo pytest.
5. Os `assert` comprovam resultado esperado para CSV, XLSX, planilhas múltiplas,
   somente alunos, somente professores, ausentes, inválidos, duplicatas,
   filtros, coluna ausente, arquivo vazio e ordem 1–5.
6. `@pytest.mark.parametrize` executa o mesmo teste uma vez para cada perfil.

Essa leitura cobre todas as instruções executáveis. Constantes extensas foram
explicadas como mapas: cada linha interna apenas associa a chave da esquerda ao
texto ou conjunto de palavras da direita.
