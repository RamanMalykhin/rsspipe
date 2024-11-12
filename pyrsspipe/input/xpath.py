import lxml.html
import requests
import logging
from pyrsspipe.input.base import AbstractInput
from rfeed import Item, Feed, Guid


def get_feed_items(
    page_url: str,
    article_items_xpath: str,
    item_title_xpath: str,
    item_content_xpath: str,
    item_url_xpath: str,
    debug_mode: bool,
    logger: logging.Logger,
) -> Feed:
    debug_mode = bool(debug_mode)
    response = requests.get(page_url)
    tree = lxml.html.fromstring(response.content)
    tree.make_links_absolute(page_url)

    feed_items = []
    articles = tree.xpath(article_items_xpath)

    if debug_mode:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Scraped {len(articles)} items from {page_url}")

    for article in articles:
        logger.debug(f"processing {article}")

        title = str(article.xpath(item_title_xpath)[0])
        logger.debug(f"found title: {title}")
        content = str(article.xpath(item_content_xpath)[0])
        logger.debug(f"found content: {content}")
        url = str(article.xpath(item_url_xpath)[0])
        logger.debug(f"found url: {url}")

        feed_item = {}
        feed_item["title"] = title
        feed_item["description"] = content
        feed_item["link"] = url
        feed_items.append(feed_item)

    if debug_mode:
        logger.setLevel(logging.INFO)

    return feed_items
