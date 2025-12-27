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

    # Все карточки текущего уровня с учётом ориентации и пола
    all_available = Card.query.filter(
        Card.level == level,
        Card.card_type == 'game',
        Card.orientation.in_(allowed_orientations),
        Card.gender.in_(allowed_genders),
        Card.target.in_(['Партнёр', 'Любой', 'Партнёр на выбор'])
    ).all()

    # Если вообще нет карточек — невозможно играть
    if not all_available:
        if level < 4:
            session['level'] += 1
            flash(f'🎉 Уровень {session["level"]} открыт!', 'info')
            return redirect(url_for('main.game'))
        else:
            flash('🎉 Все уровни пройдены!', 'success')
            return redirect(url_for('main.players'))

    # Только неиспользованные (или повторяемые)
    used_ids = session.get('used_cards', [])
    available_now = [c for c in all_available if c.id not in used_ids or c.can_repeat]

    # 🔥 КЛЮЧЕВАЯ ЛОГИКА: если НЕТ доступных карточек — переходим на уровень
    if not available_now:
        if level < 4:
            session['level'] += 1
            flash(f'🎉 Уровень {session["level"]} открыт!', 'info')
            return redirect(url_for('main.game'))
        else:
            flash('🎉 Игра завершена! Все карточки пройдены.', 'success')
            return redirect(url_for('main.players'))

    # Выбираем случайную из доступных
    card = random.choice(available_now)

    # Если нельзя повторять — добавляем в использованные
    if not card.can_repeat:
        session['used_cards'].append(card.id)
        session.modified = True

    session['current_card_id'] = card.id

    # Проверка: нужно ли выбрать цель
    selected_target = session.get('selected_target')
    targetable_players = []

    if card.target == 'Партнёр на выбор' and not selected_target:
        for p in players:
            if p['name'] == player['name']:
                continue
            if player['orientation'] == 'Гетеро':
                if (player['gender'] == 'Парень' and p['gender'] == 'Девушка') or \
                   (player['gender'] == 'Девушка' and p['gender'] == 'Парень'):
                    targetable_players.append(p)
            elif player['orientation'] in ['Би', 'Другое', 'Любая']:
                targetable_players.append(p)
            elif player['orientation'] == 'Лесби' and p['gender'] == 'Девушка':
                targetable_players.append(p)

        return render_template('game.html', 
                             card=card, player=player, 
                             targetable_players=targetable_players,
                             next=next_player)

    return render_template('game.html', 
                         card=card, player=player, 
                         next=next_player, 
                         selected_target=selected_target)