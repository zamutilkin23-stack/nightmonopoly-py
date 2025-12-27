from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


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
    return "<h1>🎮 Игра запущена!</h1><p>Карточка появится позже.</p>"


# === Админка ===
@main.route('/admin-secret')
def admin_secret():
    return redirect(url_for('main.admin_login', next=url_for('main.admin')))


@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next') or url_for('main.index')
    if request.method == 'POST':
        if request.form['username'] == 'Vladimirovich' and request.form['password'] == 'Timur':
            session['admin_logged_in'] = True
            flash('✅ Добро пожаловать', 'success')
            return redirect(next_page)
        flash('❌ Ошибка входа', 'error')
    return render_template('admin/login.html', next=next_page)


@main.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    cards = Card.query.all()
    return render_template('admin/index.html', cards=cards)


@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы вышли', 'info')
    return redirect(url_for('main.index'))