from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
import random
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Замените на свой секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://DESKTOP-19QLP36\MSSQLSERVERRR/DIPLOM?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tovar(db.Model):
    __tablename__ = 'Tovar'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), unique=True)  # Уникальный идентификатор
    Название = db.Column(db.String(255))
    Описание = db.Column(db.Text)
    Цена = db.Column(db.Float)
    image = db.Column(db.String(255))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unique_id = str(uuid.uuid4())  # Генерация уникального идентификатора

@app.route('/')
def home():
    товары = Tovar.query.all()  # Получаем все товары из базы данных

    if not товары:
        return render_template('index.html', товар=None)

    # Получаем список уже показанных товаров из сессии
    shown_ids = session.get('shown_ids', [])

    # Находим доступные товары
    available_tovars = [t for t in товары if t.id not in shown_ids]

    if not available_tovars:
        # Если все товары были показаны, сбрасываем список
        shown_ids = []
        available_tovars = товары

    # Выбираем случайный товар
    случайный_товар = random.choice(available_tovars)

    # Добавляем ID выбранного товара в список показанных
    shown_ids.append(случайный_товар.id)
    session['shown_ids'] = shown_ids

    return render_template('index.html', товар=случайный_товар)

if __name__ == '__main__':
    app.run(debug=True)