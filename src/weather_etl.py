from dotenv import load_dotenv
import os
import logging
import requests
import json
from datetime import datetime, timezone

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

api_key = os.getenv("OPENWEATHER_API_KEY")      
mongo_uri = os.getenv("MONGO_URI")               
postgres_url = os.getenv("POSTGRES_URL")

CIDADES = [
    #"Recife,BR",
    #Olinda,BR",
    "Natal,BR",
    "Catolé do Rocha,BR",
    # "João Pessoa,BR",
    # "Campina Grande,BR",
    # "Rio de janeiro,BR",
    # "São Paulo,BR",
    # "Brasília,BR"
]

def extract(cidade) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": cidade, "appid": api_key,
            "units": "metric", "lang": "pt_br"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        logging.info(f"Coleta bem-sucedida para a cidade: {cidade}")
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao coletar dados para {cidade}: {e}")
        return None

def salvar_raw(dados: dict, nome: str):
    os.makedirs("raw", exist_ok=True)  
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    file_path = os.path.join("raw", f"{timestamp}_{nome}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    logging.info(f"Dado bruto salvo em: {file_path}")

if __name__ == "__main__":
    resultados = []
    for cidade in CIDADES:
        dado = extract(cidade)
        if dado is not None:
            resultados.append(dado)

    if resultados:
        salvar_raw(resultados, "clima")