# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card

main = Blueprint('main', __name__)


# === Главная — проверка 18+ ===
@main.route('/')
def index():
    return render_template('index.html')


# === Тест: игроки (упрощённо) ===
@main.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        players = []
        for i in range(1, 5):
            name = request.form.get(f'name{i}')
            if name:
                gender = request.form.get(f'gender{i}') or 'Любой'
                orientation = request.form.get(f'orientation{i}') or 'Любая'
                players.append({'name': name, 'gender': gender, 'orientation': orientation})
        if len(players) < 2:
            flash('Минимум 2 игрока', 'error')
            return render_template('players.html')
        session['players'] = players
        session['current'] = 0
        return redirect(url_for('main.game'))
    return render_template('players.html')


@main.route('/game')
def game():
    if 'players' not in session:
        return redirect(url_for('main.players'))
    return "<h1>🎮 Игра запущена!</h1><p>Карточки ещё не подключены, но структура работает.</p>"


# === Тайный вход ===
@main.route('/admin-secret')
def admin_secret():
    return redirect(url_for('main.admin_login', next=url_for('main.admin')))


# === Админка: вход — с сессией ===
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next') or url_for('main.index')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'Vladimirovich' and password == 'Timur':
            session['admin_logged_in'] = True
            flash('✅ Добро пожаловать, командир', 'success')
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