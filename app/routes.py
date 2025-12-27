# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card

main = Blueprint('main', __name__)


# === Главная: проверка 18+ ===
@main.route('/')
def index():
    return render_template('index.html')


# === Тест админки ===
@main.route('/test-admin')
def test_admin():
    logged_in = session.get('admin_logged_in')
    return f"<h1>Тест админки</h1><p>Вход: <b>{'да' if logged_in else 'нет'}</b></p><a href='/admin-secret'>Войти</a>"


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

        # ✅ Проверка
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


# === Админка: выход ===
@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы вышли из админки', 'info')
    return redirect(url_for('main.index'))