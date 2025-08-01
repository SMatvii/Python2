from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from models import db, Pizza, Order, OrderItem, Poll, PollVote
from weather_service import WeatherService, get_weather_icon_emoji

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///oderman.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

weather_service = WeatherService(
    api_key=os.getenv('OPENWEATHER_API_KEY', 'demo-key'),
    city=os.getenv('PIZZERIA_CITY', 'Kyiv'),
    country=os.getenv('PIZZERIA_COUNTRY', 'UA')
)

@app.route('/')
def index():
    weather_data = weather_service.get_current_weather()
    pizza_recommendation = weather_service.get_pizza_recommendation(weather_data)
    
    if weather_data.get('success') and weather_data.get('icon'):
        weather_data['emoji'] = get_weather_icon_emoji(weather_data['icon'])
    
    return render_template('index.html', 
                         weather=weather_data, 
                         recommendation=pizza_recommendation)

@app.route('/menu')
def menu():
    pizzas = Pizza.query.filter_by(available=True).all()
    pizzas_dict = [pizza.to_dict() for pizza in pizzas]
    return render_template('menu.html', pizzas=pizzas_dict)

@app.route('/menu/cards')
def menu_cards():
    pizzas = Pizza.query.filter_by(available=True).all()
    pizzas_dict = [pizza.to_dict() for pizza in pizzas]
    return render_template('menu_cards.html', pizzas=pizzas_dict)

@app.route('/api/pizzas')
def api_pizzas():
    pizzas = Pizza.query.filter_by(available=True).all()
    pizzas_dict = [pizza.to_dict() for pizza in pizzas]
    return jsonify(pizzas_dict)

@app.route('/order')
def order_form():
    return render_template('order.html')

@app.route('/admin')
def admin_dashboard():
    total_pizzas = Pizza.query.count()
    available_pizzas = Pizza.query.filter_by(available=True).count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    stats = {
        'total_pizzas': total_pizzas,
        'available_pizzas': available_pizzas,
        'total_orders': total_orders,
        'pending_orders': pending_orders
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/pizzas')
def admin_pizzas():
    pizzas = Pizza.query.all()
    return render_template('admin/pizzas.html', pizzas=pizzas)

@app.route('/admin/pizzas/add', methods=['GET', 'POST'])
def admin_add_pizza():
    if request.method == 'POST':
        try:
            pizza = Pizza(
                name=request.form['name'],
                ingredients=request.form['ingredients'],
                price=float(request.form['price']),
                category=request.form['category'],
                category_display=request.form['category_display'],
                size=request.form['size'],
                popular=bool(request.form.get('popular')),
                image_url=request.form.get('image_url')
            )
            
            db.session.add(pizza)
            db.session.commit()
            
            flash(f'Піца "{pizza.name}" успішно додана!', 'success')
            return redirect(url_for('admin_pizzas'))
            
        except Exception as e:
            flash(f'Помилка при додаванні піци: {str(e)}', 'error')
    
    return render_template('admin/add_pizza.html')

@app.route('/admin/pizzas/edit/<int:pizza_id>', methods=['GET', 'POST'])
def admin_edit_pizza(pizza_id):
    pizza = Pizza.query.get_or_404(pizza_id)
    
    if request.method == 'POST':
        try:
            pizza.name = request.form['name']
            pizza.ingredients = request.form['ingredients']
            pizza.price = float(request.form['price'])
            pizza.category = request.form['category']
            pizza.category_display = request.form['category_display']
            pizza.size = request.form['size']
            pizza.popular = bool(request.form.get('popular'))
            pizza.available = bool(request.form.get('available'))
            pizza.image_url = request.form.get('image_url')
            
            db.session.commit()
            
            flash(f'Піца "{pizza.name}" успішно оновлена!', 'success')
            return redirect(url_for('admin_pizzas'))
            
        except Exception as e:
            flash(f'Помилка при оновленні піци: {str(e)}', 'error')
    
    return render_template('admin/edit_pizza.html', pizza=pizza)

@app.route('/admin/pizzas/delete/<int:pizza_id>', methods=['POST'])
def admin_delete_pizza(pizza_id):
    try:
        pizza = Pizza.query.get_or_404(pizza_id)
        pizza_name = pizza.name
        
        db.session.delete(pizza)
        db.session.commit()
        
        flash(f'Піца "{pizza_name}" успішно видалена!', 'success')
    except Exception as e:
        flash(f'Помилка при видаленні піци: {str(e)}', 'error')
    
    return redirect(url_for('admin_pizzas'))


@app.route('/poll')
def poll_page():
    poll = Poll.query.filter_by(active=True).first()
    if not poll:
        flash('Наразі немає активних опитувань', 'info')
        return redirect(url_for('index'))
    
    pizzas = Pizza.query.filter_by(available=True).all()
    return render_template('poll.html', poll=poll, pizzas=pizzas)

@app.route('/poll/vote', methods=['POST'])
def poll_vote():
    try:
        poll_id = request.form.get('poll_id')
        pizza_id = request.form.get('pizza_id')
        voter_ip = request.remote_addr
        
        existing_vote = PollVote.query.filter_by(
            poll_id=poll_id, 
            voter_ip=voter_ip
        ).first()
        
        if existing_vote:
            flash('Ви вже голосували в цьому опитуванні!', 'warning')
            return redirect(url_for('poll_page'))
        
        vote = PollVote(
            poll_id=poll_id,
            pizza_id=pizza_id,
            voter_ip=voter_ip
        )
        
        db.session.add(vote)
        db.session.commit()
        
        flash('Дякуємо за участь в опитуванні!', 'success')
        return redirect(url_for('poll_results'))
        
    except Exception as e:
        flash(f'Помилка при голосуванні: {str(e)}', 'error')
        return redirect(url_for('poll_page'))

@app.route('/poll/results')
def poll_results():
    poll = Poll.query.filter_by(active=True).first()
    if not poll:
        flash('Немає активних опитувань для відображення результатів', 'info')
        return redirect(url_for('index'))
    
    from sqlalchemy import func
    vote_results = db.session.query(
        Pizza,
        func.count(PollVote.id).label('votes')
    ).outerjoin(
        PollVote, (Pizza.id == PollVote.pizza_id) & (PollVote.poll_id == poll.id)
    ).filter(
        Pizza.available == True
    ).group_by(
        Pizza.id
    ).order_by(
        func.count(PollVote.id).desc()
    ).all()
    
    total_votes = sum([result.votes for result in vote_results])
    
    results = []
    winner = None
    
    for pizza, votes in vote_results:
        percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        result = {
            'pizza': pizza,
            'votes': votes,
            'percentage': percentage
        }
        results.append(result)
        
        if not winner and votes > 0:
            winner = pizza
    
    return render_template('poll_results.html', 
                         poll=poll, 
                         results=results, 
                         total_votes=total_votes,
                         winner=winner)

@app.route('/demo')
def jinja_demo():
    return render_template('jinja_demo.html')

@app.route('/api/order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        if not data or not data.get('items') or not data.get('customer'):
            return jsonify({
                'status': 'error',
                'message': 'Неповні дані замовлення'
            }), 400
        
        customer = data['customer']
        items = data['items']
        required_fields = ['name', 'phone', 'address']
        for field in required_fields:
            if not customer.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Поле "{field}" є обов\'язковим'
                }), 400
        
        total_amount = 0
        order = Order(
            customer_name=customer['name'],
            customer_phone=customer['phone'],
            customer_address=customer['address'],
            customer_email=customer.get('email', ''),
            notes=customer.get('notes', ''),
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()
        
        for item in items:
            pizza = Pizza.query.get(item['pizza_id'])
            if not pizza or not pizza.available:
                return jsonify({
                    'status': 'error',
                    'message': f'Піца з ID {item["pizza_id"]} недоступна'
                }), 400
            
            quantity = int(item.get('quantity', 1))
            item_total = pizza.price * quantity
            total_amount += item_total
            
            order_item = OrderItem(
                order_id=order.id,
                pizza_id=pizza.id,
                quantity=quantity,
                price=pizza.price,
                total=item_total
            )
            db.session.add(order_item)
        
        order.total_amount = total_amount
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Замовлення успішно оформлено! Ми зв\'яжемося з вами найближчим часом.',
            'order_id': f'ORD-{order.id:06d}',
            'total_amount': total_amount
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Помилка при оформленні замовлення: {str(e)}'
        }), 500

@app.template_filter('format_price')
def format_price(price):
    return f"{price} грн"

@app.template_global()
def get_current_year():
    from datetime import datetime
    return datetime.now().year

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def init_database():
    with app.app_context():
        db.create_all()
        
        if Pizza.query.count() == 0:
            test_pizzas = [
                Pizza(name='Маргарита', 
                     ingredients='Томатний соус, моцарела, свіжий базилік, оливкова олія',
                     price=250, category='classic', category_display='Класична', 
                     size='30 см', popular=True),
                Pizza(name='Пепероні',
                     ingredients='Томатний соус, моцарела, пепероні, орегано',
                     price=320, category='classic', category_display='Класична',
                     size='30 см', popular=True),
                Pizza(name='Гавайська',
                     ingredients='Томатний соус, моцарела, шинка, ананас',
                     price=280, category='classic', category_display='Класична',
                     size='30 см', popular=False),
                Pizza(name='Кватро Формаджі',
                     ingredients='Білий соус, моцарела, горгонзола, пармезан, рікота',
                     price=380, category='premium', category_display='Преміум',
                     size='30 см', popular=False),
                Pizza(name='М\'ясна',
                     ingredients='Томатний соус, моцарела, пепероні, шинка, ковбаса, бекон',
                     price=420, category='premium', category_display='Преміум',
                     size='32 см', popular=True),
                Pizza(name='Овочева',
                     ingredients='Томатний соус, моцарела, помідори, перець, цибуля, гриби, оливки',
                     price=300, category='vegetarian', category_display='Вегетаріанська',
                     size='30 см', popular=False),
            ]
            
            for pizza in test_pizzas:
                db.session.add(pizza)
            
            poll = Poll(
                title='Яка піца вам подобається найбільше?',
                description='Оберіть свою улюблену піцу з нашого меню!'
            )
            db.session.add(poll)
            
            db.session.commit()
            print("База даних ініціалізована з тестовими даними!")

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
