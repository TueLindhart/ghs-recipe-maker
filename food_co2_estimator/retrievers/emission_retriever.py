from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from food_co2_estimator.data.vector_store import get_vector_store


def get_emission_retriever(k: int = 5, **kwargs) -> VectorStoreRetriever:
    vector_store = get_vector_store()
    return vector_store.as_retriever(k=k, **kwargs)


def parse_retriever_output(documents: List[Document]):
    results = {}
    for document in documents:
        if "Total kg CO2e/kg" in document.metadata.keys():
            emission = document.metadata["Total kg CO2e/kg"]
            emission_rounded = round(float(emission), 1)
            results[document.page_content] = f"{emission_rounded} kg CO2e / kg"
    return results


def get_emission_retriever_chain(k: int = 10, **kwargs):
    retriever = get_emission_retriever(k=k, **kwargs)
    return retriever | parse_retriever_output


def batch_emission_retriever(inputs: List[str]):
    retriever_chain = get_emission_retriever_chain()
    return dict(zip(inputs, retriever_chain.batch(inputs)))
