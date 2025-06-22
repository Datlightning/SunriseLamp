import requests

res = requests.get("https://vihas.pythonanywhere.com/processed-image")
data = res.json()  # will raise an error if the response is not JSON
print(data)