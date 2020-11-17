from scrapy.item import Item, Field
from scrapy.loader.processors import TakeFirst


class PostItem(Item):
    post_title = Field()
    post_link = Field()
    post_author = Field()
    post_author_link = Field()
    post_date = Field()
    post_comments_nbr = Field()
    post_comments_link = Field()
    post_votes_nbr = Field()
    post_flair = Field()
    post_content = Field()
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
        output_processor=TakeFirst(),
    )
    comment_text = Field(
        # output_processor=TakeFirst(),
    )
