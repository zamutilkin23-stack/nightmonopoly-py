<<<<<<< HEAD
# wsgi.py
from app import create_app

app = create_app()

if __name__ == '__main__':
=======
# wsgi.py
from app import create_app

app = create_app()

if __name__ == '__main__':
>>>>>>> 05fc079 (🚀 Первый коммит: NightMonopoly v1.0 готов к деплою)
    app.run(host='0.0.0.0', port=5000, debug=False)