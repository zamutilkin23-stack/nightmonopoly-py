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
        count = int(request.form['count'])
        players = []
        for i in range(count):
            name = request.form.get(f'name_{i}')
            gender = request.form.get(f'gender_{i}')
            orientation = request.form.get(f'orientation_{i}')
            players.append({'name': name, 'gender': gender, 'orientation': orientation})
        session['players'] = players
        session['current'] = 0
        return redirect(url_for('main.game'))
    return render_template('players.html')


# === Игра: показ карточки ===
@main.route('/game')
def game():
    players = session.get('players')
    if not players:
        return redirect(url_for('main.players'))

    current_player = players[session['current']]
    next_idx = (session['current'] + 1) % len(players)
    next_player = players[next_idx]

    # Случайная карточка (по фильтрам)
    card = Card.query.filter(
        Card.orientation.in_([current_player['orientation'], 'Любая']),
        Card.gender_combo.in_([current_player['gender'], 'Любой']),
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
        flash('Неверный логин или пароль')
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
    return redirect(url_for('main.index'))


# === Добавить карточку ===
@main.route('/admin/add-card', methods=['POST'])
def add_card():
    card = Card(
        text=request.form['text'],
        level=int(request.form['level']),
        orientation=request.form['orientation'],
        gender_combo=request.form['gender_combo'],
        target=request.form['target'],
        image_url=request.form.get('image_url') or None
    )
    db.session.add(card)
    db.session.commit()
    flash('Карточка добавлена')
    return redirect(url_for('main.admin'))


# === Редактировать карточку ===
@main.route('/admin/edit-card/<int:id>', methods=['GET', 'POST'])
def edit_card(id):
    card = Card.query.get_or_404(id)
    if request.method == 'POST':
        card.text = request.form['text']
        card.level = int(request.form['level'])
        card.orientation = request.form['orientation']
        card.gender_combo = request.form['gender_combo']
        card.target = request.form['target']
        card.image_url = request.form.get('image_url') or None
        db.session.commit()
        flash('Карточка обновлена')
        return redirect(url_for('main.admin'))
    return render_template('admin/edit_card.html', card=card)


# === Удалить карточку ===
@main.route('/admin/delete-card/<int:id>', methods=['POST'])
def delete_card(id):
    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    flash('Карточка удалена')
    return redirect(url_for('main.admin'))