# Dashboard do TCC — Uso de Inteligência Artificial

Aplicação em Python para limpar, analisar e apresentar as respostas do
questionário sobre o uso de Inteligência Artificial por alunos e professores.
Os resultados são exclusivamente descritivos e representam somente a amostra.

## Tecnologias

- Python;
- pandas para leitura, limpeza e estatística;
- NiceGUI e ECharts para a interface;
- openpyxl para arquivos Excel.

## Estrutura

```text
TCC/
├── app.py
├── processamento.py
├── analise.py
├── componentes.py
├── requirements.txt
├── README.md
├── DICIONARIO_DADOS.md
├── EXPLICACAO_CODIGO.md
├── tests/
└── dados/
    ├── modelo_respostas.csv
    └── respostas.csv
```

`processamento.py` lê CSV/XLSX, reconhece cabeçalhos, limpa respostas e aplica
filtros. `analise.py` calcula frequências, percentuais, medidas descritivas,
indicadores e comparações. `componentes.py` concentra cartões, tabelas e
gráficos. `app.py` monta as nove áreas, recebe uploads e oferece exportações.

## Instalação e execução

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra `http://localhost:8080`. O servidor é iniciado sem abrir o navegador
automaticamente.

Se a porta 8080 estiver ocupada, defina outra antes de executar:

```powershell
$env:PORTA_APP="8081"
python app.py
```

## Como inserir as respostas reais

Há duas opções:

1. exporte o Google Forms em CSV, renomeie o arquivo para `respostas.csv`,
   coloque-o em `dados` e reinicie o programa;
2. use **Carregar CSV ou XLSX** no topo da dashboard. Todas as análises são
   atualizadas imediatamente.

No Google Forms, abra **Respostas**, vincule/abra a planilha e use
**Arquivo > Fazer download > Valores separados por vírgulas (.csv)**. Os
cabeçalhos podem ser as perguntas completas. A identificação usa nomes
padronizados e palavras-chave, não a posição das colunas.

CSV aceita UTF-8, UTF-8 com BOM e Latin-1, com vírgula ou ponto e vírgula. XLSX
usa a primeira planilha e mostra um aviso se houver outras.

## Filtros e páginas

Os filtros globais permitem selecionar perfil, ferramenta, período e inclusão
de duplicatas. **Limpar filtros** restaura a base completa. As nove áreas são:
visão geral; perfil; frequência e finalidade; ferramentas; produtividade e
confiança; uso responsável; comparação; qualidade; dados e exportação.

Na última área é possível pesquisar, ocultar a tabela, exportar a base tratada,
o recorte filtrado e as tabelas estatísticas em XLSX.

## Medidas estatísticas

Para variáveis nominais são usadas frequência, percentual e moda. Para escalas
ordinais de 1 a 5 são apresentadas frequência, percentual, mediana e moda como
medidas principais; média e desvio-padrão são complementares. Também são
calculados mínimo, máximo, amplitude, variância amostral, quartis, intervalo
interquartil e percentual de respostas 4 ou 5.

Uma única resposta não possui variância nem desvio-padrão amostral. Empates de
moda são mantidos. Valores ausentes não são preenchidos e valores inválidos
viram ausentes, mas são contabilizados separadamente.

## Limitações metodológicas

- A dashboard não realiza testes de hipótese, regressão ou inferência causal.
- A escala é ordinal; distâncias entre categorias não são necessariamente
  iguais.
- Diferenças pequenas de médias não provam diferenças importantes.
- Tamanho e seleção da amostra limitam a generalização.
- As respostas são percepções declaradas e podem sofrer efeitos de memória,
  interpretação e desejabilidade social.

## Erros comuns

- **Coluna obrigatória ausente:** confira se o cabeçalho contém a pergunta ou o
  nome padronizado descrito no dicionário.
- **CSV em uma única coluna:** exporte novamente; a aplicação detecta vírgula e
  ponto e vírgula.
- **XLSX não abre:** execute `pip install -r requirements.txt`.
- **Nenhum registro após filtros:** use **Limpar filtros**.
- **Porta em uso:** encerre a instância anterior do programa.

Para estudar a implementação, consulte `EXPLICACAO_CODIGO.md`.
