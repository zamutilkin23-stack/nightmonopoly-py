# app/models.py
from .extensions import db

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    orientation = db.Column(db.String(100), nullable=False)
    gender_combo = db.Column(db.String(20), nullable=False)
    target = db.Column(db.String(20), nullable=False)

class PenaltyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, nullable=False)