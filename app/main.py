from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/weatherdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для истории запросов
class WeatherHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    description = db.Column(db.String(200))
    humidity = db.Column(db.Integer)
    wind_speed = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'temperature': self.temperature,
            'description': self.description,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    city = request.json.get('city')
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            weather_entry = WeatherHistory(
                city=city,
                temperature=data['main']['temp'],
                description=data['weather'][0]['description'],
                humidity=data['main']['humidity'],
                wind_speed=data['wind']['speed']
            )
            db.session.add(weather_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            })
        else:
            return jsonify({'success': False, 'error': 'City not found'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/history')
def get_history():
    history = WeatherHistory.query.order_by(WeatherHistory.timestamp.desc()).limit(10).all()
    return jsonify([h.to_dict() for h in history])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
