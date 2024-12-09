from flask import Flask, request, jsonify, render_template
import requests
import matplotlib.pyplot as plt

app = Flask(__name__)
API_KEY = '4NHH5MewX3ey6BIbA1RfEGHBWmNLKHZA'


def get_location_key(lat, lon):
    """Получение LocationKey для координат."""
    url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    params = {
        'apikey': API_KEY,
        'q': f"{lat},{lon}"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('Key')  # Извлечение LocationKey
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location key: {e}")
        return None


def check_bad_weather(temperature, wind_speed, precipitation_probability):
    """
    Определяет, является ли погода неблагоприятной.

    Параметры:
    - temperature (float): Температура в градусах Цельсия.
    - wind_speed (float): Скорость ветра в км/ч.
    - precipitation_probability (float): Вероятность осадков в %.

    Возвращает:
    - dict: Результат анализа погодных условий.
    """
    is_bad = False
    reasons = []

    if temperature < 0 or temperature > 35:
        is_bad = True
        reasons.append(f"Temperature is extreme ({temperature}°C)")

    if wind_speed > 50:
        is_bad = True
        reasons.append(f"High wind speed ({wind_speed} km/h)")

    if precipitation_probability > 70:
        is_bad = True
        reasons.append(f"High chance of precipitation ({precipitation_probability}%)")

    return {
        "is_bad_weather": is_bad,
        "reasons": reasons if is_bad else ["Weather conditions are favorable"]
    }


def get_weather_data(lat, lon):
    """Получение данных о погоде и обработка ошибок API."""
    location_key = get_location_key(lat, lon)
    if not location_key:
        return {"error": "Failed to fetch location key"}

    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {
        'apikey': API_KEY,
        'metric': True
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            forecast = data['DailyForecasts'][0]

            # Извлечение данных
            temperature = {
                'min': forecast['Temperature']['Minimum']['Value'],
                'max': forecast['Temperature']['Maximum']['Value']
            }
            wind_speed = forecast.get('Day', {}).get('Wind', {}).get('Speed', {}).get('Value', 0)
            precipitation_probability = forecast.get('Day', {}).get('PrecipitationProbability', 0)

            # Оценка неблагоприятных условий
            analysis = check_bad_weather(temperature['max'], wind_speed, precipitation_probability)

            return {
                'date': forecast['Date'],
                'temperature': temperature,
                'wind_speed': wind_speed,
                'precipitation_probability': precipitation_probability,
                'conditions': forecast['Day']['IconPhrase'],
                'analysis': analysis
            }
        else:
            return {"error": f"API error: {response.status_code} - {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"API connection failed: {e}"}


@app.route('/')
def index():
    """Главная страница с формой для ввода маршрута."""
    return render_template('index.html')


@app.route('/check_route', methods=['POST'])
def check_route():
    """Обработка маршрута из формы."""
    try:
        start = request.form.get('start')
        end = request.form.get('end')

        # Пример сопоставления городов и координат
        city_to_coordinates = {
            "moscow": (55.856719, 37.608954),
            "sochi": (43.582890, 39.730607)
        }

        start_coords = city_to_coordinates.get(start.lower())
        end_coords = city_to_coordinates.get(end.lower())

        if not start_coords or not end_coords:
            return render_template("result.html", result="City not found or unsupported.")

        # Получение данных о погоде
        start_weather = get_weather_data(*start_coords)
        end_weather = get_weather_data(*end_coords)

        if "error" in start_weather or "error" in end_weather:
            error_message = start_weather.get("error") or end_weather.get("error")
            return render_template("result.html", result=f"Error fetching weather data: {error_message}")

        # Формирование результата
        result = {
            "start": {
                "city": start.capitalize(),
                "weather": start_weather
            },
            "end": {
                "city": end.capitalize(),
                "weather": end_weather
            }
        }

        return render_template("result.html", result=result)

    except Exception as e:
        return render_template("result.html", result=f"Unexpected error: {e}")


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
