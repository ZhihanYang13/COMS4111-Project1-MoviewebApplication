# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 14:43:55 2022

@author: YYY
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange

from datetime import date

class addUser(FlaskForm):
    email = StringField(label=('Email:'))
    name = StringField('Name:')
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    password = IntegerField('Set your password (0-9) with at least 6 characters:',
                            [InputRequired(), NumberRange(min=100000, message='Invalid password')])
    submit = SubmitField('Add')


class Comment(FlaskForm):
    rate = RadioField('Rate:', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
                                        (8, 8), (9, 9), (10, 10)])
    comment = StringField('Write your comment: ')
    submit = SubmitField('Comment')
    


class addlikelist(FlaskForm):
  name=StringField(label=('Name of likelist:'))
  share_value = SelectField('Share', choices=[(1, 'public'), (0, 'private')])
  submit = SubmitField('Add')

class includelikelist(FlaskForm):
  submit = SubmitField('Add')


def stringdate():
    today = date.today()
    return str(today)