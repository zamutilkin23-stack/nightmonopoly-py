# app/models.py
from .extensions import db

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    orientation = db.Column(db.String(20), nullable=False)  # М-Ж, Ж-М и т.д.
    gender_combo = db.Column(db.String(20), nullable=False)  # Парень, Девушка, Любой
    target = db.Column(db.String(20), nullable=False)  # Партнёр, Любой

class PenaltyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)