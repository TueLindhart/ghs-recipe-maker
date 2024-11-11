from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from food_co2_estimator.data.vector_store.variables import (
    EMBEDDING_MODEL,
    VECTOR_DB_COLLECTION_NAME,
    VECTOR_DB_PERSIST_DIR,
)


def get_vector_store() -> Chroma:
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        collection_name=VECTOR_DB_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_PERSIST_DIR,
    )
