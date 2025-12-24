# init_db.py
from app import create_app
from app.models import db, Card, PenaltyCard

app = create_app()

with app.app_context():
    # Удаляем старые таблицы
    db.drop_all()
    db.create_all()
    print("✅ Таблицы пересозданы")

    # Пример карточек (уровни 1-4)
    cards = [
        Card(text="Расскажи комплимент соседу", level=1, orientation="любая", gender_combo="any", target="neighbor"),
        Card(text="Поцелуй в шею справа", level=3, orientation="любая", gender_combo="any", target="neighbor"),
        Card(text="Имитация поцелуя с игроком того же пола", level=4, orientation="Би,Гей,Лесби", gender_combo="ММ,ЖЖ", target="neighbor"),
        Card(text="Сделай 10 отжиманий", level=1, orientation="любая", gender_combo="any", target="self"),
        Card(text="Пробеги вокруг стола", level=2, orientation="любая", gender_combo="any", target="self"),
        Card(text="Сними одну вещь", level=3, orientation="любая", gender_combo="any", target="self"),
    ]

    for card in cards:
        db.session.add(card)

    # Штрафы
    penalties = [
        PenaltyCard(text="Сделай 10 отжиманий", duration=60),
        PenaltyCard(text="Пробеги вокруг стола", duration=30),
        PenaltyCard(text="Постой на одной ноге 1 минуту", duration=60),
    ]

    for penalty in penalties:
        db.session.add(penalty)

    db.session.commit()
    print("✅ Данные добавлены: карточек —", len(cards), ", штрафов —", len(penalties))