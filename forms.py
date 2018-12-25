from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, DateField, SelectField, FileField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional, InputRequired, NumberRange
from flask_uploads import UploadSet, IMAGES
import os


general_upload_directory = os.environ.get('GENERAL_UPLOAD_DIRECTORY')
