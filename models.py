#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2018 Joshua <ogunyinkajoshua@gmail.com>

import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DEFAULT_DISPLAY_PICTURE = os.environ.get('DEFAULT_DP')


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True, index=True)
    fullname = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String( 128 ), nullable = False, index = True)
    subject = db.Column(db.String(256), nullable=False)
    message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return '<ContactMessages Name: {}, Message: {}>\n'.format(self.fullname, self.message)

    
class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    topic = db.Column(db.String(256), nullable=False, unique=True)
    categories = db.Column(db.String(512), nullable=False)
    writer = db.Column(db.String(128), nullable=False)
    date_written = db.Column(db.DateTime, nullable=False)
    brief = db.Column(db.Text, nullable=False)
    blog_filename = db.Column(db.String(512), nullable=False, unique=True)
    comments = db.relationship('Comment', backref='user_comments')
    
    @staticmethod
    def get_articles(articles_object):
        if articles_object is None: return []
        return [ { 'topic': article.topic, 'date': article.date_written,\
            'writer': article.writer, 'comments': len(article.comments),\
            'category': article.categories, 'topic_id': article.id,\
            'brief': article.brief } for article in articles_object ]
    
    @staticmethod
    def get_comments(comments):
        if len(comments) == 0: return [] 
        return [ {'name': comment.commenter_name, 'comment': comment.comment_text,\
            'replies': get_comments(comment.replies)} for comment in comments]

    @staticmethod
    def get_single_article(article):
        if article is None: return article
        date_written = article.date_written.strftime('%b %d, %Y')
        return { 'topic': article.topic, 'date': date_written, 'writer': article.writer,\
            'comments': Article.get_comments(article.comments), 'category': article.categories,\
            'num_comment': len(article.comments) }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    commenter_name = db.Column(db.String(256), nullable=False)
    commenter_email = db.Column(db.String(256), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    replies = db.relationship('Comment')
    response_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
