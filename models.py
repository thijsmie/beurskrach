from extensions import db


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    username = db.Column(db.String(80), unique=True)
    points = db.Column(db.Integer)
        
        
class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    name = db.Column(db.String(80))
    colour = db.Column(db.Integer)
    
    # Public market variables
    current_value = db.Column(db.Integer)
    in_circulation = db.Column(db.Integer)
    total_sold = db.Column(db.Integer)
    
    # Private market variables
    market_value = db.Column(db.Integer)
    crash_potential = db.Column(db.Float)
    global_trend = db.Column(db.Float)
    trend_wiggle = db.Column(db.Float)
    
    next_timestep = db.Column(db.Integer)
    
    sell_amount = db.Column(db.Integer)
    buy_amount = db.Column(db.Integer)
    
    
class PriceHistory(db.Model):
    __tablename__ = 'history'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    
    product = db.relationship('Product', backref='history')
    product_id = db.Column(db.ForeignKey('product.id'))    
    
    timestep = db.Column(db.Integer)
    value = db.Column(db.Integer)
    in_circulation = db.Column(db.Integer)
    total_sold = db.Column(db.Integer)

