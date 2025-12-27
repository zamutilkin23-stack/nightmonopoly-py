# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card
import random

main = Blueprint('main', __name__)


# === Главная: проверка 18+ ===
@main.route('/')
def index():
    return render_template('index.html')


# === Ввод игроков ===
@main.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        try:
            player_data = request.form.getlist('player')
            players = []
            for p in player_data:
                if p.strip():
                    name, gender, orientation = p.split('|')
                    players.append({
                        'name': name,
                        'gender': gender,
                        'orientation': orientation
                    })
            if len(players) < 2:
                flash('Нужно минимум 2 игрока', 'error')
                return render_template('players.html')
            session['players'] = players
            session['current'] = 0
            return redirect(url_for('main.game'))
        except Exception as e:
            flash('Ошибка в данных игроков', 'error')
            return render_template('players.html')

    return render_template('players.html')


# === Игра: показ карточки ===
@main.route('/game')
def game():
    players = session.get('players')
    if not players:
        return redirect(url_for('main.players'))

    current = session['current']
    current_player = players[current]
    next_idx = (current + 1) % len(players)
    next_player = players[next_idx]

    # Фильтрация карточек по ориентации
    allowed_orientations = ['Любая']
    if current_player['orientation'] == 'Би':
        allowed_orientations += ['Гетеро', 'Лесби', 'Другое']
    else:
        allowed_orientations.append(current_player['orientation'])

    card = Card.query.filter(
        Card.orientation.in_(allowed_orientations),
        Card.gender.in_([current_player['gender'], 'Любой']),
        Card.target.in_(['Партнёр', 'Любой'])
    ).order_by(db.func.random()).first()

    if not card:
        card = Card.query.order_by(db.func.random()).first()

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
    return redirect(url_for('main.admin_login'))


# === Админка: вход ===
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'Vladimirovich' and request.form['password'] == 'Timur':
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin'))
        flash('Неверный логин или пароль', 'error')
    return render_template('admin/login.html')


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
    flash('Вы вышли из админки', 'info')
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
        flash(f'❌ Ошибка: {e}', 'error')
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
            flash(f'❌ Ошибка: {e}', 'error')
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
        flash(f'❌ Ошибка: {e}', 'error')
    return redirect(url_for('main.admin'))