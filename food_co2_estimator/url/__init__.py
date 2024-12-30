HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )
}

# Tags to remove by default
TAGS_TO_DECOMPOSE = ["script", "style", "noscript", "header", "footer", "img"]

# CSS selectors to remove comments or pingbacks
COMMENT_SELECTORS = [".comment", ".pingback"]

# A list of (tag, attributes_dict) for widgets to remove (expand as needed)
WIDGET_SELECTORS_TO_REMOVE = [
    ("div", {"class": "widget sbi-feed-widget"}),  # e.g. Instagram feed widget
    # Add more widget selectors here in the future
]
