# app/models.py
from .extensions import db

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    orientation = db.Column(db.String(100), nullable=False)
    gender_combo = db.Column(db.String(20), nullable=False, default="any")
    target = db.Column(db.String(20), default="random")

class PenaltyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    player_count = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.DateTime, default=db.func.now())
    finished = db.Column(db.Boolean, default=False)

    def generate_qr_code(self):
        import qrcode
        from io import BytesIO
        import base64
        url = f"https://nightmonopoly.ru/game?id={self.code}"
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"