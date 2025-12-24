# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Card, PenaltyCard
from .extensions import db

main = Blueprint('main', __name__)

# Главная
@main.route('/')
def index():
    return render_template('index.html')

# Проверка возраста
@main.route('/age-check', methods=['GET', 'POST'])
def age_check():
    if request.method == 'POST':
        if request.form.get('age') == 'yes':
            session['age_verified'] = True
            return redirect(url_for('main.game_setup'))
        else:
            return redirect(url_for('main.index'))
    return render_template('age_check.html')

# Настройка игроков
@main.route('/game-setup', methods=['GET', 'POST'])
def game_setup():
    if not session.get('age_verified'):
        return redirect(url_for('main.age_check'))

    if request.method == 'POST':
        name = request.form.get('name')
        gender = request.form.get('gender')
        orientation = request.form.get('orientation')
        players = session.get('players', [])
        players.append({'name': name, 'gender': gender, 'orientation': orientation})
        session['players'] = players

    players = session.get('players', [])
    return render_template('game_setup.html', players=players)

# Удаление игрока
@main.route('/remove-player/<int:index>', methods=['POST'])
def remove_player(index):
    players = session.get('players', [])
    if 0 <= index < len(players):
        players.pop(index)
        session['players'] = players
    return redirect(url_for('main.game_setup'))

# Начало игры
@main.route('/start-game')
def start_game():
    if not session.get('players'):
        flash('Добавьте хотя бы одного игрока!')
        return redirect(url_for('main.game_setup'))

    import random
    session['game_code'] = str(random.randint(100000, 999999))
    session['current_player_index'] = 0
    return redirect(url_for('main.game'))

# Игровой экран
@main.route('/game')
def game():
    players = session.get('players', [])
    if not players:
        return redirect(url_for('main.game_setup'))

    current_idx = session.get('current_player_index', 0)
    current = players[current_idx]
    next_idx = (current_idx + 1) % len(players)
    session['current_player_index'] = next_idx

    card = Card.query.order_by(db.func.random()).first()
    if not card:
        card_text = "Нет доступных карточек"
    else:
        card_text = card.text

    return render_template('game.html', player=current, card=card_text)

# Экран штрафа
@main.route('/penalty')
def penalty():
    card = PenaltyCard.query.order_by(db.func.random()).first()
    duration = card.duration if card else 60
    text = card.text if card else "Выполните штраф: станцуйте!"
    return render_template('penalty.html', text=text, duration=duration)

# === АДМИНКА ===

# Логин (простой пароль)
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['login'] == 'Vladimirovich' and request.form['password'] == 'Timur':
            session['admin'] = True
            return redirect(url_for('main.admin_index'))
        else:
            flash('Неверный логин или пароль')
    return render_template('admin/login.html')

# Главная админки
@main.route('/admin')
def admin_index():
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))
    cards = Card.query.all()
    penalties = PenaltyCard.query.all()
    return render_template('admin/index.html', cards=cards, penalties=penalties)

# Добавить карточку
@main.route('/admin/add-card', methods=['GET', 'POST'])
def add_card():
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    if request.method == 'POST':
        try:
            text = request.form['text']
            level = int(request.form['level'])
            orientation = request.form['orientation']
            gender_combo = request.form['gender_combo']
            target = request.form['target']

            card = Card(
                text=text,
                level=level,
                orientation=orientation,
                gender_combo=gender_combo,
                target=target
            )
            db.session.add(card)
            db.session.commit()
            flash('Карточка добавлена!')
            return redirect(url_for('main.admin_index'))
        except Exception as e:
            flash(f'Ошибка: {e}')
            return redirect(url_for('main.add_card'))

    return render_template('admin/add_card.html')

# Добавить штраф
@main.route('/admin/add-penalty', methods=['GET', 'POST'])
def add_penalty():
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    if request.method == 'POST':
        try:
            text = request.form['text']
            duration = int(request.form['duration'])

            penalty = PenaltyCard(text=text, duration=duration)
            db.session.add(penalty)
            db.session.commit()
            flash('Штраф добавлен!')
            return redirect(url_for('main.admin_index'))
        except Exception as e:
            flash(f'Ошибка: {e}')
            return redirect(url_for('main.add_penalty'))

    return render_template('admin/add_penalty.html')

# Редактировать карточку
@main.route('/admin/edit-card/<int:id>', methods=['GET', 'POST'])
def edit_card(id):
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    card = Card.query.get_or_404(id)
    if request.method == 'POST':
        try:
            card.text = request.form['text']
            card.level = int(request.form['level'])
            card.orientation = request.form['orientation']
            card.gender_combo = request.form['gender_combo']
            card.target = request.form['target']
            db.session.commit()
            flash('Карточка обновлена!')
            return redirect(url_for('main.admin_index'))
        except Exception as e:
            flash(f'Ошибка: {e}')

    return render_template('admin/edit_card.html', card=card)

# Удалить карточку
@main.route('/admin/delete-card/<int:id>', methods=['POST'])
def delete_card(id):
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    flash('Карточка удалена!')
    return redirect(url_for('main.admin_index'))
