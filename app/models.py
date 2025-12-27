# app/models.py
from .extensions import db

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    orientation = db.Column(db.String(20), nullable=False)  # Гетеро, Би и т.д.
    gender = db.Column(db.String(20), nullable=False)      # Парень, Девушка
    target = db.Column(db.String(20), nullable=False)      # Партнёр, Любой
    image_url = db.Column(db.String(300), nullable=True)   # GIF или фото