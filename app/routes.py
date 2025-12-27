# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card, PenaltyCard
import qrcode
from io import BytesIO
import base64

main = Blueprint('main', __name__)


# === Главная страница ===
@main.route('/')
def index():
    # Генерация QR-кода благодарности
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("Спасибо за игру в NightMonopoly! 💋")
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
    
    # Штраф только если уровень >= 2
    penalty = PenaltyCard.query.first() if card.level >= 2 else None
    
    return render_template('card.html', card=card, penalty=penalty)


# === Тайный вход в админку (невидимый маршрут) ===
@main.route('/admin-secret')
def admin_secret():
    # При заходе — запоминаем, откуда пришёл (например, с главной или карточки)
    next_page = request.args.get('next') or url_for('main.index')
    return redirect(url_for('main.admin_login', next=next_page))


# === Админка: вход ===
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Получаем, куда идти после входа
    next_page = request.args.get('next') or url_for('main.index')

    if request.method == 'POST':
        if request.form['username'] == 'Vladimirovich' and request.form['password'] == 'Timur':
            session['admin_logged_in'] = True
            flash('✅ Добро пожаловать в админку', 'success')
            return redirect(next_page)
        flash('❌ Неверный логин или пароль', 'error')
    
    return render_template('admin/login.html', next=next_page)


# === Админка: главная ===
@main.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    cards = Card.query.all()
    penalty_cards = PenaltyCard.query.all()
    return render_template('admin/index.html', cards=cards, penalty_cards=penalty_cards)


# === Админка: выход → возвращает туда, откуда пришёл ===
@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы вышли из админки', 'info')
    # Возвращаемся на предыдущее место
    return redirect(url_for('main.index'))


# === Добавить карточку ===
@main.route('/admin/add-card', methods=['POST'])
def add_card():
    try:
        card = Card(
            text=request.form['text'].strip(),
            level=int(request.form['level']),
            orientation=request.form['orientation'],
            gender_combo=request.form['gender_combo'],
            target=request.form['target']
        )
        db.session.add(card)
        db.session.commit()
        flash('✅ Карточка успешно добавлена', 'success')
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
            card.gender_combo = request.form['gender_combo']
            card.target = request.form['target']
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
        flash(f'❌ Ошибка при удалении: {e}', 'error')
    return redirect(url_for('main.admin'))


# === Добавить штраф ===
@main.route('/admin/add-penalty', methods=['POST'])
def add_penalty():
    try:
        penalty = PenaltyCard(
            text=request.form['text'].strip()
        )
        db.session.add(penalty)
        db.session.commit()
        flash('✅ Штраф добавлен', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Ошибка: {e}', 'error')
    return redirect(url_for('main.admin'))


# === Удалить штраф ===
@main.route('/admin/delete-penalty/<int:id>', methods=['POST'])
def delete_penalty(id):
    try:
        penalty = PenaltyCard.query.get_or_404(id)
        db.session.delete(penalty)
        db.session.commit()
        flash('🗑️ Штраф удалён', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Ошибка: {e}', 'error')
    return redirect(url_for('main.admin'))