import requests

# Проверка GET-запроса
response_get = requests.get("http://127.0.0.1:5000/weather?lat=40.7128&lon=-74.0060")
print("GET Response:")
print(response_get.json())

# Проверка POST-запроса
route_data = {
    "route": [
        {"lat": 40.7128, "lon": -74.0060},
        {"lat": 34.0522, "lon": -118.2437}
    ]
}
response_post = requests.post("http://127.0.0.1:5000/route_weather", json=route_data)
print("\nPOST Response:")
print(response_post.json())
