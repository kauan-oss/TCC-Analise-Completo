# Dicionário de dados

Valores ausentes significam que não houve resposta válida. Eles não são
substituídos por média, mediana ou moda.

| Coluna | Pergunta / significado | Tipo | Valores e conversão | Estatísticas |
|---|---|---|---|---|
| `data_resposta` | Data e hora automática do formulário | Temporal | Data válida; inválidas viram ausentes | Primeira e última data |
| `perfil` | Você é aluno ou professor? | Nominal | `Aluno`, `Professor` | Frequência, percentual, moda |
| `frequencia_uso` | Frequência geral de uso de IA | Ordinal | 1 nunca/raramente a 5 muito frequentemente | Frequências, mediana, moda e medidas complementares |
| `uso_pessoal` | Uso de IA para fins pessoais | Ordinal | 1 a 5 | Idem |
| `uso_profissional` | Uso de IA para fins profissionais | Ordinal | 1 a 5 | Idem |
| `uso_academico` | Uso de IA para fins acadêmicos | Ordinal | 1 a 5 | Idem |
| `ia_mais_utilizada` | Ferramenta usada com maior frequência | Nominal | ChatGPT, Claude, DeepSeek, Perplexity, Gemini ou Nenhuma dessas opções | Frequência, percentual, moda |
| `ganho_produtividade` | Ganho percebido de produtividade | Ordinal | 1 muito baixo a 5 muito alto | Frequências, mediana, moda e medidas complementares |
| `confianca_respostas` | Confiança nas respostas da IA | Ordinal | 1 não confio a 5 confio totalmente | Idem |
| `verifica_fontes` | Frequência de verificação das fontes | Ordinal | 1 nunca/raramente a 5 muito frequentemente | Idem |
| `preocupacao_plagio` | Preocupação com plágio | Ordinal | 1 nada a 5 extremamente preocupado | Idem |
| `preocupacao_raciocinio_critico` | Preocupação com redução do raciocínio crítico | Ordinal | 1 nada a 5 extremamente preocupado | Idem |

Para cada escala, uma coluna terminada em `_rotulo` guarda o texto apresentado
na interface. `_duplicada` é um indicador técnico: `True` marca repetições além
da primeira ocorrência de uma linha idêntica.

Rótulos antigos como `Raramente`, `Mais ou menos`, `Com grande frequência`,
`Pouco ganho`, `Ganho razoável`, `Ganho bom` e `Muito ganho` são reconhecidos e
convertidos para a escala equivalente. Um texto não reconhecido não é
reinterpretado: vira ausente e aparece no relatório de qualidade.
