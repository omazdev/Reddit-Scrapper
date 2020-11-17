import scrapy
from scrapy.loader import ItemLoader
from ..items import PostItem, CommentItem

class WebDevSpider(scrapy.Spider):
    name = "webdev"
    start_urls = ['https://old.reddit.com/r/webdev/']
    pages_index = 1
    pages_to_scrape = 1


    def parse(self, response):
        # extract posts title, url, date, username, flairs, nbr of comments & nbr of votes.
        for post in response.css('div#siteTable .thing.link'):
            loader = ItemLoader(item=PostItem(), selector=post)
            loader.add_css('post_title', '.title.may-blank::text')
            loader.add_css('post_link', '.title.may-blank::attr(href)')
            loader.add_css('post_author', 'a.author.may-blank::text')
            loader.add_css('post_author_link', 'a.author.may-blank::attr(href)')
            loader.add_css('post_date', 'time.live-timestamp::attr(title)')
            loader.add_css('post_comments_nbr', 'a.bylink.comments::text')
            loader.add_css('post_comments_link', 'a.bylink.comments::attr(href)')
            loader.add_css('post_votes_nbr', 'div.score.unvoted::attr(title)')
            loader.add_css('post_flair', 'span.linkflairlabel::attr(title)')
            post_item = loader.load_item()
            post_comments_link = post.css('a.bylink.comments::attr(href)').get()
            
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
        if post_loader.add_css('post_content', 'div#siteTable > div.thing div.usertext-body p') is None:
            post_loader.add_value('post_content', 'None')
        
        # TODO Get post_content for other forms of post (video, external link, ...)
        
        # Get comments
        for comment in response.css('div.commentarea div.sitetable.nestedlisting div.thing.noncollapsed.comment > div.entry.unvoted'):
            comment_loader = ItemLoader(item=CommentItem(), selector=comment)
            comment_loader.add_css('comment_author', 'p.tagline > a.author.may-blank::text')
            comment_loader.add_css('comment_author_link', 'p.tagline > a.author.may-blank::attr(href)')
            comment_loader.add_css('comment_score', 'p.tagline > span.score.unvoted::attr(title)')
            comment_loader.add_css('comment_date', 'p.tagline > time.live-timestamp::attr(title)')
            comment_loader.add_css('comment_text', 'form.usertext > div.usertext-body p')
            
            comment_item = comment_loader.load_item()
            
            post_loader.add_value('post_comments', dict(comment_item))

        yield post_loader.load_item()
