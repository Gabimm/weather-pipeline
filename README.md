# Weather Pipeline

Pipeline de dados completo — coleta, transformação e carga de dados climáticos, do início ao fim, documentado como se fosse entrar em produção.

## Sobre o projeto

Este projeto coleta dados climáticos em tempo real da **API OpenWeatherMap**, para 9 cidades brasileiras espalhadas por diferentes regiões (Nordeste, Sudeste e Centro-Oeste), transforma esses dados com Pandas, e carrega o resultado em dois bancos: PostgreSQL (dados detalhados) e MongoDB Atlas (um resumo agregado por cidade).

A escolha da OpenWeatherMap se deu pela riqueza de atributos retornados por chamada (temperatura, umidade, pressão, vento, nebulosidade, chuva, horários de nascer/pôr do sol) — o suficiente para gerar transformações e agregações com significado real, em vez de um dataset raso. Coletar de várias cidades, em vez de uma só, também permitiu explorar comparações geográficas na camada agregada do MongoDB.

Esse é o desafio final do módulo 3 (Introdução à Engenharia de Dados na Prática) da formação **NExT Dados 2026.1 (CESAR School)**.

## Arquitetura

![Arquitetura do pipeline](docs/arquitetura.png)

O fluxo segue o padrão ETL: a API é consultada pela função `extract()`, que salva o retorno bruto (sem nenhuma alteração) na camada `raw/`. A função `transform()` lê todos os arquivos da `raw/`, limpa e organiza os dados com Pandas. Por fim, `load_postgres()` e `load_mongo()` carregam o resultado nos dois bancos, cada um com um propósito diferente.

## Estrutura do repositório

```
weather-pipeline/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── extract.py       # coleta defensiva da API + salva a camada raw
│   ├── transform.py     # achata, renomeia, trata nulos e converte datas
│   ├── load.py          # carga no PostgreSQL e no MongoDB Atlas
│   └── pipeline.py      # orquestra as três etapas em sequência
├── raw/                 # coletas reais em JSON, com timestamp no nome
└── docs/
    ├── arquitetura.png  # diagrama do fluxo de dados
    └── evidencias/      # prints da tabela no Postgres e da coleção no Atlas
```

## Decisões técnicas

**Por que `if_exists="replace"` no PostgreSQL?**
A cada execução, `transform()` reconstrói o dataset inteiro a partir de todos os arquivos já salvos na `raw/` — não apenas o mais recente. Como o resultado final é sempre gerado do zero a partir da mesma fonte, substituir a tabela inteira a cada carga garante que rodar o pipeline uma vez ou dez vezes produz exatamente o mesmo resultado, sem duplicar nenhuma linha. O histórico de coletas fica preservado de qualquer forma na pasta `raw/`, que nunca é apagada.

**O que a coleção derivada do MongoDB resume?**
A coleção `resumo_por_cidade` agrega os dados por cidade: temperatura média, umidade média, soma total de chuva registrada e quantidade de coletas feitas. Não é uma cópia da tabela do Postgres — é um recorte analítico, pensado para responder perguntas do tipo "qual cidade está mais quente, em média?" sem precisar processar os dados brutos de novo.

**Que validações foram feitas?**
- O campo `weather`, que a API retorna como uma lista com um único item, é achatado para um dicionário simples antes da normalização.
- A coluna de chuva (`chuva_1h`) fica nula nas cidades sem chuva registrada — esses nulos são preenchidos com `0`, já que "sem chuva" é logicamente zero, não um dado ausente.
- Colunas de timestamp Unix (`data_coleta`, `nascer_sol`, `por_sol`) são convertidas para datas legíveis.
- Campos sem valor analítico (metadados internos da API, coordenadas, IDs internos) são descartados antes da carga.
- Ao final da transformação, uma checagem confirma que não sobrou nenhum valor nulo inesperado no DataFrame, e registra um aviso no log caso sobre algum.

**Segurança de credenciais**
Nenhuma senha, chave de API ou connection string está no código. Todas ficam num arquivo `.env` local (fora do controle de versão, listado no `.gitignore`), e são carregadas em tempo de execução com `python-dotenv`.

## Como rodar do zero

### Pré-requisitos
- Python 3.12 ou 3.13
- PostgreSQL instalado localmente (ou acesso a uma instância)
- Uma conta no MongoDB Atlas com um cluster criado
- Uma chave de API gratuita da [OpenWeatherMap](https://openweathermap.org/api)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/Gabimm/weather-pipeline.git
cd weather-pipeline

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# source .venv/bin/activate        # macOS/Linux

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie o banco no PostgreSQL
# (via psql, pgAdmin ou outro client de sua preferência)
CREATE DATABASE weather_pipeline;
```

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
OPENWEATHER_API_KEY=sua_chave_aqui
MONGO_URI=mongodb+srv://usuario:senha@seu-cluster.mongodb.net/
POSTGRES_URL=postgresql+psycopg2://usuario:senha@localhost:5432/weather_pipeline
```

Por fim, execute o pipeline completo:

```bash
python src/pipeline.py
```

Isso vai: coletar o clima das 9 cidades configuradas, salvar o JSON bruto em `raw/`, transformar os dados, e carregar o resultado no PostgreSQL e no MongoDB.

## Cidades coletadas

Recife, Olinda, Natal, Catolé do Rocha, João Pessoa, Campina Grande, Rio de Janeiro, São Paulo e Brasília. A lista pode ser ajustada em `CIDADES`, no topo do arquivo `src/extract.py`.

## Dados coletados

| Campo | Descrição |
|---|---|
| `cidade` | Nome da cidade |
| `pais` | Código do país |
| `temperatura` | Temperatura atual (°C) |
| `sensacao_termica` | Sensação térmica (°C) |
| `temp_min` / `temp_max` | Temperatura mínima e máxima |
| `umidade` | Umidade relativa do ar (%) |
| `pressao` | Pressão atmosférica |
| `descricao_clima` / `clima_categoria` | Descrição textual e categoria do clima |
| `vel_vento` | Velocidade do vento |
| `visibilidade` | Visibilidade (metros) |
| `chuva_1h` | Precipitação na última hora (mm) — `0` quando não houve chuva |
| `nebulosidade` | Cobertura de nuvens (%) |
| `data_coleta` | Data e hora da coleta |
| `nascer_sol` / `por_sol` | Horário do nascer e do pôr do sol |

## Evidências

Prints da tabela `clima` no PostgreSQL e da coleção `resumo_por_cidade` no MongoDB Atlas estão em [`docs/evidencias/`](docs/evidencias/).

## Tecnologias

- **Linguagem:** Python
- **Coleta:** requests
- **Transformação:** pandas
- **Persistência:** PostgreSQL (via SQLAlchemy + psycopg2), MongoDB Atlas (via pymongo)
- **Configuração:** python-dotenv
- **Modelagem do fluxo:** draw.io