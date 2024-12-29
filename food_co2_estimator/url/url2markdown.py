import re

import requests
import validators
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from food_co2_estimator.url import (
    COMMENT_SELECTORS,
    HEADERS,
    TAGS_TO_DECOMPOSE,
    WIDGET_SELECTORS_TO_REMOVE,
)


def fetch_page_content(url: str, headers: dict) -> str | None:
    """Fetch the page content as text using requests."""
    if validators.url(url):
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError if the response was unsuccessful
        return response.text


def parse_html(html_content: str, parser: str = "html.parser") -> BeautifulSoup:
    """Return a BeautifulSoup object for the given HTML content."""
    return BeautifulSoup(html_content, parser)


def remove_unwanted_tags(soup: BeautifulSoup, tags: list) -> None:
    """Remove all unwanted tags from the soup."""
    for tag in soup(tags):
        tag.decompose()


def remove_comment_containers(soup: BeautifulSoup, selectors: list) -> None:
    """Remove all elements matching the provided CSS selectors."""
    selector_string = ", ".join(selectors)
    for element in soup.select(selector_string):
        element.decompose()


def remove_widgets(soup: BeautifulSoup, widget_selectors: list) -> None:
    """
    Remove any widgets found by the given (tag, attrs) tuples.
    For example: ("div", {"class": "widget sbi-feed-widget"})
    """
    for tag_name, attrs in widget_selectors:
        for widget in soup.find_all(tag_name, attrs=attrs):
            widget.decompose()


def remove_all_anchor_tags(soup: BeautifulSoup) -> None:
    """Remove all <a> tags from the soup."""
    for a_tag in soup.find_all("a"):
        a_tag.decompose()


def convert_body_to_markdown(soup: BeautifulSoup) -> str | None:
    """
    Convert the <body> content of the soup to Markdown,
    then trim whitespace and remove extra blank lines.
    Returns a cleaned Markdown string or None if no body found.
    """
    body_content = soup.body
    if not body_content:
        return

    markdown_text = md(str(body_content))
    # Trim whitespace
    markdown_text = markdown_text.strip()
    # Remove multiple blank lines
    markdown_text = re.sub(r"\n\s*\n+", "\n\n", markdown_text)

    return markdown_text


def get_markdown_from_url(url: str) -> str | None:
    """
    Given a URL, fetch its HTML, remove unwanted elements,
    and return the content of <body> as Markdown. Returns an
    empty string if there is no <body> content.
    """
    # 1. Fetch the page content
    html_text = fetch_page_content(url, HEADERS)
    if html_text is None:
        return

    # 2. Parse HTML
    soup = parse_html(html_text)

    # 3. Remove unwanted tags
    remove_unwanted_tags(soup, TAGS_TO_DECOMPOSE)

    # 4. Remove widgets (e.g., Instagram feed)
    remove_widgets(soup, WIDGET_SELECTORS_TO_REMOVE)

    # 5. Remove comment containers
    remove_comment_containers(soup, COMMENT_SELECTORS)

    # 6. Remove all <a> tags
    remove_all_anchor_tags(soup)

    # 7. Convert the body to Markdown
    return convert_body_to_markdown(soup)
