from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
import random
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

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
    Название = db.Column(db.String(255))
    Описание = db.Column(db.Text)
    Цена = db.Column(db.Float)
    image = db.Column(db.String(255))
    Категория = db.Column(db.String(50))

class Klient(db.Model):
    __tablename__ = 'klient'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255, collation='utf8_general_ci'), nullable=False)
    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        print(f"Введенный пароль: {password}")
        print(f"Хэш пароля из базы данных: {self.password_hash}")
        return check_password_hash(self.password_hash, password)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    klient_id = db.Column(db.Integer, db.ForeignKey('klient.id'), nullable=False)
    tovar_id = db.Column(db.Integer, db.ForeignKey('Tovar.id'), nullable=False)

    klient = db.relationship('Klient', backref='cart_items')
    tovar = db.relationship('Tovar', backref='cart_items')

@app.route('/')
def home():
    товары = Tovar.query.all()
    num_to_display = len(товары)

    if not товары:
        return render_template('index.html', товары=[])

    random_товары = random.sample(товары, min(num_to_display, len(товары)))

    return render_template('index.html', товары=random_товары)


@app.route('/add_to_cart/<int:tovar_id>', methods=['POST'])
def add_to_cart(tovar_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу логина

    user_id = session['user_id']

    # Проверяем, существует ли товар
    tovar = Tovar.query.get(tovar_id)
    if not tovar:
        flash("Товар не найден.")
        return redirect(url_for('home', tovar_id=tovar_id))

    # Проверяем, существует ли запись в корзине
    existing_cart_item = Cart.query.filter_by(klient_id=user_id, tovar_id=tovar_id).first()
    if existing_cart_item:
        flash("Товар уже в корзине.")
        return redirect(url_for("home", tovar_id=tovar_id))

    # Добавляем товар в корзину
    new_cart_item = Cart(klient_id=user_id, tovar_id=tovar_id)
    db.session.add(new_cart_item)
    db.session.commit()

    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:tovar_id>', methods=['POST'])
def remove_from_cart(tovar_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу логина

    user_id = session['user_id']
    cart_item = Cart.query.filter_by(klient_id=user_id, tovar_id=tovar_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()  # Сохраняем изменения в базе данных
        flash('Товар был удален из корзины.')
    else:
        flash('Товар не найден в корзине.')

    return redirect(url_for('cart'))  #

@app.route('/cart', methods = ['GET'])
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу логина

    user_id = session['user_id']
    cart_items = Cart.query.filter_by(klient_id=user_id).all()

    # Получаем список товаров в корзине
    products_in_cart = []
    for item in cart_items:
        product = Tovar.query.get(item.tovar_id)
        products_in_cart.append(product)

    return render_template('cart.html', товары=products_in_cart)

@app.route('/product/<int:tovar_id>')
def product(tovar_id):
    товар = Tovar.query.get_or_404(tovar_id)  # Получаем товар по ID или возвращаем 404
    return render_template('product.html', товар=товар)

@app.route('/buy/<int:tovar_id>', methods=['GET'])
def buy(tovar_id):
    товар = Tovar.query.get_or_404(tovar_id)  # Получаем товар по ID или возвращаем 404
    return render_template('buy.html', товар=товар)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = Klient.query.filter_by(login=login).first()

        if user:
            if user.password_hash is None:
                print("Error: password_hash is None for user:", user.login)
                error = "Ошибка: Неправильная конфигурация пользователя"
                return render_template('login.html', error=error)

            if user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.login
                return redirect(url_for('home'))
            else:
                error = 'Неверный пароль'
                return render_template('login.html', error=error)
        else:
            error = 'Пользователь не найден'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        existing_user = Klient.query.filter_by(login=login).first()
        if existing_user:
            error = 'Пользователь с таким логином уже существует'
            return render_template('register.html', error=error)

        # Создаем нового пользователя
        new_user = Klient(login=login)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            db.session.rollback()
            error = 'Произошла ошибка при создании пользователя'
            return render_template('register.html', error=error)

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/filter-products', methods=['POST'])
def filter_products():
    price_from = request.form.get('price_from', type=float)
    price_to = request.form.get('price_to', type=float)
    category = request.form.get('category', '')
    template_name = request.form.get('template_name', 'index.html')  # Имя шаблона

    # Если цена не указана, устанавливаем ее на минимально возможное значение (0) или максимально возможное значение (10000)
    if price_from is None:
        price_from = 0
    if price_to is None:
        price_to = 100000

    # Фильтруем товары по заданным критериям
    filtered_products = Tovar.query.filter(
        Tovar.Цена >= price_from,
        Tovar.Цена <= price_to
    )

    # Если выбрана категория, фильтруем по ней
    if category:
        filtered_products = filtered_products.filter(Tovar.Категория == category)

    # Получаем отфильтрованные товары
    filtered_products = filtered_products.all()

    return render_template(template_name, товары=filtered_products)


@app.route('/katalog')
def katalog():
    товары = Tovar.query.all()
    num_to_display = len(товары)

    if not товары:
        return render_template('katalog.html', товары=[])

    random_товары = random.sample(товары, min(num_to_display, len(товары)))

    return render_template('katalog.html', товары=random_товары)



if __name__ == '__main__':
    app.run(debug=True)