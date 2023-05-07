from typing import Literal

from langchain.chains import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.sql_database import SQLDatabase

from prompt_templates.co2_sql_prompts import (
    DK_CO2_SQL_PROMPT_WITH_EXAMPLES,
    EN_CO2_SQL_PROMPT_WITH_EXAMPLES,
)


def get_en_co2_sql_chain(language: Literal["da", "en"], verbose: bool = False):
    sql_dk_co2_db = SQLDatabase.from_uri("sqlite:///data/dk_co2_emission.db", sample_rows_in_table_info=2)
    prompt = PromptTemplate(
        input_variables=["input", "table_info", "dialect"],
        template=EN_CO2_SQL_PROMPT_WITH_EXAMPLES if language == "en" else DK_CO2_SQL_PROMPT_WITH_EXAMPLES,
    )
    llm = ChatOpenAI(  # type: ignore
        temperature=0,
    )
    en_co2_sql_chain = SQLDatabaseChain.from_llm(
        llm=llm,
        db=sql_dk_co2_db,
        verbose=verbose,
        prompt=prompt,
        top_k=100,
    )

    return en_co2_sql_chain
