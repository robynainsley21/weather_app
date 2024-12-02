from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_key = "0a05aaca142eafd2174374fa14f28035"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric"
    response = requests.get(url)
    data = response.json()