# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card

main = Blueprint('main', __name__)

# === Главная ===
@main.route('/')
def index():
    return render_template('index.html')

# === Выбор игроков ===
@main.route('/players')
def players():
    return render_template('players.html')

# === Настройка игроков ===
@main.route('/setup')
def setup():
    count = int(request.args.get('count', 2))
    return render_template('setup.html', count=count)

# === Обработка формы игроков ===
@main.route('/start', methods=['POST'])
def start():
    players = []
    for i in range(1, 5):
        name = request.form.get(f'name{i}')
        if name:
            gender = request.form.get(f'gender{i}')
            orientation = request.form.get(f'orientation{i}')
            players.append({
                'name': name,
                'gender': gender,
                'orientation': orientation
            })

    if len(players) < 2:
        flash('Нужно хотя бы 2 игрока', 'error')
        return redirect(url_for('main.players'))

    session['players'] = players
    session['current'] = 0
    session['level'] = 1  # Начинаем с 1 уровня
    return redirect(url_for('main.game'))

# === Игра: показ карточки ===
@main.route('/game')
def game():
    if 'players' not in session:
        return redirect(url_for('main.players'))

    players = session['players']
    current = session['current']
    current_player = players[current]
    next_player = players[(current + 1) % len(players)]
    level = session['level']

    # Фильтр по ориентации
    allowed_orientations = ['Любая']
    if current_player['orientation'] == 'Би':
        allowed_orientations += ['Гетеро', 'Лесби', 'Другое']
    else:
        allowed_orientations.append(current_player['orientation'])

    # Фильтр по полу
    allowed_genders = [current_player['gender'], 'Любой']

    # Ищем карточку
    card = Card.query.filter(
        Card.level == level,
        Card.orientation.in_(allowed_orientations),
        Card.gender.in_(allowed_genders),
        Card.target.in_(['Партнёр', 'Любой'])
    ).order_by(db.func.random()).first()

    # Если нет — переходим на следующий уровень
    if not card and level < 4:
        session['level'] += 1
        flash(f'🎉 Переход на уровень {session["level"]}!', 'info')
        return redirect(url_for('main.game'))

    # Если и на 4 уровне нет — игра окончена
    if not card:
        flash('🎉 Все карточки пройдены! Игра завершена.', 'success')
        return redirect(url_for('main.players'))

    return render_template('game.html', card=card, player=current_player, next=next_player)

# === Следующий игрок ===
@main.route('/next')
def next_player():
    if 'players' in session:
        session['current'] = (session['current'] + 1) % len(session['players'])
    return redirect(url_for('main.game'))
# === Тайный вход ===
@main.route('/admin-secret')
def admin_secret():
    return redirect(url_for('main.admin_login', next=url_for('main.admin')))

# === Вход в админку ===
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next') or url_for('main.index')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'Vladimirovich' and password == 'Timur':
            session['admin_logged_in'] = True
            flash('✅ Добро пожаловать, командир!', 'success')
            return redirect(next_page)
        else:
            flash('❌ Неверный логин или пароль', 'error')
    
    return render_template('admin/login.html', next=next_page)

# === Админка: главная ===
@main.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    cards = Card.query.all()
    return render_template('admin/index.html', cards=cards)

# === Остальное: админка, вход и т.д. — остаётся как есть ===