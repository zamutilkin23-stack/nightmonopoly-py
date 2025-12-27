# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card, PenaltyCard
import qrcode
from io import BytesIO
import base64

main = Blueprint('main', __name__)

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
    penalty_cards = PenaltyCard.query.all()
    return render_template('admin/index.html', cards=cards, penalty_cards=penalty_cards)

# === Админка: выход ===
@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin_login'))

# === Добавить карточку ===
@main.route('/admin/add-card', methods=['POST'])
def add_card():
    card = Card(
        text=request.form['text'],
        level=int(request.form['level']),
        orientation=request.form['orientation'],
        gender_combo=request.form['gender_combo'],
        target=request.form['target']
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

# === Главная страница ===
@main.route('/')
def index():
    # Генерируем QR-код благодарности
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("Спасибо за игру в NightMonopoly! 🌙")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    return render_template('index.html', qr_code=qr_code)

# === Показать карточку ===
@main.route('/card', methods=['POST'])
def show_card():
    card_id = request.form.get('card_id', type=int)
    if not card_id:
        return render_template('card.html', error="Введите номер карточки")
    card = Card.query.get(card_id)
    if not card:
        return render_template('card.html', error=f"Карточка №{card_id} не найдена")
    return render_template('card.html', card=card)