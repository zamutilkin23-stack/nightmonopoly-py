# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card, PenaltyCard  # ✅ КРИТИЧЕСКИ ВАЖНО

main = Blueprint('main', __name__)


# === АДМИНКА: ВХОД ===
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'Vladimirovich' and request.form['password'] == 'Timur':
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin'))
        flash('Неверный логин или пароль', 'error')
    return render_template('admin/login.html')


# === АДМИНКА: ГЛАВНАЯ ===
@main.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    cards = Card.query.all()
    penalty_cards = PenaltyCard.query.all()
    return render_template('admin/index.html', cards=cards, penalty_cards=penalty_cards)


# === АДМИНКА: ВЫХОД ===
@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin_login'))


# === АДМИНКА: ДОБАВИТЬ КАРТОЧКУ ===
@main.route('/admin/add-card', methods=['POST'])
def add_card():
    try:
        card = Card(
            text=request.form['text'].strip(),
            level=int(request.form['level']),
            orientation=request.form['orientation'],
            gender_combo=request.form['gender_combo'],
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


# === АДМИНКА: РЕДАКТИРОВАТЬ ===
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
            card.image_url = request.form.get('image_url') or None
            db.session.commit()
            flash('✅ Карточка обновлена', 'success')
            return redirect(url_for('main.admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Ошибка: {e}', 'error')
    return render_template('admin/edit_card.html', card=card)


# === АДМИНКА: УДАЛИТЬ ===
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


# === ИГРОВОЕ ПОЛЕ: ГЛАВНАЯ ===
@main.route('/')
def index():
    # Генерируем QR-код
    import qrcode
    from io import BytesIO
    import base64
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("Спасибо за игру в NightMonopoly! 💋")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    return render_template('index.html', qr_code=qr_code)


# === ПОКАЗАТЬ КАРТОЧКУ ===
@main.route('/card', methods=['POST'])
def show_card():
    card_id = request.form.get('card_id', type=int)
    if not card_id:
        return render_template('card.html', error="Введите номер карточки")
    card = Card.query.get(card_id)
    if not card:
        return render_template('card.html', error=f"Карточка №{card_id} не найдена")
    return render_template('card.html', card=card)