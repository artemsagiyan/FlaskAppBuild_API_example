from flask_appbuilder import AppBuilder, expose, BaseView, ModelView, ModelRestApi
from flask import Flask, render_template, url_for, redirect, Response, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.registerviews import BaseRegisterUser
from flask_appbuilder.security.decorators import protect
from flask_appbuilder.api import rison, BaseApi, expose, safe
from flask import g, request, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

from flask import current_app

from sqlalchemy.sql import exists
from sqlalchemy import asc, desc, exc, or_

import ast
import json
import os

from app import db, appbuilder

UPLOAD_FOLDER = '/home/kmk/Pictures'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app) 

class Human(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    middle_name = db.Column(db.String(20))

    num_of_pasport = db.Column(db.String(10))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return 'Article %r' % self.id

class Users(BaseApi):
    
    @expose('/', methods=['GET'])
    @protect()
    @safe
    def index(self) -> Response:
        return Response({"message":"page is opened"}, status=200, mimetype='application/json')

    #the own page
    @expose('/register/', methods=['GET', 'POST'])
    @protect()
    @safe
    def registerdata(self) -> Response:
        try:
            request_data = request.get_json(force=True)
            name = request_data['name']
            last_name = request_data['last_name']
            middle_name = request_data['middle_name']
            num_of_pasport = request_data['num_of_pasport']

            person = Human(name=name, last_name=last_name, middle_name=middle_name, num_of_pasport=num_of_pasport)
        
            db.session.add(person)
            db.session.commit()

            return self.response({"message":"Request completed successfully"}, status=200, mimetype='application/json')

        except:
            db.session.rollback()

            return Response({"message":"Warning:Haven't been add"}, status=400, mimetype='application/json')
    
    #update a definite data
    @expose('/update/<ind:id>', methods=['PUT'])
    @protect()
    @safe
    def updatedata(self, id: int) -> Response:

        article = Human.query.get_or_404(id)

        try:
            request_data = request.get_json(force=True)
            article.name = request_data['name']
            article.last_name = request_data['last_name']
            article.middle_name = request_data['middle_name']
            article.num_of_pasport = request_data['num_of_pasport']

            db.session.commit()

            return Response({"message":"Data in DB is changed"}, status=200, mimetype='application/json')
        
        except:
            db.session.rollback()

            return Response({"message":"Warning: Data haven't been change"}, status=400, mimetype="application/json")

    #delete a definite data
    @expose("/delete/<int:id>/", methods=['DELETE'])
    @protect()
    @safe
    def deletedata(self, id: int) -> Response:

        article = Human.query.get_or_404(id)

        try:
            db.session.delete(article)
            db.session.commit()

            return Response({"message":"Data is deleted"}, status=200, mimetype='application/json')
        
        except:
            db.session.rollback()

            return Response({"message":"Don't find such data"}, mimetype='application/json')

    #to add a new picture in way: "UPLOAD_FOLDER"
    @expose('/image/', methods=['GET', 'POST'])
    @protect()
    @safe
    def upload_file(self) -> Response:

        try:
            if 'file1' not in request.files:
                return 'there is no file1 in form!'
            file1 = request.files['file1']
            path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file1.save(path)

            return path

        except:

            return Response({"message":"Image is uplouded"}, status=200, mimetype='application/json')

    #all data
    @expose("/posts/")
    @protect
    @safe
    def get(self) -> Response:
        article = Human.query.order_by(Human.last_name).all()
        
        return article

appbuilder.add_view_no_menu(Users())
appbuilder.add_api(Users)