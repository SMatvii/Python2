import requests
import os
from datetime import datetime

class WeatherService:
    def __init__(self, api_key, city='Kyiv', country='UA'):
        self.api_key = api_key
        self.city = city
        self.country = country
        self.base_url = 'https://api.openweathermap.org/data/2.5'
    
    def get_current_weather(self):
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{self.city},{self.country}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'uk'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': True,
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'feels_like': round(data['main']['feels_like']),
                'city': data['name']
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Помилка запиту до API: {str(e)}'
            }
        except KeyError as e:
            return {
                'success': False,
                'error': f'Неочікувана структура відповіді API: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Загальна помилка: {str(e)}'
            }
    
    def get_pizza_recommendation(self, weather_data):
        if not weather_data.get('success'):
            return {
                'title': '🍕 Завжди гарний час для піци!',
                'message': 'Незалежно від погоди, наші піци завжди смачні!',
                'recommended_pizza': 'Маргарита'
            }
        
        temp = weather_data.get('temperature', 20)
        description = weather_data.get('description', '').lower()

        if temp >= 25:
            return {
                'title': '🌞 Спекотна погода!',
                'message': 'В таку жару рекомендуємо легкі піци з овочами та свіжими інгредієнтами.',
                'recommended_pizza': 'Овочева',
                'reason': 'Легка та освіжаюча'
            }
        elif temp <= 5:
            return {
                'title': '❄️ Холодно на вулиці!',
                'message': 'Зігрійтеся нашими ситними м\'ясними піцами!',
                'recommended_pizza': 'М\'ясна',
                'reason': 'Ситна та зігрівальна'
            }
        elif 'дощ' in description or 'rain' in description:
            return {
                'title': '🌧️ Дощова погода!',
                'message': 'В дощову погоду немає нічого кращого за класичну піцу з доставкою додому!',
                'recommended_pizza': 'Пепероні',
                'reason': 'Класика для затишку'
            }
        elif 'сніг' in description or 'snow' in description:
            return {
                'title': '❄️ Сніжна погода!',
                'message': 'Снігопад - ідеальний час для гарячої піци з багатьма сирами!',
                'recommended_pizza': 'Кватро Формаджі',
                'reason': 'Гаряча та сирна'
            }
        elif 'хмарно' in description or 'cloud' in description:
            return {
                'title': '☁️ Хмарна погода!',
                'message': 'Похмурий день стане яскравішим з нашою яскравою Гавайською піцою!',
                'recommended_pizza': 'Гавайська',
                'reason': 'Яскрава та смачна'
            }
        else:
            return {
                'title': '🌤️ Чудова погода!',
                'message': 'В таку погоду ідеально підійде наша популярна Маргарита!',
                'recommended_pizza': 'Маргарита',
                'reason': 'Класична та улюблена'
            }

def get_weather_icon_emoji(icon_code):
    icon_map = {
        '01d': '☀️',  
        '01n': '🌙', 
        '02d': '⛅',  
        '02n': '☁️',  
        '03d': '☁️',
        '03n': '☁️',
        '04d': '☁️',
        '04n': '☁️',
        '09d': '🌧️',
        '09n': '🌧️',
        '10d': '🌦️',
        '10n': '🌧️',
        '11d': '⛈️',
        '11n': '⛈️',
        '13d': '❄️',
        '13n': '❄️',
        '50d': '🌫️',
        '50n': '🌫️', 
    }
    return icon_map.get(icon_code, '🌤️')
