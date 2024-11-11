from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
from langchain_core.documents import Document

from food_co2_estimator.data.vector_store import get_vector_store
from food_co2_estimator.data.vector_store.variables import EXCEL_FILE_DIR

df_dk = pd.read_excel(EXCEL_FILE_DIR, sheet_name="DK")
df_gb = pd.read_excel(EXCEL_FILE_DIR, sheet_name="GB")


emission_records_dk: List[Dict[Any, Any]] = df_dk.to_dict(orient="records")
emission_records_gb: List[Dict[Any, Any]] = df_gb.to_dict(orient="records")

vector_store = get_vector_store()
documents = []
uuids = []
for id, (emission_record_dk, emission_record_gb) in enumerate(
    zip(emission_records_dk, emission_records_gb), 1
):

    if "Name" in emission_record_gb:
        documents.append(
            Document(
                page_content=emission_record_gb["Name"],
                metadata=emission_record_dk,
                id=id,
            )
        )
        uuids.append(str(uuid4()))


vector_store.add_documents(documents)
