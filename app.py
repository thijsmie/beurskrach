from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from paths import TEMPLATE_FOLDER, STATIC_FOLDER


app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)



Bootstrap(app)

auth = LoginManager(app)
auth.login_view = "login"
auth.session_protection = "strong"

auth_hasher = Bcrypt(app)


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    username = db.Column(db.String(80), unique=True)
    passhash = db.Column(db.String(256))
    points = db.Column(db.Integer)
    
    def __init__(self):
        self.points = 0
        
        
class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    name = db.Column(db.String(80))
    colour = db.Column(db.Integer)
    
    # Public market variables
    current_value = db.Column(db.Integer)
    in_circulation = db.Column(db.Integer)
    
    # Private market variables
    market_value = db.Column(db.Integer)
    crash_potential = db.Column(db.Float)
    global_trend = db.Column(db.Float)
    trend_wiggle = db.Column(db.Float)
    
    next_timestep = db.Column(db.Integer)
    
    
class BuyOrder(db.Model):
    __tablename__ = 'buyorder'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    user = db.relationship('User', backref='buyorders')
    user_id = db.Column(db.ForeignKey('user.id'))
    
    product = db.relationship('Product', backref='buyorders')
    product_id = db.Column(db.ForeignKey('product.id'))
    
    amount = db.Column(db.Integer)
    unit_price = db.Column(db.Integer)
    
    submitted_timestep = db.Column(db.Integer)
    processed_timestep = db.Column(db.Integer)
    
    
    
class SellOrder(db.Model):
    __tablename__ = 'sellorder'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    user = db.relationship('User', backref='sellorders')
    user_id = db.Column(db.ForeignKey('user.id'))
    
    product = db.relationship('Product', backref='sellorders')
    product_id = db.Column(db.ForeignKey('product.id'))
    
    amount = db.Column(db.Integer)
    unit_price = db.Column(db.Integer)
    
    submitted_timestep = db.Column(db.Integer)
    processed_timestep = db.Column(db.Integer)
    
    
class Ownership(db.Model):
    __tablename__ = 'ownership'  
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    user = db.relationship('User', backref='owned')
    user_id = db.Column(db.ForeignKey('user.id'))
    
    product = db.relationship('Product', backref='owned')
    product_id = db.Column(db.ForeignKey('product.id'))
    
    amount = db.Column(db.Integer)
    
    
class PriceHistory(db.Model):
    __tablename__ = 'history'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    product = db.relationship('Product', backref='history')
    product_id = db.Column(db.ForeignKey('product.id'))    
    
    timestep = db.Column(db.Integer)
    value = db.Column(db.Integer)
    
    
db.create_all()
db.session.commit()
    

def do_timestep():
    # Prevent raceconditions, if we're doing a timestep lock all relevant tables
    db.session.execute("LOCK TABLES product, buyorder, sellorder, ownership WRITE") 
    
    process_sellorders()
    process_buyorders()
    update_product_prices()
    process_sellorders()
    process_buyorders()
    
    # Release locked tables
    db.session.commit()
    db.session.execute("UNLOCK TABLES") 
    
    
def update_product_prices():
    products = Product.query.all()
    
    for product in products:
        product_history = PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.timestep.desc())
        
        new_history_point = PriceHistory()
        new_history_point.product = product
        new_history_point.timestep = product.next_timestep
        new_history_point.value = product.current_value
        
        product.next_timestep += 1
        
        if random.random() < product.crash_potential:
            new_price = do_product_crash(product)
        else:
            new_price = int(product_history[0] +
                            (product.market_value - product.current_value) * abs(random.gauss(0, 1)) +
                            product.global_trend * random.random() +
                            (product.history[0] - product.history[1]) / 2.
                                * random.random())
                                
            new_price = max(1, new_price)                   
            update_product_potentials(product, product_history)  
                              
        
        product.current_value = new_price
        db.session.add(new_history_point)
        
        
def do_product_crash(product):
    if product.current_value > product.market_value:
        # Bubble crash
        product.current_value = max(1, 2*product.market_value - product.current_value)
        product.trend_wiggle *= 2.
        product.global_trend = -product.current_value / 4. + random.gauss(10, 10)
        product.crash_potential = 0.001
    else:
        # Trust crash
        product.current_value = int(random.gauss(product.current_value / 2., product.current_value / 4.))
        product.trend_wiggle *= 3.
        product.global_trend = random.gauss(5, 10)
        product.crash_potential = 0.002
    return product.current_value
        
        
def update_product_potentials(product, product_history):
    product.global_trend = product.global_trend*(1-product.trend_wiggle) + (product_history[1] - product_history[0])*product.trend_wiggle
    product.trend_wiggle *= abs(random.gauss(1, 0.3)) 
    product.crash_potential += product.trend_wiggle * 0.01
    
    
def place_sellorder(product_id, amount, unit_price):
    inventory = current_user.owned
    for item in inventory:
        if item.product.id == product.id:
            if item.amount < amount:
                return False
                
            item.amount -= amount
            order = SellOrder()
            order.amount = amount
            order.product = item.product
            order.unit_price = unit_price
            order.submitted_timestep = item.product.current_timestep
            db.session.add(order)
            return True
    return False
    
    
def place_buyorder(product_id, amount, unit_price):
    if current_user.points < amount * unit_price:
        return False
        
    current_user.points -= amount * unit_price
    
    order = BuyOrder()
    order.amount = amount
    
    order.product = Product.query.get(product_id)
    if order.product is None:
        return False
        
    order.unit_price = unit_price
    order.submitted_timestep = order.product.current_timestep
    db.session.add(order)
    return True
    
    
def process_sellorders():
    orders = SellOrder.query.filter_by(processed_timestep=None).all()
    for order in orders:
        if order.unit_price <= order.product.current_value:
            # FULFILLED
            order.processed_timestep = order.product.current_timestep
            order.user.points += order.amount * order.unit_price
            order.product.in_circulation += order.amount
      
            
def process_buyorders():
    orders = BuyOrder.query.filter_by(processed_timestep=None).order_by(BuyOrder.submitted_timestep.asc(), BuyOrder.amount.desc()).all()
    for order in orders:
        if order.unit_price >= order.product.current_value and order.product.in_circulation >= order.amount:
            # FULFILLED
            order.processed_timestep = order.product.current_timestep
            user_add_inventory(order.user, order.product, order.amount)
            order.product.in_circulation -= order.amount
                    
            
def user_add_inventory(user, product, amount):
    for item in user.owned:
        if item.product_id == product.id:
            item.amount += amount
            return
    item = Ownership()
    item.product = product
    item.user = user
    item.amount = amount         
    


@app.route('/')
def index():
    return render_template('index.html')
 
   
@app.route('/login')
def login():
    if do_login(request.form.get('username'), request.form.get('password')):
        return redirect(url_for('index'))
    return render_template('do_login.html')

@app.route('/logout')
@login_required
def logout():
    do_logout()
    return redirect(url_for('index'))
    
   
@app.route('/place/buyorder')
@login_required
def do_place_buyorder():
    if place_buyorder(request.form):
        return render_template('success.html', message="Successfully placed buyorder")
    return redirect(url_for('index'))
    
    
@app.route('/place/sellorder')
@login_required
def do_place_sellorder():
    if place_sellorder(request.form):
        return render_template('success.html', message="Successfully placed sellorder")
    return redirect(url_for('index')) 
 
    
# Random session key generation, inspired by django.utils.crypto.get_random_string
import random

try:
    random = random.SystemRandom()
except NotImplementedError:
    LOG.critical("Insecure random! Please make random.SystemRandom available!")


# noinspection PyUnusedLocal
def generate_random_string(length):
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(length)])


@auth.user_loader
def load_user(session_token):
    return User.query.filter_by(token=session_token).first()


def do_login(username, password):
    user = User.query.filter_by(username=username).first()

    if user is None:
        return False

    if not auth_hasher.check_password_hash(user.passhash, password):
        return False

    user.token = generate_random_string(64)

    # DB session committing can introduce weird stuff if do_login is ever called in the middle of something.
    # So don't do that...
    db.session.commit()

    login_user(user)
    return True


def do_logout():
    logout_user()


def new_user(username, password, email):
    user = User()
    user.username = username
    user.passhash = auth_hasher.generate_password_hash(password)
    user.email = email

    return user
    
    
if __name__ == "__main__":
    app.run(debug=True)
