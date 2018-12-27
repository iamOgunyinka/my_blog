#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2018 Joshua <ogunyinkajoshua@gmail.com>
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, url_for, redirect, request, abort, flash, current_app, jsonify
from flask_wtf.csrf import CSRFError
from sqlalchemy.exc import IntegrityError, OperationalError
from models import db, ContactMessage, Article, Comment
from werkzeug.utils import secure_filename
from logging import log, ERROR
import os, redis, json


main = Blueprint('main', __name__)
cache_pass,port_number=os.environ.get('redis_pass'),int(os.environ.get('redis_port'))
instant_data_cache = redis.StrictRedis(password=cache_pass,port=port_number)
feedback = 'blog:feedback'
article_key = 'blog:article_key'


@main.errorhandler(CSRFError)
def handle_csrf_error_handler(error):
    flash(error)
    return redirect(url_for('main.index_route'))


@main.route('/home')
@main.route('/index')
@main.route('/')
def index_route():
    # get latest articles first
    all_articles = Article.get_articles(db.session.query(Article).order_by(Article.id.desc()).all())
    return render_template('index.html', articles=all_articles)


@main.route('/blog')
def blog_route():
    try:
        article_id = int(request.args.get('blog_id'))
        article_object = db.session.query(Article).filter_by(id=article_id).first()
        if article_object is None:
            return abort(404)
        article_text = instant_data_cache.hmget(article_key, article_object.blog_filename)
        if not article_text:
            article_text = ''
            with open(article.blog_filename, 'r') as text_file:
                for line in text_file:
                    article_text += line
            instant_data_cache.hmset(article_key, {article_object.blog_filename: article_text})
        else:
            if type(article_text) == list:
                article_text = article_text[0]
            article_text = article_text.decode()
        article_data = Article.get_single_article(article_object)
        return render_template('article.html', article_text=article_text, metadata=article_data)
    except ValueError as exc:
        print(exc)
        return redirect(url_for('main.index_route'))
    except Exception as exception:
        print(exception)
        return redirect(url_for('main.index_route'))


@main.route('/about_me')
def about_me_route():
    return render_template('about.html')


@main.route('/contacts', methods=['GET'])
def contacts_route():
    return render_template('contact.html')


@main.route('/receive_message', methods=['POST'])
def get_in_touch_route():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    try:
        new_message = ContactMessage(fullname=name, email=email, subject=subject, message=message)
        db.session.add(new_message)
        db.session.commit()
        cached_message = json.dumps({'name': name, 'email': email, 'subject': subject, 'message': message})
        instant_data_cache.lpush(feedback, cached_message)
        flash('Your message has been sent')
    except IntegrityError as ie:
        db.session.rollback()
        log(WARNING, ie)
        flash('There was an error sending your message')
    return redirect(url_for('main.contacts_route'))
