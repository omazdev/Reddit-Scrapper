Scrape-subreddits
=======================
This is a web scraper written in ``Python 3.8.6`` using ``Scrapy 2.4.0`` to scrape ``old.reddit.com``.

It actually scrapes the ``wevdev`` subreddit to get the posts and their related comments.

The posts, comments, authors are stored in a ``Sqlite`` DB by default (see Database section below to use ``Mysql`` instead). 

This project uses:

* ``demoji==0.3.0`` to replace emojis with text.
* ``SQLAlchemy 1.3.20`` as an ORM (see models.py).
* ``scrapy-user-agents 0.1.1`` for user agents rotation.
* ``scrapy-proxy-pool 0.1.7`` for proxy rotation (disabled by default, see instructions below for how to enable it). 

Installation
------------

    pip install -r requirements.txt 

Usage
-----

In webdev_spider.py, set the desired number of pages to scrape:

    pages_to_scrape = 3

To run the spider in webdev_spider.py :

    #webdev_spider.py
    scrapy crawl webdev

To save crawled data in a json file, first disable the pipelines in settings.py :  

    #settings.py
    ITEM_PIPELINES = {
        #'subreddit.pipelines.DuplicatesPipeline': 100,
        #'subreddit.pipelines.SavePostsCommentsPipeline': 200,
    }

Then run :

    scrapy crawl webdev -o webdev-posts.json


Database
--------

The project uses Sqlite to store scraped data, however, to use ``Mysql``, create a DB named ``'scrapy_subreddit'`` (utf8 encoding) then in settings.py, replace CONNECTION_STRING :

    #settings.py
    # MySQL (PyMySQL)
    CONNECTION_STRING = "{drivername}://{user}:{passwd}@{host}/{db_name}?charset=utf8".format(
        drivername="mysql+pymysql",
        user="your-username",
        passwd="your-password",
        host="localhost",
        db_name="scrapy_subreddit",
    )

User agents/proxies rotation
----------------------------

By default, only user agents rotation is used. However, to use proxies rotation along with user agents, in settings.py uncomment these lines :
    
    #settings.py
    PROXY_POOL_ENABLED = True

    DOWNLOADER_MIDDLEWARES = {
        ...
        'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
        'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
        ...
    }

PS: Scraping time might be long using proxies rotation.

Log
---

The Logger output is saved in log.txt, settings.py :

    #settings.py
    LOG_FILE="log.txt"
    LOG_ENABLED=True

Contribution
------------

This project was developed for educational purposes. However, PRs are welcome to improve the project.

Disclaimer
----------

This project can only be used for educational purposes. Using this software against target systems without prior permission is illegal, and any damages from misuse of this software will not be the responsibility of the author.
