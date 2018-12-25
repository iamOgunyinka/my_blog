#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright June, 2018 Joshua <ogunyinkajoshua@yahoo.com>
#

from flask import Flask
from flask_moment import Moment
from models import db
from flask_uploads import configure_uploads, patch_request_class
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
import os

moment = Moment()
bootstrap = Bootstrap()
csrf = CSRFProtect()

def create_app():
    app = Flask( __name__ )
    app.config['SECRET_KEY'] = os.environ.get( 'SECRET_KEY' )
    app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get( 'WTF_KEY' )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOADS_DEFAULT_DEST'] = os.environ.get('UPLOAD_DIR')
    app.config['UPLOADS_DEFAULT_URL'] = os.environ.get('GENERAL_UPLOAD_URL')

    moment.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    
    from views import main
    app.register_blueprint(main)
    
    #~ csrf.exempt(main)
    return app
