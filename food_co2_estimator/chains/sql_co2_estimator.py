import os
from typing import Literal

from langchain.chains.llm import LLMChain
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import ChatOpenAI

from food_co2_estimator.prompt_templates.sql_co2_estimator import (
    DK_CO2_SQL_PROMPT_TEMPLATE,
    EN_CO2_SQL_PROMPT_TEMPLATE,
)
from food_co2_estimator.utils.openai_model import get_model


def get_co2_sql_chain(language: Literal["da", "en"], verbose: bool = False):
    sql_dk_co2_db = SQLDatabase.from_uri(
        f"sqlite:///{os.getcwd()}/food_co2_estimator/data/dk_co2_emission.db",
        sample_rows_in_table_info=2,
    )
    llm_chain = LLMChain(
        llm=get_model(),
        prompt=(
            EN_CO2_SQL_PROMPT_TEMPLATE
            if language == "en"
            else DK_CO2_SQL_PROMPT_TEMPLATE
        ),
        verbose=verbose,
    )

    co2_sql_chain = SQLDatabaseChain(
        llm_chain=llm_chain,
        database=sql_dk_co2_db,
        verbose=verbose,
        top_k=200,
    )

    return co2_sql_chain
