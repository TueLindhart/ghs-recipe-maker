from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup

from food_co2_estimator.url.url2markdown import (
    convert_body_to_markdown,
    fetch_page_content,
    get_markdown_from_url,
    parse_html,
    remove_all_anchor_tags,
    remove_comment_containers,
    remove_unwanted_tags,
    remove_widgets,
)


@pytest.mark.parametrize(
    "url,headers,expected_content",
    [
        ("https://example.com", {}, "<html>Example</html>"),
        ("Estimate this recipe", {}, None),
    ],
    ids=["valid_url", "invalid_url"],
)
def test_fetch_page_content(mocker, url, headers, expected_content):
    """Test fetching page content"""
    mock_response = Mock()
    mock_response.text = expected_content
    mock_response.raise_for_status = Mock()

    mocker.patch("requests.get", return_value=mock_response)

    result = fetch_page_content(url, headers)
    assert result == expected_content


@pytest.mark.parametrize(
    "html_content,parser,expected_type",
    [
        ("<html><body>Example</body></html>", "html.parser", BeautifulSoup),
        ("<html><body>Example</body></html>", "lxml", BeautifulSoup),
    ],
    ids=["html_parser", "lxml_parser"],
)
def test_parse_html(html_content, parser, expected_type):
    """Test parsing HTML content"""
    result = parse_html(html_content, parser)
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    "html_content,tags,expected_content",
    [
        ("<div><p>Text</p></div>", ["p"], "<div></div>"),
        ("<div><span>Text</span></div>", ["span"], "<div></div>"),
    ],
    ids=["remove_p_tag", "remove_span_tag"],
)
def test_remove_unwanted_tags(html_content, tags, expected_content):
    """Test removing unwanted tags"""
    soup = BeautifulSoup(html_content, "html.parser")
    remove_unwanted_tags(soup, tags)
    assert str(soup) == expected_content


@pytest.mark.parametrize(
    "html_content,selectors,expected_content",
    [
        ("<div class='comment'>Comment</div><p>Text</p>", [".comment"], "<p>Text</p>"),
        (
            "<div class='pingback'>Pingback</div><p>Text</p>",
            [".pingback"],
            "<p>Text</p>",
        ),
    ],
    ids=["remove_comment", "remove_pingback"],
)
def test_remove_comment_containers(html_content, selectors, expected_content):
    """Test removing comment containers"""
    soup = BeautifulSoup(html_content, "html.parser")
    remove_comment_containers(soup, selectors)
    assert str(soup) == expected_content


# A list of (tag, attributes_dict) for widgets to remove (expand as needed)
WIDGET_SELECTORS_TO_REMOVE = [
    ("div", {"class": "widget sbi-feed-widget"}),  # e.g. Instagram feed widget
    # Add more widget selectors here in the future
]


@pytest.mark.parametrize(
    "html_content,widget_selectors,expected_content",
    [
        (
            "<div class='widget sbi-feed-widget'>Widget</div><p>Text</p>",
            [("div", {"class": "widget sbi-feed-widget"})],
            "<p>Text</p>",
        ),
        (
            "<div class='instagram'>Instagram</div><p>Text</p>",
            [("div", {"class": "instagram"})],
            "<p>Text</p>",
        ),
    ],
    ids=["remove_widget", "remove_instagram"],
)
def test_remove_widgets(html_content, widget_selectors, expected_content):
    """Test removing widgets"""
    soup = BeautifulSoup(html_content, "html.parser")
    remove_widgets(soup, widget_selectors)
    assert str(soup) == expected_content


@pytest.mark.parametrize(
    "html_content,expected_content",
    [
        ("<a href='https://example.com'>Link</a><p>Text</p>", "<p>Text</p>"),
        ("<a href='https://example.com'>Link</a>", ""),
    ],
    ids=["remove_anchor_with_text", "remove_anchor_only"],
)
def test_remove_all_anchor_tags(html_content, expected_content):
    """Test removing all <a> tags"""
    soup = BeautifulSoup(html_content, "html.parser")
    remove_all_anchor_tags(soup)
    assert str(soup) == expected_content


@pytest.mark.parametrize(
    "html_content,expected_markdown",
    [
        ("<html><body><p>Hello, world!</p></body></html>", "Hello, world!"),
        (
            "<html><body><h1>Title</h1><p>Paragraph</p></body></html>",
            "Title\n=====\n\nParagraph",
        ),
        (
            "<html><body><ul><li>Item 1</li><li>Item 2</li></body></ul>",
            "* Item 1\n* Item 2",
        ),
        ("<html><body><strong>Bold</strong></body></html>", "**Bold**"),
        ("<html><body><em>Italic</em></body></html>", "*Italic*"),
        (
            "<html><body><a href='https://example.com'>Link</a></body></html>",
            "[Link](https://example.com)",
        ),
        (
            "<html><body><img src='image.jpg' alt='Image'></body></html>",
            "![Image](image.jpg)",
        ),
        ("<html><body><blockquote>Quote</blockquote></body></html>", "> Quote"),
        ("<html><body><code>Code</code></body></html>", "`Code`"),
        (
            "<html><body><pre><code>Preformatted Code</code></pre></body></html>",
            "```\nPreformatted Code\n```",
        ),
        (
            "<html><body><table><tr><td>Cell</td></tr></table></body></html>",
            "| Cell |\n| --- |",
        ),
        ("<html><body></body></html>", ""),  # Empty content
    ],
    ids=[
        "simple_paragraph",
        "header_and_paragraph",
        "unordered_list",
        "bold_text",
        "italic_text",
        "link",
        "image",
        "blockquote",
        "inline_code",
        "preformatted_code",
        "table",
        "empty_content",
    ],
)
def test_convert_body_to_markdown(html_content, expected_markdown):
    """Test conversion of HTML content to Markdown"""
    soup = BeautifulSoup(html_content, "html.parser")
    result = convert_body_to_markdown(soup)
    assert result == expected_markdown


@pytest.mark.parametrize(
    "url,expected_markdown",
    [
        ("https://example.com/simple", "Simple content"),
        ("https://example.com/complex", "Title\n=====\n\nComplex content"),
        ("https://example.com/empty", ""),  # Empty content
        ("https://example.com/invalid", "Error: Invalid URL"),  # Invalid URL
    ],
    ids=["simple_content", "complex_content", "empty_content", "invalid_url"],
)
def test_get_markdown_from_url(mocker, url, expected_markdown):
    """Test fetching and converting HTML content from URL to Markdown"""
    mock_html_content = {
        "https://example.com/simple": "<html><body><p>Simple content</p></body></html>",
        "https://example.com/complex": "<html><body><h1>Title</h1><p>Complex content</p></body></html>",
        "https://example.com/empty": "<html><body></body></html>",
        "https://example.com/invalid": None,
    }

    def mock_requests_get(url, headers=None):
        class MockResponse:
            def __init__(self, text):
                self.text = text

            def raise_for_status(self):
                pass

        if mock_html_content[url] is None:
            raise Exception("Invalid URL")
        return MockResponse(mock_html_content[url])

    mocker.patch("requests.get", side_effect=mock_requests_get)

    if url == "https://example.com/invalid":
        with pytest.raises(Exception, match="Invalid URL"):
            get_markdown_from_url(url)
    else:
        result = get_markdown_from_url(url)
        assert result == expected_markdown
