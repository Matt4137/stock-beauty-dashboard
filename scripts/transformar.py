import pandas as pd
import os

df = pd.read_csv("datos/productos_raw.csv")

df = df[["title", "price", "category", "brand", "stock"]]

df.columns = ["producto", "precio", "categoria", "marca", "stock"]

df["marca"].fillna("Sin marca", inplace=True)
df["stock"].fillna(0, inplace=True)

df = df[df["precio"] > 0]
df = df[df["stock"] >= 0]

df["producto"] = df["producto"].str.title()
df["marca"] = df["marca"].str.title()

traducciones_categoria = {
    "beauty": "Belleza",
    "fragrances": "Perfumes",
    "furniture": "Muebles"
}

df["categoria"] = df["categoria"].map(traducciones_categoria)

df = df[df["categoria"].notna()]

df["valor_inventario"] = df["precio"] * df["stock"]

df.drop_duplicates(inplace=True)

print("Registros finales:", len(df))
print(df.describe())

os.makedirs("datos", exist_ok=True)
df.to_csv("datos/productos_limpios.csv", index=False)

print("Transformación avanzada completa")