import requests
from pyrsspipe.input.base import AbstractInput
from rfeed import Item, Feed, Guid
from pydantic import BaseModel


class PatreonInput(AbstractInput):
    @staticmethod
    def execute(logger, **kwargs) -> Feed:
        campaign_id = kwargs["campaign_id"]

        api_url = "https://www.patreon.com/api/posts"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept-Language": "en-US,en;q=0.5",
        }
        posts_data = []
        with requests.session() as s:
            logger.info(f"campaign id is {campaign_id}")
            logger.info(f"getting posts")
            data = s.get(
                api_url,
                headers=headers,
                params={
                    "filter[campaign_id]": campaign_id,
                    "filter[contains_exclusive_posts]": "true",
                    "sort": "-published_at",
                },
            ).json()
            logger.info(f'found {len(data["data"])} posts')
            for d in data["data"]:
                post_data = {
                    "title": d["attributes"]["title"],
                    "link": f"https://www.patreon.com/{d['attributes']['patreon_url']}",
                    "description": d["attributes"]["teaser_text"],
                    "author": "placeholder@example.py",
                }
                posts_data.append(post_data)

        logger.info(f"finished pull for {campaign_id}")

        feed_items = []
        for post_data in posts_data:
            feed_items.append(
                Item(
                    title=post_data["title"],
                    link=post_data["link"],
                    description=post_data["description"],
                    author=post_data["author"],
                    guid=Guid(post_data["link"]),
                )
            )

        feed = Feed(
            title="Patreon",
            link="https://www.patreon.com",
            description="",
            language="en-US",
            items=feed_items,
        )
        return feed

    @staticmethod
    def get_validator():
        class Validator(BaseModel):
            campaign_id: int
        return Validator
