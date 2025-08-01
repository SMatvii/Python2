from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    category_display = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20), nullable=False, default='30 см')
    popular = db.Column(db.Boolean, default=False)
    available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Pizza {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'price': str(int(self.price)),
            'category': self.category,
            'category_display': self.category_display,
            'size': self.size,
            'popular': self.popular,
            'available': self.available,
            'image_url': self.image_url
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_address = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    delivery_type = db.Column(db.String(20), nullable=True, default='delivery')
    delivery_address = db.Column(db.Text, nullable=True)
    delivery_time = db.Column(db.String(10), nullable=True)
    payment_method = db.Column(db.String(20), nullable=True, default='cash')
    order_comment = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    pizza = db.relationship('Pizza', backref='order_items')

    def __repr__(self):
        return f'<OrderItem {self.pizza.name} x{self.quantity}>'

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.relationship('PollVote', backref='poll', lazy=True)

    def __repr__(self):
        return f'<Poll {self.title}>'

class PollVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'), nullable=False)
    voter_ip = db.Column(db.String(45), nullable=False)  # IPv4 або IPv6
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pizza = db.relationship('Pizza', backref='poll_votes')

    def __repr__(self):
        return f'<PollVote {self.pizza.name}>'
