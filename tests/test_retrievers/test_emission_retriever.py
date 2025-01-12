from typing import List, Tuple

import pytest
from langchain_core.documents import Document

from food_co2_estimator.retrievers.emission_retriever import (
    INGREDIENT_UNITS,
    NUMBER_WORDS,
    batch_emission_retriever,
    clean_ingredient_list,
    get_clean_regex,
    parse_retriever_output,
    remove_quantities,
    remove_units,
)


def create_number_word_test_cases() -> List[Tuple[str, str]]:
    """Create test cases for number word removal"""
    normal_cases = [(f"{word} tomatoes", "tomatoes") for word in NUMBER_WORDS]

    uppercase_cases = [
        (f"{word.upper()} tomatoes", "tomatoes") for word in NUMBER_WORDS
    ]

    return normal_cases + uppercase_cases


def create_number_word_test_ids() -> List[str]:
    """Create test ids for number word test cases"""
    normal_ids = [f"number_word_{word}" for word in NUMBER_WORDS]
    uppercase_ids = [f"uppercase_{word}" for word in NUMBER_WORDS]
    return normal_ids + uppercase_ids


def create_test_cases() -> List[Tuple[str, str]]:
    # Basic unit tests
    normal_cases = [(f"{unit} tomatoes", "tomatoes") for unit in INGREDIENT_UNITS]

    # Test uppercase variants
    uppercase_cases = [
        (f"{unit.upper()} tomatoes", "tomatoes") for unit in INGREDIENT_UNITS
    ]

    return normal_cases + uppercase_cases


def create_test_ids() -> List[str]:
    normal_ids = [f"unit_{unit}" for unit in INGREDIENT_UNITS]
    uppercase_ids = [f"uppercase_{unit}" for unit in INGREDIENT_UNITS]
    return normal_ids + uppercase_ids


@pytest.mark.parametrize(
    "ingredient,expected",
    create_number_word_test_cases(),
    ids=create_number_word_test_ids(),
)
def test_remove_number_words(ingredient: str, expected: str):
    """Test removal of all number words

    Args:
        ingredient: String containing number word and ingredient
        expected: String with number word removed
    """
    result = remove_quantities(ingredient)
    assert result == expected


@pytest.mark.parametrize(
    "ingredient,expected", create_test_cases(), ids=create_test_ids()
)
def test_remove_all_units(ingredient: str, expected: str):
    """Test removal of all units

    Args:
        ingredient: Input string containing unit and ingredient
        expected: Expected output with unit removed
    """
    result = remove_units(ingredient)
    assert result == expected


def test_get_clean_regex():
    """Test that the regex pattern is created correctly"""
    pattern = get_clean_regex()
    assert pattern is not None
    # Test pattern matches number words
    assert pattern.match("one tomato")
    # Test pattern matches units
    assert pattern.match("kg tomatoes")
    # Test pattern matches complex cases
    assert pattern.match("2 kg of tomatoes")


@pytest.mark.parametrize(
    "ingredients,expected",
    [
        (
            ["2 kg tomatoes", "1 liter milk", "3 large eggs"],
            ["tomatoes", "milk", "eggs"],
        ),
        (["one cup flour", "two tablespoons sugar"], ["flour", "sugar"]),
        (["500g butter", "250ml cream"], ["butter", "cream"]),
        (
            [],  # Empty list
            [],
        ),
        (
            ["tomatoes"],  # No quantities or units
            ["tomatoes"],
        ),
    ],
    ids=[
        "basic_measurements",
        "number_words",
        "metric_units",
        "empty_list",
        "no_units",
    ],
)
def test_clean_ingredient_list(ingredients, expected):
    """Test cleaning a list of ingredients"""
    result = clean_ingredient_list(ingredients)
    assert result == expected


def create_test_cleaning_cases():
    """Create test cases and ids for integrated cleaning tests"""
    test_cases = [
        ("2 kg of tomatoes", "tomatoes"),
        ("1-2 cups milk", "milk"),
        ("1/2 cup of sugar", "sugar"),
        ("3.5 liters water", "water"),
        ("one large onion", "onion"),
        ("tomatoes", "tomatoes"),
        ("", ""),
        ("2-3 tablespoons of olive oil", "olive oil"),
        ("0.5 kg flour", "flour"),
        ("1,5 kg potatoes", "potatoes"),
        (".5 kg rice", "rice"),
        ("1/4 cup butter", "butter"),
        ("1/2 teaspoon salt", "salt"),
        ("3/4 dl cream", "cream"),
        ("2-3 tablespoons oil", "oil"),
        ("2 to 3 carrots", "carrots"),
        ("2~3 onions", "onions"),
        ("2...3 cloves", "cloves"),
        ("two-three apples", "apples"),
        ("half lemon", "lemon"),
        ("quarter orange", "orange"),
        ("1 1/2 cups flour", "flour"),
        ("1.5-2 dl milk", "milk"),
        ("one-and-a-half spoons", "spoons"),
        ("a pinch of salt", "salt"),
        ("some sugar", "sugar"),
        ("something", "something"),
        ("tomato", "tomato"),
    ]

    test_ids = [
        "with_of",
        "range_quantity",
        "fraction_quantity",
        "decimal_quantity",
        "word_quantity",
        "no_quantity",
        "empty_string",
        "complex_case",
        "decimal_variation_1",
        "decimal_variation_2",
        "decimal_variation_3",
        "fraction_1",
        "fraction_2",
        "fraction_3",
        "range_1",
        "range_2",
        "range_3",
        "range_4",
        "number_word_1",
        "number_word_2",
        "number_word_3",
        "mixed_format_1",
        "mixed_format_2",
        "mixed_format_3",
        "edge_case_1",
        "edge_case_2",
        "remove_substring_1",
        "remove_substring_2",
    ]

    return test_cases, test_ids


@pytest.mark.parametrize(
    "input_string,expected",
    create_test_cleaning_cases()[0],
    ids=create_test_cleaning_cases()[1],
)
def test_integrated_cleaning(input_string: str, expected: str):
    """Test complete cleaning process (quantities and units)"""
    no_quantity = remove_quantities(input_string)
    no_units = remove_units(no_quantity)
    assert no_units == expected


def test_parse_retriever_output():
    # Arrange
    mock_documents = [
        Document(page_content="beef", metadata={"Total kg CO2e/kg": 60.0}),
        Document(page_content="chicken", metadata={"Total kg CO2e/kg": 6.1}),
        Document(page_content="no_emission", metadata={}),
    ]

    # Act
    result = parse_retriever_output(mock_documents)

    # Assert
    expected = {"beef": "60.0 kg CO2e / kg", "chicken": "6.1 kg CO2e / kg"}
    assert result == expected


def test_batch_emission_retriever(monkeypatch: pytest.MonkeyPatch):
    # Arrange
    ingredients = ["2 kg tomatoes", "1 liter milk", "3 large eggs"]

    mock_retriever_output = {
        "tomatoes": "2.0 kg CO2e / kg",
        "milk": "1.0 kg CO2e / kg",
        "eggs": "3.0 kg CO2e / kg",
    }

    class MockRetrieverChain:
        def batch(self, inputs):
            return list(mock_retriever_output.values())

    def mock_get_emission_retriever_chain(*args, **kwargs):
        return MockRetrieverChain()

    monkeypatch.setattr(
        "food_co2_estimator.retrievers.emission_retriever.get_emission_retriever_chain",
        mock_get_emission_retriever_chain,
    )

    # Act
    result = batch_emission_retriever(ingredients)

    # Assert
    expected = dict(zip(ingredients, mock_retriever_output.values()))
    assert result == expected
