# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .extensions import db
from .models import Card
import random

main = Blueprint('main', __name__)


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

    # Карточки текущего уровня
    available_cards = Card.query.filter(
        Card.level == level,
        Card.card_type == 'game',
        Card.orientation.in_(allowed_orientations),
        Card.gender.in_(allowed_genders),
        Card.target.in_(['Партнёр', 'Любой', 'Партнёр на выбор'])
    ).all()

    if not available_cards:
        if level < 4:
            session['level'] += 1
            flash(f'🎉 Уровень {session["level"]} открыт!', 'info')
            return redirect(url_for('main.game'))
        else:
            flash('🎉 Все уровни пройдены!', 'success')
            return redirect(url_for('main.players'))

    # Неиспользованные
    used_ids = session.get('used_cards', [])
    unused = [c for c in available_cards if c.id not in used_ids or c.can_repeat]
    if not unused:
        if level < 4:
            session['level'] += 1
            flash(f'🎉 Уровень {session["level"]} открыт!', 'info')
            return redirect(url_for('main.game'))
        else:
            flash('🎉 Игра завершена!', 'success')
            return redirect(url_for('main.players'))

    card = random.choice(unused)
    session['current_card_id'] = card.id

    # Определяем, кого можно выбрать
    targetable_players = []
    if card.target == 'Партнёр на выбор':
        for p in players:
            if p['name'] == player['name']:
                continue  # нельзя самому себе
            if player['orientation'] == 'Гетеро':
                if (player['gender'] == 'Парень' and p['gender'] == 'Девушка') or \
                   (player['gender'] == 'Девушка' and p['gender'] == 'Парень'):
                    targetable_players.append(p)
            elif player['orientation'] in ['Би', 'Другое', 'Любая']:
                targetable_players.append(p)
            # Лесби — отдельно
            elif player['orientation'] == 'Лесби' and player['gender'] == 'Девушка' and p['gender'] == 'Девушка':
                targetable_players.append(p)

    selected_target = session.get('selected_target')

    if card.target == 'Партнёр на выбор' and not selected_target:
        return render_template('game.html', 
                             card=card, player=player, 
                             targetable_players=targetable_players,
                             next=next_player)

    return render_template('game.html', 
                         card=card, player=player, 
                         next=next_player, 
                         selected_target=selected_target)


@main.route('/select-target', methods=['POST'])
def select_target():
    target_name = request.form.get('target_player')
    if target_name:
        session['selected_target'] = target_name
    return redirect(url_for('main.game'))


@main.route('/next')
def next_player():
    if 'players' in session:
        session['current'] = (session['current'] + 1) % len(session['players'])
        session.pop('selected_target', None)
        session.pop('current_card_id', None)
    return redirect(url_for('main.game'))