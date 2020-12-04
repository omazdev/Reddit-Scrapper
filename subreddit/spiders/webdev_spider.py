import scrapy
from scrapy.loader import ItemLoader
from ..items import PostItem, CommentItem
import demoji
import logging

class WebDevSpider(scrapy.Spider):
    name = "webdev"
    start_urls = ['https://old.reddit.com/r/webdev/']
    pages_index = 1
    pages_to_scrape = 1
    try:
        demoji.download_codes()
    except Exception as e:
        logging.info("****Demoji Failed to load : {e}****")

    def load_css(self, selector, loader, field_name, css, null_value):
        if selector.css(css).get() is not None:
            loader.add_css(field_name, css)
        else:
            loader.add_value(field_name, null_value)

    def parse(self, response):
        # extract posts title, url, date, username, flairs, nbr of comments & nbr of votes.
        for post in response.css('div#siteTable div.thing.link[data-whitelist-status="all_ads"]'):
            post_loader = ItemLoader(item=PostItem(), selector=post)

            self.load_css(post, post_loader, 'post_title',
                          '.title.may-blank::text', "NULL")
            self.load_css(post, post_loader, 'post_link',
                          '.title.may-blank::attr(href)', "NULL")
            self.load_css(post, post_loader, 'post_author',
                          'a.author.may-blank::text', "NULL")
            self.load_css(post, post_loader, 'post_author_link',
                          'a.author.may-blank::attr(href)', "NULL")
            self.load_css(post, post_loader, 'post_date',
                          'time.live-timestamp::attr(title)', "NULL")
            self.load_css(post, post_loader, 'post_comments_nbr',
                          'a.bylink.comments::text', "0")
            self.load_css(post, post_loader, 'post_comments_link',
                          'a.bylink.comments::attr(href)', "NULL")
            self.load_css(post, post_loader, 'post_votes_nbr',
                          'div.score.unvoted::attr(title)', "0")
            self.load_css(post, post_loader, 'post_flair',
                          'span.linkflairlabel::attr(title)', "NULL")

            post_item = post_loader.load_item()
            post_comments_link = post.css(
                'a.bylink.comments::attr(href)').get()

            if post_comments_link is not None:
                yield response.follow(post_comments_link, self.parse_comments, meta={'post_item': post_item})

        next_page = response.css('span.next-button a::attr(href)').get()
        if next_page is not None and self.pages_index < self.pages_to_scrape:
            self.pages_index += 1
            yield response.follow(next_page, self.parse)

    def parse_comments(self, response):
        # for each post extract comments : author, comment, score, date.
        post_item = response.meta['post_item']
        post_loader = ItemLoader(item=post_item, response=response)

        # Get post content
        if response.css('div#siteTable > div.thing div.usertext-body p').get() is None:
            post_loader.add_value('post_content', "NULL")
        else:
            post_loader.add_css(
                'post_content', 'div#siteTable > div.thing div.usertext-body p')

        # TODO Get post_content for other forms of post (video, external link, ...)

        # Get comments
        comments = response.css(
            'div.commentarea div.sitetable.nestedlisting div.thing.noncollapsed.comment > div.entry.unvoted')
        # If no comments,
        if not comments:
            post_loader.add_value('post_comments', "NULL")
        else:
            for comment in comments:
                # Check if the comment is not deleted
                if comment.css('p.tagline > em::text').get() != "[deleted]":
                    comment_loader = ItemLoader(
                        item=CommentItem(), selector=comment)

                    self.load_css(comment, comment_loader, 'comment_author',
                                'p.tagline > a.author.may-blank::text', "NULL")
                    self.load_css(comment, comment_loader, 'comment_author_link',
                                'p.tagline > a.author.may-blank::attr(href)', "NULL")
                    self.load_css(comment, comment_loader, 'comment_score',
                                'p.tagline > span.score.unvoted::attr(title)', 0)
                    self.load_css(comment, comment_loader, 'comment_date',
                                'p.tagline > time.live-timestamp::attr(title)', "NULL")
                    self.load_css(comment, comment_loader, 'comment_text',
                                'form.usertext > div.usertext-body p', "NULL")

                    comment_item = comment_loader.load_item()

                    post_loader.add_value('post_comments', dict(comment_item))

        yield post_loader.load_item()
