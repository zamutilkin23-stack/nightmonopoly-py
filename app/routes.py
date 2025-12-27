# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card

main = Blueprint('main', __name__)


# === Главная: проверка 18+ ===
@main.route('/')
def index():
    return render_template('index.html')


# === Выбор игроков ===
@main.route('/players')
def players():
    return render_template('players.html')


# === Настройка количества игроков ===
@main.route('/setup')
def setup():
    count = int(request.args.get('count', 2))
    return render_template('setup.html', count=count)


# === Старт игры ===
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
        flash('Нужно минимум 2 игрока', 'error')
        return redirect(url_for('main.players'))

    session['players'] = players
    session['current'] = 0
    session['level'] = 1
    return redirect(url_for('main.game'))


# === Игра: показ карточки ===
@main.route('/game')
def game():
    if 'players' not in session:
        return redirect(url_for('main.players'))

    players = session['players']
    current = session['current']
    player = players[current]
    next_player = players[(current + 1) % len(players)]
    level = session['level']

    # Фильтр по ориентации
    allowed_orientations = ['Любая']
    if player['orientation'] == 'Би':
        allowed_orientations += ['Гетеро', 'Лесби', 'Другое']
    else:
        allowed_orientations.append(player['orientation'])

    # Фильтр по полу
    allowed_genders = [player['gender'], 'Любой']

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

    if not card:
        flash('🎉 Все карточки пройдены!', 'success')
        return redirect(url_for('main.players'))

    return render_template('game.html', card=card, player=player, next=next_player)


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


# === Админка: вход ===
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next') or url_for('main.index')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Vladimirovich' and password == 'Timur':
            session['admin_logged_in'] = True
            flash('✅ Добро пожаловать!', 'success')
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


# === Админка: выход ===
@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы вышли', 'info')
    return redirect(url_for('main.index'))


# === Добавить карточку ===
@main.route('/admin/add-card', methods=['POST'])
def add_card():
    try:
        card = Card(
            text=request.form['text'].strip(),
            level=int(request.form['level']),
            orientation=request.form['orientation'],
            gender=request.form['gender'],
            target=request.form['target'],
            image_url=request.form.get('image_url') or None
        )
        db.session.add(card)
        db.session.commit()
        flash('✅ Карточка добавлена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Ошибка: {str(e)}', 'error')
    return redirect(url_for('main.admin'))


# === Редактировать карточку ===
@main.route('/admin/edit-card/<int:id>', methods=['GET', 'POST'])
def edit_card(id):
    card = Card.query.get_or_404(id)
    if request.method == 'POST':
        try:
            card.text = request.form['text'].strip()
            card.level = int(request.form['level'])
            card.orientation = request.form['orientation']
            card.gender = request.form['gender']
            card.target = request.form['target']
            card.image_url = request.form.get('image_url') or None
            db.session.commit()
            flash('✅ Карточка обновлена', 'success')
            return redirect(url_for('main.admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Ошибка: {str(e)}', 'error')
    return render_template('admin/edit_card.html', card=card)


# === Удалить карточку ===
@main.route('/admin/delete-card/<int:id>', methods=['POST'])
def delete_card(id):
    try:
        card = Card.query.get_or_404(id)
        db.session.delete(card)
        db.session.commit()
        flash('🗑️ Карточка удалена', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Ошибка: {str(e)}', 'error')
    return redirect(url_for('main.admin'))