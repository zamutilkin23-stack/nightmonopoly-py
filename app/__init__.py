from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'nightfanta-2025-secret-key'

    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'nightfanta.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app