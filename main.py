from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = "0a05aaca142eafd2174374fa14f28035"

def get_weather_data(lat, lon):
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    current_response = requests.get(current_url).json()
    
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    forecast_response = requests.get(forecast_url).json()
    
    pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    pollution_response = requests.get(pollution_url).json()
    
    daily_forecasts = {}
    for item in forecast_response['list']:
        day = datetime.fromtimestamp(item['dt']).strftime('%A')
        temp_min = item['main']['temp_min']
        temp_max = item['main']['temp_max']

        if day not in daily_forecasts:
            daily_forecasts[day] = {
                'temp_min': temp_min,
                'temp_max': temp_max,
                'icon': item['weather'][0]['icon'],
                'description': item['weather'][0]['description']
            }
        else:
            daily_forecasts[day]['temp_min'] = min(daily_forecasts[day]['temp_min'], temp_min)
            daily_forecasts[day]['temp_max'] = max(daily_forecasts[day]['temp_max'], temp_max)

    forecast = []
    for day, data in list(daily_forecasts.items())[:5]:
        forecast.append({
            'day': day,
            'temp_min': data['temp_min'],
            'temp_max': data['temp_max'],
            'description': data['description'],
            'icon': data['icon']
        })

    weather_data = {
        'current': {
            'temp': current_response['main']['temp'],
            'feels_like': current_response['main']['feels_like'],
            'humidity': current_response['main']['humidity'],
            'wind_speed': current_response['wind']['speed'],
            'description': current_response['weather'][0]['description'],
            'icon': current_response['weather'][0]['icon'],
            'day': datetime.fromtimestamp(current_response['dt']).strftime('%A'),
            'city': current_response['name'],
            'country': current_response['sys']['country'],
            'temp_min': current_response['main']['temp_min'],
            'temp_max': current_response['main']['temp_max']
        },
        'forecast': forecast,
        'pollution': {
            'aqi': pollution_response['list'][0]['main']['aqi'],
            'components': pollution_response['list'][0]['components']
        }
    }
    
    return weather_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    location = data.get('location', '')
    lat = data.get('lat')
    lon = data.get('lon')
    
    if not (lat and lon):
        location_parts = [part.strip() for part in location.split(',')]
        city = location_parts[0]
        country_code = location_parts[1] if len(location_parts) > 1 else ''
        
        if country_code:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit=1&appid={API_KEY}"
        else:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
            
        geo_response = requests.get(geo_url).json()
        
        if not geo_response:
            return jsonify({'error': 'Location not found'})
        
        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']
    
    try:
        weather_data = get_weather_data(lat, lon)
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)