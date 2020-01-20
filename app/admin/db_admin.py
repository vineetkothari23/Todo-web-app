#!/usr/bin/env python
from datetime import datetime, timedelta
from app import db
from flask import current_app
from app.models import User, Challenge, Task, challengers
from config import Config

def tearDown(db):
    db.session.remove()
    db.drop_all()
    db.session.commit()
