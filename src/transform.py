import glob
import json
import logging
import pandas as pd

COLUNAS_MANTIDAS = {
    "name": "cidade",
    "sys.country": "pais",
    "main.temp": "temperatura",
    "main.feels_like": "sensacao_termica",
    "main.temp_min": "temp_min",
    "main.temp_max": "temp_max",
    "main.humidity": "umidade",
    "main.pressure": "pressao",
    "weather.description": "descricao_clima",
    "weather.main": "clima_categoria",
    "wind.speed": "vel_vento",
    "visibility": "visibilidade",
    "rain.1h": "chuva_1h",
    "clouds.all": "nebulosidade",
    "dt": "data_coleta",
    "sys.sunrise": "nascer_sol",
    "sys.sunset": "por_sol",
}

def transform():
    caminhos = glob.glob("raw/*.json")
    
    registros = []
    for caminho in caminhos:
        with open(caminho, "r", encoding="utf-8") as f:
            dados_arquivo = json.load(f)
            registros.extend(dados_arquivo)

    # Resolve o campo "weather": troca a lista por só o primeiro item dela
    for registro in registros:
        registro["weather"] = registro["weather"][0]
        
    logging.info(f"Total de registros lidos de {len(caminhos)} arquivo(s): {len(registros)}")
    
    df = pd.json_normalize(registros)
    df = df[list(COLUNAS_MANTIDAS.keys())]
    df = df.rename(columns=COLUNAS_MANTIDAS)
    logging.info(f"Colunas geradas após normalização: {list(df.columns)}")

    # Trata nulos: cidades sem chuva registrada viram 0, não NULL
    df["chuva_1h"] = df["chuva_1h"].fillna(0)
    
    # Converte timestamps Unix (segundos) para datas legíveis
    df["data_coleta"] = pd.to_datetime(df["data_coleta"], unit="s")
    df["nascer_sol"] = pd.to_datetime(df["nascer_sol"], unit="s")
    df["por_sol"] = pd.to_datetime(df["por_sol"], unit="s")
    
    # Validação: garante que não sobrou nenhum nulo inesperado
    if df.isnull().any().any():
        logging.warning(f"Ainda existem valores nulos após o tratamento:\n{df.isnull().sum()}")
    else:
        logging.info("Nenhum valor nulo inesperado encontrado.")
    
    logging.info(f"Transformação concluída: {df.shape[0]} linhas, {df.shape[1]} colunas")
    
    return df

if __name__ == "__main__":
    df = transform()
    print(df.head())
    print(df.dtypes)