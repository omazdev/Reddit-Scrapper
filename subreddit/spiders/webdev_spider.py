import scrapy


class WebDevSpider(scrapy.Spider):
    name = "webdev"
    start_urls = ['https://old.reddit.com/r/webdev/']
    pages_index = 1
    pages_to_scrape = 1

    def parse(self, response):
        # extract posts title, url, date, username, flairs, nbr of comments & nbr of votes.
        for post in response.css('.thing.link'):
            post_item = {
                'post_title': post.css('.title.may-blank::text').get(),
                'post_link': post.css('.title.may-blank::attr(href)').get(),
                'post_author': post.css('a.author.may-blank::text').get(),
                'post_author_link': post.css('a.author.may-blank::attr(href)').get(),
                'post_date': post.css('time.live-timestamp::attr(title)').get(),
                'post_comments_nbr': post.css('a.bylink.comments::text').get(),
                'post_comments_link': post.css('a.bylink.comments::attr(href)').get(),
                'post_votes_nbr': post.css('div.score.unvoted::attr(title)').get(),
                'post_flair': post.css('span.linkflairlabel::attr(title)').get(),
            }
            yield response.follow(post_item['post_comments_link'], self.parse_comments, meta={'post_item': post_item})

        next_page = response.css('span.next-button a::attr(href)').get()
        if next_page is not None and self.pages_index < self.pages_to_scrape:
            self.pages_index += 1
            yield response.follow(next_page, self.parse)

    def parse_comments(self, response):
        # for each post extract comments : author, comment, score, date.
        post_item = response.meta['post_item']
        post_item['comments'] = {}
        comment_index = 0
        
        # Get post content
        post_item['post_content'] = response.css(
            'div.thing.linkflair-showoff div.usertext-body p').getall()

        # TODO Get post_content for other forms of post (video, external link, ...)
        
        # Get comments
        for comment in response.css('div.thing.noncollapsed.comment'):
            post_item['comments'][comment_index] = dict(
                comment_author=comment.css('a.author.may-blank::text').get(),
                comment_author_link=comment.css(
                    'a.author.may-blank::attr(href)').get(),
                comment_score=comment.css(
                    'span.score.unvoted::attr(title)').get(),
                comment_date=comment.css(
                    'time.live-timestamp::attr(title)').get(),
                comment_text=comment.css('div.entry.unvoted')[0].css(
                    'form.usertext > div.usertext-body p').getall(),
            )

            comment_index += 1

        yield post_item
