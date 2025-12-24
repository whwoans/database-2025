from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(30), unique=True, nullable=False)
    passwd = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    favorites = db.relationship('FavoriteStore', backref='user', lazy=True)
    
    def set_password(self, password):
        self.passwd = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.passwd, password)

class Owner(db.Model):
    __tablename__ = 'owner'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.String(30), unique=True, nullable=False)
    owner_passwd = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    
    # Relationships
    stores = db.relationship('Store', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.owner_passwd = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.owner_passwd, password)

class Rider(db.Model):
    __tablename__ = 'rider'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rider_id = db.Column(db.String(30), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    vehicle = db.Column(db.String(30), nullable=False)
    
    # Relationships
    orders = db.relationship('Order', backref='rider', lazy=True)

class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(30), nullable=False)
    
    # Relationships
    stores = db.relationship('Store', backref='category_rel', lazy=True)

class Store(db.Model):
    __tablename__ = 'store'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=True)
    store_name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    minprice = db.Column(db.String(30), nullable=False)
    reviewCount = db.Column(db.Integer, default=0, nullable=False)
    operationTime = db.Column(db.String(250), nullable=False)
    closedDay = db.Column(db.String(250), nullable=False)
    information = db.Column(db.String(500), nullable=True)  # 가게 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    menus = db.relationship('Menu', backref='store', lazy=True)
    orders = db.relationship('Order', backref='store', lazy=True)
    coupons = db.relationship('Coupon', backref='store', lazy=True)
    favorites = db.relationship('FavoriteStore', backref='store', lazy=True)
    reviews = db.relationship('Review', backref='store', lazy=True)
    payment = db.relationship('Payment', backref='stores', lazy=True)  # 기존 단일 payment_id용 (하위 호환)

class Menu(db.Model):
    __tablename__ = 'menu'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    menu = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

class Order(db.Model):
    __tablename__ = 'order'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('rider.id'), nullable=True)
    order = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Review(db.Model):
    __tablename__ = 'review'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)  # 주문 ID 추가
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

class FavoriteStore(db.Model):
    __tablename__ = 'favorite_store'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

class Payment(db.Model):
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment = db.Column(db.String(30), nullable=False)

class Coupon(db.Model):
    __tablename__ = 'coupon'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    period = db.Column(db.Integer, nullable=True)  # 유효기간 (일 단위)
    discount = db.Column(db.Integer, nullable=True)  # 할인 금액 또는 할인율
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

class StorePayment(db.Model):
    __tablename__ = 'store_payment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    store = db.relationship('Store', backref='store_payments', lazy=True)
    payment = db.relationship('Payment', backref='store_payments', lazy=True)

