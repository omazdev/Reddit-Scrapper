from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from sqlalchemy import UniqueConstraint

from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Post(Base):
    __tablename__ = "post"
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        UniqueConstraint('publish_date', 'comments_link',
                         name='_post_pub_link_uc'),
    )
    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    link = Column('link', Text())
    content = Column('content', Text())
    publish_date = Column('publish_date', DateTime)
    votes_count = Column('votes_count', Integer())
    flair = Column('flair', String(20))
    author_id = Column(Integer, ForeignKey('author.id'))  # Many posts to one author
    comments_count = Column('comments_count',Integer())
    comments_link = Column('comments_link', String(250))
    comments = relationship('Comment', backref="post")  # One post to many comments


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(50), unique=True)
    link = Column('link', String(250))
    posts = relationship('Post', backref='author') # One author to many Posts
    comments = relationship('Comment', backref='author') # One author to many Comments


class Comment(Base):
    __tablename__ = "comment"
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        UniqueConstraint('publish_date', 'author_id',
                         'post_id', name='_comment_pub_post_uc'),
    )
    id = Column(Integer, primary_key=True)
    content = Column('content', Text())
    publish_date = Column('publish_date', DateTime)
    score = Column('score', Integer())
    post_id = Column(Integer, ForeignKey('post.id'))  # Many comments to one post
    author_id = Column(Integer, ForeignKey('author.id'))  # Many comments to one author

