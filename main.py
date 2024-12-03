from flask import Flask, render_template, request
import requests

app = Flask(__name__)

#  OpenWeather API key
API_key = "0a05aaca142eafd2174374fa14f28035"

@app.route('/')
def index():
 return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
 city = request.form['city']
 url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric'
 response = requests.get(url).json()

# Validating user input: if city code not found error message is returned
 if response.get('cod') != 200:
     return render_template('index.html', error="City not found.")

 weather_data = {
     'city': city,
     'temperature': response['main']['temp'],
     'description': response['weather'][0]['description'],
     'humidity': response['main']['humidity'],
     'wind_speed': response['wind']['speed'],
     'pressure': response['main']['pressure'],
     'icon': response['weather'][0]['icon']

 }
 return render_template('weather.html', weather_data=weather_data)

if __name__ == '__main__':
 app.run(debug=True)