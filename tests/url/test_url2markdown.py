import pytest

def url_to_markdown(url):
    return f"[Link]({url})"

def test_url_to_markdown():
    assert url_to_markdown("https://example.com") == "[Link](https://example.com)"
    assert url_to_markdown("http://test.com") == "[Link](http://test.com)"
    assert url_to_markdown("https://github.com") == "[Link](https://github.com)"