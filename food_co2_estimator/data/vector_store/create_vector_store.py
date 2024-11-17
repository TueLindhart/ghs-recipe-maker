import logging
from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
from langchain_core.documents import Document
from tqdm import tqdm  # Import tqdm for the progress bar

from food_co2_estimator.data.vector_store import get_vector_store
from food_co2_estimator.data.vector_store.variables import EXCEL_FILE_DIR
from food_co2_estimator.language.translator import MyTranslator

# Read Excel files
df_dk = pd.read_excel(EXCEL_FILE_DIR, sheet_name="DK")

# Convert DataFrame to a list of dictionaries
emission_records_dk: List[Dict[Any, Any]] = df_dk.to_dict(orient="records")

# Initialize vector store and translator
vector_store = get_vector_store()
translator = MyTranslator()

documents = []
uuids = []

# Loop over the records with a progress bar
for id, emission_record_dk in enumerate(tqdm(emission_records_dk), 1):

    dk_name: str | None = emission_record_dk.get("Navn", None)
    dk_name: str | None = emission_record_dk.get("Produkt", None)
    if dk_name is None:
        logging.warning(f"Object {emission_record_dk} is not added to DB")
        continue

    translated_name = translator.translate(dk_name)
    documents.append(
        Document(
            page_content=translated_name,
            metadata=emission_record_dk,
            id=id,
        )
    )
    uuids.append(str(uuid4()))

# Add documents to the vector store
vector_store.add_documents(documents)
