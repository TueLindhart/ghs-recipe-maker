import pytest
from your_module import CO2EstimatorModel

def test_co2_estimator_model_validation():
    valid_data = {
        "field1": "value1",
        "field2": 10,
        "field3": True
    }
    model = CO2EstimatorModel(**valid_data)
    assert model.field1 == "value1"
    assert model.field2 == 10
    assert model.field3 is True

def test_co2_estimator_model_invalid_data():
    invalid_data = {
        "field1": 123,
        "field2": "not_a_number",
        "field3": "not_a_boolean"
    }
    with pytest.raises(ValueError):
        CO2EstimatorModel(**invalid_data)