# wsgi.py
from app import create_app

app = create_app()

# Render импортирует `app` — этого достаточно