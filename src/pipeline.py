from dotenv import load_dotenv
import logging

from extract import extract, salvar_raw, CIDADES
from transform import transform
from load import load_postgres, load_mongo

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    # 1. Extração
    resultados = []
    for cidade in CIDADES:
        dado = extract(cidade)
        if dado is not None:
            resultados.append(dado)

    if resultados:
        salvar_raw(resultados, "clima")

    # 2. Transformação
    df = transform()

    # 3. Carga
    load_postgres(df)
    load_mongo(df)