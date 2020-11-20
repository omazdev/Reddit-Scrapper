from scrapy.item import Item, Field
from itemloaders.processors import MapCompose, TakeFirst, Join
from datetime import datetime


def convert_date(text):
    # convert string Sun Nov 1 12:12:35 2020 UTC to Python date
    if text == "NULL":
        return None
    else:
        return datetime.strptime(text, '%a %b %d %H:%M:%S %Y %Z')


def strip_comments_count(text):
    """
    strip "comments and comment strings"
    """
    result = text.strip(" comments")
    if result == "":
        return "0"
    else:
        return result


class PostItem(Item):
    post_title = Field(
        output_processor=TakeFirst(),
    )
    post_link = Field(
        output_processor=TakeFirst(),
    )
    post_author = Field(
        output_processor=TakeFirst(),
    )
    post_author_link = Field(
        output_processor=TakeFirst(),
    )
    post_date = Field(
        input_processor=MapCompose(convert_date),
        output_processor=TakeFirst(),
    )
    post_comments_nbr = Field(
        input_processor=MapCompose(strip_comments_count),
        output_processor=TakeFirst(),
    )
    post_comments_link = Field(
        output_processor=TakeFirst(),
    )
    post_votes_nbr = Field(
        output_processor=TakeFirst(),
    )
    post_flair = Field(
        output_processor=TakeFirst(),
    )
    post_content = Field(
        output_processor=Join(),
    )
    post_comments = Field()


class CommentItem(Item):
    comment_author = Field(
        output_processor=TakeFirst(),
    )
    comment_author_link = Field(
        output_processor=TakeFirst(),
    )
    comment_score = Field(
        output_processor=TakeFirst(),
    )
    comment_date = Field(
        input_processor=MapCompose(convert_date),
        output_processor=TakeFirst(),
    )
    comment_text = Field(
        output_processor=Join(),
    )
