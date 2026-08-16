from sqlalchemy import create_engine
import os
import logging

def load_postgres(df):
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)
    
    df.to_sql("clima", engine, if_exists="replace", index=False)
    
    logging.info(f"Carga no PostgreSQL concluída: {df.shape[0]} linhas na tabela 'clima'")

from pymongo import MongoClient

def load_mongo(df):
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["weather_pipeline"]
    colecao = db["resumo_por_cidade"]
    
    resumo = df.groupby("cidade").agg(
        temperatura_media=("temperatura", "mean"),
        umidade_media=("umidade", "mean"),
        chuva_total=("chuva_1h", "sum"),
        qtd_coletas=("cidade", "count")
    ).reset_index()
    
    registros = resumo.to_dict(orient="records")
    
    colecao.delete_many({})
    colecao.insert_many(registros)
    
    logging.info(f"Carga no MongoDB concluída: {len(registros)} cidades na coleção 'resumo_por_cidade'")

if __name__ == "__main__":
    import logging
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    from transform import transform
    df = transform()
    load_postgres(df)
    load_mongo(df) 