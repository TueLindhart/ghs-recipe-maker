import os

EMBEDDING_MODEL = "text-embedding-3-large"
VECTOR_DB_COLLECTION_NAME = "vector_co2_db"
VECTOR_DB_PERSIST_DIR = f"{os.getcwd()}/food_co2_estimator/data/vector_store/store"
EXCEL_FILE_DIR = f"{os.getcwd()}/food_co2_estimator/data/vector_store/DBv2.xlsx"
