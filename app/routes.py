# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from .models import db, Card, PenaltyCard
import random
import string
import qrcode
from io import BytesIO
import base64

# === ✅ СНАЧАЛА создаём Blueprint ===
main = Blueprint('main', __name__)


# === 🔐 Админ: вход/выход ===
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function


@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'Vladimirovich' and request.form['password'] == 'Timur':
            session['admin_logged_in'] = True
            return redirect('/admin')
        flash('❌ Неверный логин или пароль')
    return '''
    <form method="POST" style="text-align:center;margin:50px;">
        <h2>🔐 Вход в админку</h2>
        <input name="username" placeholder="Логин" required><br><br>
        <input type="password" name="password" placeholder="Пароль" required><br><br>
        <button type="submit">Войти</button>
    </form>
    '''


@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('✅ Выход выполнен')
    return redirect('/admin/login')


@main.route('/admin')
@admin_required
def admin():
    cards = Card.query.all()
    penalties = PenaltyCard.query.all()
    return render_template('admin/index.html', cards=cards, penalties=penalties)


# === 🎮 ОСНОВНЫЕ МАРШРУТЫ ===

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/age-check', methods=['GET', 'POST'])
def age_check():
    if request.method == 'POST':
        age = request.form.get('age')
        if age and int(age) >= 18:
            session['age_verified'] = True
            return redirect('/game-setup')
        flash('❌ Вам должно быть 18+')
    return render_template('age_check.html')


@main.route('/game-setup')
def game_setup():
    if not session.get('age_verified'):
        return redirect('/age-check')
    players = session.get('players', [])
    return render_template('game_setup.html', players=players)


@main.route('/add-player', methods=['POST'])
def add_player():
    name = request.form['name'].strip()
    if not name:
        flash('❌ Имя не может быть пустым')
        return redirect('/game-setup')
    players = session.get('players', [])
    if len(players) >= 4:
        flash('❌ Максимум 4 игрока')
    else:
        players.append({
            'name': name,
            'gender': request.form['gender'],
            'orientation': request.form['orientation']
        })
        session['players'] = players
    return redirect('/game-setup')


@main.route('/remove-player/<int:index>')
def remove_player(index):
    players = session.get('players', [])
    if 0 <= index < len(players):
        players.pop(index)
        session['players'] = players
    return redirect('/game-setup')


# === 🚀 START GAME — ключевой маршрут ===
@main.route('/start-game')
def start_game():
    players = session.get('players', [])
    if len(players) < 2:
        flash('❌ Минимум 2 игрока')
        return redirect('/game-setup')

    session.update({
        'game_code': ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
        'current_player_index': 0,
        'current_level': 1,
        'used_cards': [],
        'game_started': True
    })
    return redirect('/game')  # ✅ Переход в игру


# === 🎲 ИГРОВОЙ ЭКРАН ===
@main.route('/game')
def game():
    if not session.get('game_started') or len(session.get('players', [])) < 2:
        return redirect('/game-setup')

    players = session['players']
    current_idx = session['current_player_index']
    current_player = players[current_idx]
    current_level = session['current_level']
    player_combo = ''.join([p['gender'] for p in players])

    available_cards = Card.query.filter_by(level=current_level).all()
    available_cards = [
        c for c in available_cards
        if "any" in c.gender_combo or player_combo in [combo.strip() for combo in c.gender_combo.split(',')]
    ]
    available_cards = [c for c in available_cards if c.id not in session['used_cards']]

    if not available_cards:
        if current_level < 4:
            session['current_level'] += 1
            session['used_cards'] = []
            return redirect('/game')
        else:
            flash('🎉 Все карточки использованы!')
            return redirect('/game-setup')

    card = random.choice(available_cards)
    session['used_cards'].append(card.id)

    next_idx = (current_idx + 1) % len(players)
    session['current_player_index'] = next_idx

    return render_template(
        'game.html',
        card=card,
        current_player=current_player,
        next_player=players[next_idx],
        current_level=current_level
    )


# === 🔄 Сброс игры ===
@main.route('/reset-game')
def reset_game():
    session.clear()
    flash('🔄 Игра сброшена')
    return redirect('/game-setup')


# === ⚠️ ЭКРАН ШТРАФА ===
@main.route('/penalty')
def show_penalty():
    if not session.get('game_started'):
        return redirect('/game-setup')
    try:
        penalty = random.choice(PenaltyCard.query.all())
        duration = penalty.duration
        return render_template('penalty.html', penalty=penalty, duration=duration)
    except:
        flash('❌ Ошибка загрузки штрафа')
        return redirect('/game')


# === 🖼️ ГЕНЕРАТОР QR-КОДА — В КОНЦЕ! ===
@main.app_context_processor
def inject_qr():
    def generate_qr_base64(data):
        try:
            qr = qrcode.QRCode(version=1, box_size=4, border=2)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print("QR Error:", e)
            return ""
    return dict(generate_qr_base64=generate_qr_base64)