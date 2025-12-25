# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card, PenaltyCard

main = Blueprint('main', __name__)

# Админка
@main.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    cards = Card.query.all()
    penalty_cards = PenaltyCard.query.all()
    return render_template('admin/index.html', cards=cards, penalty_cards=penalty_cards)

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'Vladimirovich' and password == 'Timur':
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin'))
        flash('Неверный логин или пароль')
    return render_template('admin/login.html')

@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin_login'))

# Добавить карточку
@main.route('/admin/add-card', methods=['POST'])
def add_card():
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
    flash('Карточка добавлена')
    return redirect(url_for('main.admin'))

# Редактировать карточку
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

# Удалить карточку
@main.route('/admin/delete-card/<int:id>', methods=['POST'])
def delete_card(id):
    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    flash('Карточка удалена')
    return redirect(url_for('main.admin'))

# Добавить штраф
@main.route('/admin/add-penalty', methods=['POST'])
def add_penalty():
    text = request.form['text']
    duration = int(request.form['duration'])
    penalty = PenaltyCard(text=text, duration=duration)
    db.session.add(penalty)
    db.session.commit()
    flash('Штраф добавлен')
    return redirect(url_for('main.admin'))

# Редактировать штраф
@main.route('/admin/edit-penalty/<int:id>', methods=['GET', 'POST'])
def edit_penalty(id):
    penalty = PenaltyCard.query.get_or_404(id)
    if request.method == 'POST':
        penalty.text = request.form['text']
        penalty.duration = int(request.form['duration'])
        db.session.commit()
        flash('Штраф обновлён')
        return redirect(url_for('main.admin'))
    return render_template('admin/edit_penalty.html', penalty=penalty)

# Удалить штраф
@main.route('/admin/delete-penalty/<int:id>', methods=['POST'])
def delete_penalty(id):
    penalty = PenaltyCard.query.get_or_404(id)
    db.session.delete(penalty)
    db.session.commit()
    flash('Штраф удалён')
    return redirect(url_for('main.admin'))