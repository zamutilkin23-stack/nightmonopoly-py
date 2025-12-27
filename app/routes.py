# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card
import random

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/players')
def players():
    return render_template('players.html')


@main.route('/setup')
def setup():
    count = int(request.args.get('count', 2))
    return render_template('setup.html', count=count)


@main.route('/start', methods=['POST'])
def start():
    players = []
    for i in range(1, 5):
        name = request.form.get(f'name{i}')
        if name:
            gender = request.form.get(f'gender{i}')
            orientation = request.form.get(f'orientation{i}')
            players.append({
                'name': name,
                'gender': gender,
                'orientation': orientation
            })

    if len(players) < 2:
        flash('Нужно минимум 2 игрока', 'error')
        return redirect(url_for('main.players'))

    session['players'] = players
    session['current'] = 0
    session['level'] = 1
    session['used_cards'] = []
    return redirect(url_for('main.game'))


@main.route('/game')
def game():
    if 'players' not in session:
        return redirect(url_for('main.players'))

    players = session['players']
    current = session['current']
    player = players[current]
    next_player = players[(current + 1) % len(players)]
    level = session['level']

    # Фильтр по ориентации
    allowed_orientations = ['Любая']
    if player['orientation'] == 'Би':
        allowed_orientations += ['Гетеро', 'Лесби', 'Другое']
    else:
        allowed_orientations.append(player['orientation'])

    # Фильтр по полу
    allowed_genders = [player['gender'], 'Любой']

    # Все карточки текущего уровня
    all_available = Card.query.filter(
        Card.level == level,
        Card.card_type == 'game',
        Card.orientation.in_(allowed_orientations),
        Card.gender.in_(allowed_genders),
        Card.target.in_(['Партнёр', 'Любой', 'Партнёр на выбор'])
    ).all()

    if not all_available:
        if level < 4:
            session['level'] += 1
            flash(f'🎉 Уровень {session["level"]} открыт!', 'info')
            return redirect(url_for('main.game'))
        else:
            flash('🎉 Все уровни пройдены!', 'success')
            return redirect(url_for('main.players'))

    # Только доступные
    used_ids = session.get('used_cards', [])
    available_now = [c for c in all_available if c.id not in used_ids or c.can_repeat]

    if not available_now:
        if level < 4:
            session['level'] += 1
            flash(f'🎉 Уровень {session["level"]} открыт!', 'info')
            return redirect(url_for('main.game'))
        else:
            flash('🎉 Игра завершена!', 'success')
            return redirect(url_for('main.players'))

    card = random.choice(available_now)

    if not card.can_repeat:
        session['used_cards'].append(card.id)
        session.modified = True

    session['current_card_id'] = card.id

    # Автоматический выбор цели
    selected_target = None
    if card.target == 'Партнёр на выбор':
        candidates = [p for p in players if p['name'] != player['name']]
        if candidates:
            filtered = []
            for p in candidates:
                if player['orientation'] == 'Гетеро':
                    if (player['gender'] == 'Парень' and p['gender'] == 'Девушка') or \
                       (player['gender'] == 'Девушка' and p['gender'] == 'Парень'):
                        filtered.append(p)
                elif player['orientation'] in ['Би', 'Другое', 'Любая']:
                    filtered.append(p)
                elif player['orientation'] == 'Лесби' and p['gender'] == 'Девушка':
                    filtered.append(p)

            if filtered:
                chosen = random.choice(filtered)
                selected_target = chosen['name']
            else:
                chosen = random.choice(candidates)
                selected_target = chosen['name']

        session['selected_target'] = selected_target

    return render_template('game.html', 
                         card=card, 
                         player=player, 
                         next=next_player, 
                         selected_target=selected_target)


@main.route('/next')
def next_player():
    if 'players' in session:
        session['current'] = (session['current'] + 1) % len(session['players'])
        session.pop('selected_target', None)
        session.pop('current_card_id', None)
    return redirect(url_for('main.game'))


@main.route('/penalty')
def penalty():
    if 'players' not in session:
        return redirect(url_for('main.players'))

    players = session['players']
    current = session['current']
    player = players[current]
    next_player = players[(current + 1) % len(players)]

    card = Card.query.filter_by(card_type='penalty').order_by(db.func.random()).first()
    if not card:
        card = Card(
            text="Ты не справился — поцелуй в шею",
            level=2,
            card_type='penalty',
            orientation='Любая',
            gender='Любой',
            target='Любой',
            can_repeat=True
        )

    return render_template('penalty.html', card=card, player=player, next=next_player)


@main.route('/admin-secret')
def admin_secret():
    return redirect(url_for('main.admin_login', next=url_for('main.admin')))


@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next') or url_for('main.index')
    
    # 🔐 Флаг: если уже вошёл — не пускаем снова
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 🔑 Логин/пароль
        if username == 'Vladimirovich' and password == 'Timur':
            session['admin_logged_in'] = True
            session.permanent = True  # ← Чтобы сессия не терялась
            flash('✅ Добро пожаловать!', 'success')
            return redirect(next_page)
        else:
            flash('❌ Неверный логин или пароль', 'error')
    
    return render_template('admin/login.html', next=next_page)


@main.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        flash('🔐 Войдите в админку', 'error')
        return redirect(url_for('main.admin_login'))
    game_cards = Card.query.filter_by(card_type='game').all()
    penalty_cards = Card.query.filter_by(card_type='penalty').all()
    return render_template('admin/index.html', game_cards=game_cards, penalty_cards=penalty_cards)


@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы вышли из админки', 'info')
    return redirect(url_for('main.index'))


@main.route('/admin/add-card', methods=['POST'])
def add_card():
    if not session.get('admin_logged_in'):
        flash('❌ Доступ запрещён', 'error')
        return redirect(url_for('main.admin_login'))
    
    try:
        card = Card(
            text=request.form['text'].strip(),
            level=int(request.form['level']),
            card_type=request.form['card_type'],
            orientation=request.form['orientation'],
            gender=request.form['gender'],
            target=request.form['target'],
            image_url=request.form.get('image_url'),
            can_repeat='can_repeat' in request.form
        )
        db.session.add(card)
        db.session.commit()
        flash('✅ Карточка добавлена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Ошибка: {str(e)}', 'error')
    return redirect(url_for('main.admin'))


@main.route('/admin/edit-card/<int:id>', methods=['GET', 'POST'])
def edit_card(id):
    if not session.get('admin_logged_in'):
        flash('❌ Доступ запрещён', 'error')
        return redirect(url_for('main.admin_login'))
    
    card = Card.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            card.text = request.form['text'].strip()
            card.level = int(request.form['level'])
            card.card_type = request.form['card_type']
            card.orientation = request.form['orientation']
            card.gender = request.form['gender']
            card.target = request.form['target']
            card.image_url = request.form.get('image_url')
            card.can_repeat = 'can_repeat' in request.form
            db.session.commit()
            flash('✅ Обновлено', 'success')
            return redirect(url_for('main.admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Ошибка: {str(e)}', 'error')
    
    return render_template('admin/edit_card.html', card=card)


@main.route('/admin/delete-card/<int:id>', methods=['POST'])
def delete_card(id):
    if not session.get('admin_logged_in'):
        flash('❌ Доступ запрещён', 'error')
        return redirect(url_for('main.admin_login'))
    
    try:
        card = Card.query.get_or_404(id)
        db.session.delete(card)
        db.session.commit()
        flash('🗑️ Удалено', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Ошибка: {str(e)}', 'error')
    return redirect(url_for('main.admin'))