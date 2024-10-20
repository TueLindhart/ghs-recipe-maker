from langchain.output_parsers import RetryWithErrorOutputParser
from langchain.schema.output_parser import BaseOutputParser

from food_co2_estimator.utils.openai_model import get_model


def get_retry_parser(parser: BaseOutputParser):
    return RetryWithErrorOutputParser.from_llm(parser=parser, llm=get_model())
