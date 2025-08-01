import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_api_pizzas():
    print("🍕 Тестування API піц...")
    try:
        response = requests.get(f'{BASE_URL}/api/pizzas')
        if response.status_code == 200:
            pizzas = response.json()
            print(f"Знайдено {len(pizzas)} піц")
            for pizza in pizzas[:3]:
                print(f"   - {pizza['name']}: {pizza['price']} грн")
        else:
            print(f"Помилка: {response.status_code}")
    except Exception as e:
        print(f"Помилка: {e}")

def test_order_api():
    print("\n🛒 Тестування API замовлень...")
    
    test_order = {
        "customer": {
            "name": "Тест Клієнт",
            "phone": "+380123456789",
            "address": "вул. Тестова, 1",
            "email": "test@example.com",
            "notes": "Тестове замовлення"
        },
        "items": [
            {"pizza_id": 1, "quantity": 2},
            {"pizza_id": 2, "quantity": 1}
        ]
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/order',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_order)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                print(f"✅ Замовлення створено: {result['order_id']}")
                print(f"   Сума: {result['total_amount']} грн")
            else:
                print(f"❌ Помилка: {result['message']}")
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            print(f"   Відповідь: {response.text}")
    except Exception as e:
        print(f"❌ Помилка: {e}")

def test_poll_vote():
    print("\n📊 Тестування опитування...")
    
    vote_data = {
        'poll_id': 1,
        'pizza_id': 1
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/poll/vote',
            data=vote_data
        )
        
        if response.status_code == 200:
            print("Голос додано")
        else:
            print(f"⚠️Статус: {response.status_code}")
    except Exception as e:
        print(f"Помилка: {e}")

def test_pages():
    print("\n🌐 Тестування сторінок...")
    
    pages = [
        ('/', 'Головна'),
        ('/menu', 'Меню'),
        ('/order', 'Замовлення'),
        ('/poll', 'Опитування'),
        ('/poll/results', 'Результати'),
        ('/admin', 'Адмін панель')
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f'{BASE_URL}{url}')
            status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {status} {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == '__main__':
    print("Початок тестування веб-застосунку Oderman\n")
    
    test_pages()
    test_api_pizzas()
    test_order_api()
    test_poll_vote()
    
    print("\nТестування завершено!")
