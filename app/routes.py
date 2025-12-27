# В add_card и edit_card:
card = Card(
    text=request.form['text'],
    level=int(request.form['level']),
    orientation=request.form['orientation'],
    gender_combo=request.form['gender_combo'],
    target=request.form['target'],
    image_url=request.form.get('image_url') or None
)