from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
import random
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://DESKTOP-19QLP36\MSSQLSERVERRR/DIPLOM?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tovar(db.Model):
    __tablename__ = 'Tovar'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), unique=True)  
    Название = db.Column(db.String(255))
    Описание = db.Column(db.Text)
    Цена = db.Column(db.Float)
    image = db.Column(db.String(255))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unique_id = str(uuid.uuid4()) 

@app.route('/')
def home():
    товары = Tovar.query.all()  

    if not товары:
        return render_template('index.html', товар=None)

    shown_ids = session.get('shown_ids', [])

    available_tovars = [t for t in товары if t.id not in shown_ids]

    if not available_tovars:
        shown_ids = []
        available_tovars = товары

    случайный_товар = random.choice(available_tovars)

    shown_ids.append(случайный_товар.id)
    session['shown_ids'] = shown_ids

    return render_template('index.html', товар=случайный_товар)

if __name__ == '__main__':
    app.run(debug=True)
