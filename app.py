from flask import Flask, request, jsonify
import requests
import matplotlib.pyplot as plt

app = Flask(__name__)
API_KEY = 'NXW094u1iVpVAR2avrB63pFmqGqxXC2b'  # Замените на ваш реальный API-ключ


def get_location_key(lat, lon):
    """Получение LocationKey для координат."""
    url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    params = {
        'apikey': API_KEY,
        'q': f"{lat},{lon}"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('Key')  # Извлечение LocationKey
    else:
        print(f"Failed to fetch location key: {response.text}")
        return None


def get_weather_data(lat, lon):
    """Получение данных о погоде по координатам."""
    location_key = get_location_key(lat, lon)
    if not location_key:
        return {"error": "Failed to fetch location key"}

    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {
        'apikey': API_KEY,
        'metric': True
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        forecast = data['DailyForecasts'][0]
        return {
            'date': forecast['Date'],
            'temperature': {
                'min': forecast['Temperature']['Minimum']['Value'],
                'max': forecast['Temperature']['Maximum']['Value']
            },
            'precipitation': {
                'type': forecast['Day'].get('PrecipitationType', 'None'),
                'intensity': forecast['Day'].get('PrecipitationIntensity', 'None'),
                'has_precipitation': forecast['Day']['HasPrecipitation']
            },
            'conditions': forecast['Day']['IconPhrase']
        }
    else:
        print(f"Failed to fetch weather data: {response.text}")
        return {"error": "Failed to fetch weather data"}


@app.route('/weather', methods=['GET'])
def weather():
    """Эндпоинт для получения данных о погоде по одной точке."""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Please provide latitude and longitude"}), 400
    weather_data = get_weather_data(lat, lon)
    return jsonify(weather_data)


@app.route('/route_weather', methods=['POST'])
def route_weather():
    """Эндпоинт для получения данных о погоде для маршрута."""
    data = request.json
    if not data or 'route' not in data:
        return jsonify({"error": "Please provide a route"}), 400

    weather_reports = []
    for point in data['route']:
        lat = point.get('lat')
        lon = point.get('lon')
        if not lat or not lon:
            continue
        weather_data = get_weather_data(lat, lon)
        weather_reports.append({
            'location': point,
            'weather': weather_data
        })

    # Визуализация данных
    plot_weather(weather_reports)

    return jsonify(weather_reports)


def plot_weather(data):
    """Создание графика температуры для маршрута."""
    locations = [f"{p['location']['lat']},{p['location']['lon']}" for p in data]
    temperatures = [p['weather']['temperature']['max'] for p in data]

    plt.figure(figsize=(10, 5))
    plt.plot(locations, temperatures, marker='o')
    plt.title('Temperature Along the Route')
    plt.xlabel('Location')
    plt.ylabel('Max Temperature (°C)')
    plt.grid()
    plt.savefig('weather_route.png')
    print("Temperature plot saved as 'weather_route.png'.")


if __name__ == '__main__':
    app.run(debug=True)
