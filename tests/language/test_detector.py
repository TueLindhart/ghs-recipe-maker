import pytest

def test_language_detection():
    assert detect_language("Hello, how are you?") == "English"
    assert detect_language("Bonjour, comment ça va?") == "French"
    assert detect_language("Hola, ¿cómo estás?") == "Spanish"
    assert detect_language("Hallo, wie geht es dir?") == "German"