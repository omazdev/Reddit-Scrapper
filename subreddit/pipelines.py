from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from subreddit.models import Post, Comment, Author, db_connect, create_table
import logging


class SavePostsCommentsPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        
    
    def fill_post(self,item ,session ,post ,post_author):
        """
        Fill the post object with item attributes
        """
        post.title = item["post_title"]
        post.link = item["post_link"]
        post.content = item["post_content"]
        post.publish_date = item["post_date"]
        post.votes_count = int(item["post_votes_nbr"])
        post.flair = item["post_flair"]
        post.comments_count = int(item["post_comments_nbr"])
        post.comments_link = item["post_comments_link"]

        post_author.name = item["post_author"]
        post_author.link = item["post_author_link"]

        # check whether the author exists
        exist_author = session.query(Author).filter_by(
            name=post_author.name
        ).first()

        if exist_author is not None:  # the current author exists
            post.author = exist_author
        else:
            post.author = post_author
            
        return post

    
    def fill_comment(self,session ,post , comment ,post_comment ,comment_author):
        """
        Fill the comment object with item attributes
        """
        comment.content = post_comment["comment_text"]
        comment.publish_date = post_comment["comment_date"]
        comment.score = int(post_comment["comment_score"])
        comment.post = post

        comment_author.name = post_comment["comment_author"]
        comment_author.link = post_comment["comment_author_link"]

        # check whether the author exists
        exist_author = session.query(
            Author).filter_by(name=comment_author.name).first()

        if exist_author is not None:  # the current author exists
            comment.author = exist_author
        else:
            comment.author = comment_author
    
    def process_item(self, item, spider):
        """
        Save posts and related comments in the database
        """
        for field in item.fields:
            item.setdefault(field, 'NULL')

        session = self.Session()
        post = Post()
        comment = Comment()
        post_author = Author()
            
        # check whether the post exists 
        # supposing combination of publish_date & comments_link is unique  
        exist_post = session.query(Post).filter_by(
            publish_date=item["post_date"],
            comments_link=item["post_comments_link"],
        ).first()

        if exist_post is not None:  # the current post exists
            # update the post 
            post = exist_post
            logging.info(f'****Updating post : {post.title} ****')
            self.fill_post(item, session, post, post_author)
        else:
            # insert as a new post
            try:
                self.fill_post(item, session, post, post_author)
                logging.info(f'****Adding post : {post.title} ****')
                session.add(post)
            except:
                session.rollback()
                raise
        
        # Saving the post id to use later when querying for comments
        post_id = post.id
        try:
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        # check whether the current post has comments or not
        if "post_comments" in item and item["post_comments"][0] != "NULL":
            for post_comment in item["post_comments"]:
                comment = Comment()
                comment_author = Author()
                
                # check whether the comment exists 
                exist_comment = session.query(Comment).filter_by(
                    content=post_comment["comment_text"],
                    publish_date=post_comment["comment_date"],
                    post_id=post_id,
                ).join(Author).filter(
                    Author.name == post_comment["comment_author"],
                ).first()

                if exist_comment is not None:  # the current comment exists
                    # update the comment 
                    comment = exist_comment
                    logging.info(f'****Updating comment : {comment.author.name} | {comment.publish_date} ****')
                    self.fill_comment(session, post, comment, post_comment, comment_author)
                else:
                    # insert as a new comment
                    try:
                        self.fill_comment(session, post, comment, post_comment, comment_author)
                        logging.info(f'****Adding comment : {comment.author.name} | {comment.publish_date} ****')
                        session.add(comment)
                    except:
                        session.rollback()
                        raise

            try:
                session.commit()

            except:
                session.rollback()
                raise

            finally:
                session.close()

        return item


class DuplicatesPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        logging.info("****DuplicatesPipeline: database connected****")

    def process_item(self, item, spider):
        session = self.Session()
        exist_post = session.query(Post).filter_by(
            title=item["post_title"]).first()
        if exist_post is not None:  # the current post exists
            raise DropItem("Duplicate item found: %s" % item["post_title"])
            session.close()
        else:
            return item
            session.close()
