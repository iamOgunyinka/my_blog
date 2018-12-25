#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  article_writer.py
#  
#  Copyright 2019 Josh <Josh@JOSHUA>

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from models import Article
from threading import Thread
from datetime import datetime
import os, redis, time, shutil


cache_pass, port_number = os.environ.get('redis_pass'), int(os.environ.get('redis_port'))
data_cache = redis.StrictRedis(password=cache_pass, port=port_number)
article_key = 'blog:article_key'

sleep_time = 5

def create_app():
    application = Flask(__name__)

    application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
    application.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    return application


app = create_app()
db = SQLAlchemy()
db.init_app(app)


def main(logger, argv):
    """
    usage: prog "title of article" "writer" "category" "filename"
    """
    if len(argv) != 5:
        logger.write('unable to process blog\n\nusage: prog "title of article" "writer" "category" "filename"')
        exit(-1)
    
    title, writer, category, filename = (argv[1], argv[2], argv[3], argv[4])
    brief_text = '' # a brief introduction of the text file
    basename = ''
    try:
        filename = os.path.normpath(os.path.abspath(filename))
        with open(filename, 'r') as article_text:
            brief_text = article_text.read(300)
        with app.app_context():
            blog_path = os.path.join(current_app.instance_path, 'blogs')
            if not os.path.exists(blog_path):
                os.makedirs(blog_path)
        shutil.copy2(filename, blog_path) #throws FileNotFoundError if src/dest isn't found
        basename = os.path.join(blog_path, os.path.basename(filename))
    except Exception as e:
        logger.write(str(e))
        exit(-1)
    time.sleep(sleep_time)
    with app.app_context():
        try:
            new_article = Article(topic=title, categories=category, writer=writer,\
                date_written=datetime.now(), brief=brief_text, blog_filename=basename)
            db.session.add(new_article)
            db.session.commit()
            with open(basename, 'r') as text_file:
                text = ''
                for line in text_file:
                    text += line
                data_cache.hmset(article_key, {basename: text})
        except Exception as exception:
            db.session.rollback()
            logger.write(str(exception))


event_logger = open('./article_logs.txt', 'a')

if __name__ == '__main__':
    import sys
    new_thread = Thread(target=main, args=[event_logger, sys.argv])
    new_thread.setDaemon(False)
    new_thread.start()
    new_thread.join()
    event_logger.close()
