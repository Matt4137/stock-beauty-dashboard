import requests
import pandas as pd
import os

url = "https://dummyjson.com/products"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print("Error en la petición:", response.status_code)
    exit()

df = pd.DataFrame(data["products"])

os.makedirs("datos", exist_ok=True)

df.to_csv("datos/productos_raw.csv", index=False)

print("Ingesta completa:", len(df), "registros")

