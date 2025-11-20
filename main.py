import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://pizzarte.pe/collections/listo-para-hornear'

response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

product_elements = soup.find_all('div', class_='product-info-inner')

# Inicializar una lista para guardar los resultados
products_data = []

# Iterar sobre cada elemento de producto
for product in product_elements:
    # Dentro de cada elemento 'product', buscamos el título y el precio
    
    # Extrae el Título (buscando 'a' dentro de 'h4.product-title')
    title_element = product.find('h4', class_='product-title').find('a')
    product_title = title_element.get_text(strip=True) if title_element else "N/A"
    
    # Extrae el Precio (buscando el div con la clase 'prod-price')
    price_element = product.find('div', class_='prod-price')
    product_price = price_element.get_text(strip=True) if price_element else "N/A"
    
    # Guardar los datos
    products_data.append({
        'title': product_title,
        'price': product_price
    })

# Convertir la lista de diccionarios en un DataFrame de pandas
df = pd.DataFrame(products_data)

df['title'] = df['title'].str.replace('Pizzarte', 'Continental', regex=False)
df['title'] = df['title'].str.replace('Capresse', 'Margarita', regex=False)
df['title'] = df['title'].str.replace('Peperoni', 'Salame', regex=False)
df['title'] = df['title'].str.replace('Jamón', 'Americana', regex=False)

df['price'] = df['price'].str.replace('S/. ', '', regex=False)
df['price'] = df['price'].astype(float)

df['restaurant'] = 'Pizzarte'

# Crear un diccionario a partir de nueva data
dontomasino_data = {
    'title': ['Mozzarella', 'Hawaiana', 'Continental', 'Margarita', 'Salame', 'Americana', 'Champiñones', 'Genovesa', 'Zucchini'],
    'price': [35, 35, 35, 35, 40, 35, 35, 35, 35]
}

df2 = pd.DataFrame(dontomasino_data)
df2['price'] = df2['price'].astype(float)
df2['restaurant'] = 'Don Tomasino'

df_final = pd.concat([df, df2], ignore_index=True)

# --- ANÁLISIS PIVOT Y CÁLCULO DE DIFERENCIAS ---
# Crear la tabla dinámica (pivot) para comparación
df_pivot = df_final.pivot(index='title', columns='restaurant', values='price').reset_index()
df_pivot = df_pivot.fillna(0)

# Calcular la Diferencia Absoluta (Don Tomasino - Pizzarte)
df_pivot['Diferencia_Absoluta'] = df_pivot['Don Tomasino'] - df_pivot['Pizzarte']

# Corregir la Diferencia Absoluta (Si Pizzarte no tiene el producto, la diferencia es 0)
condicion_no_comparable = (df_pivot['Pizzarte'] == 0)
df_pivot.loc[condicion_no_comparable, 'Diferencia_Absoluta'] = 0

# Calcular la Diferencia Porcentual
df_pivot['Diferencia_Porcentual'] = (
    df_pivot['Diferencia_Absoluta'] / 
    df_pivot['Pizzarte'].replace(0, float('nan'))
).fillna(0) * 100

# --- CLASIFICACIÓN EN ESCENARIOS ---
df_pivot['Escenario'] = 'N/A'

# Escenario 1: Ambos
ambos = (df_pivot['Don Tomasino'] > 0) & (df_pivot['Pizzarte'] > 0)
df_pivot.loc[ambos, 'Escenario'] = 'Ambos'

# Escenario 2: Solo Pizzarte
solo_pizzarte = (df_pivot['Don Tomasino'] == 0) & (df_pivot['Pizzarte'] > 0)
df_pivot.loc[solo_pizzarte, 'Escenario'] = 'Pizzarte'

# Escenario 3: Solo Don Tomasino
solo_don_tomasino = (df_pivot['Don Tomasino'] > 0) & (df_pivot['Pizzarte'] == 0)
df_pivot.loc[solo_don_tomasino, 'Escenario'] = 'Don Tomasino'

# --- RESULTADO FINAL ---
df_filtered = df_pivot[df_pivot['Escenario'].isin(['Ambos', 'Don Tomasino'])].reset_index(drop=True)
df_filtered = df_filtered.drop(columns=['Escenario'])
#print(df_filtered)

df_pizzarte = df_pivot[df_pivot['Escenario'] == 'Pizzarte'].reset_index(drop=True)
df_pizzarte = df_pizzarte.drop(columns=['Escenario'])
#print(df_pizzarte)

# Guardar los resultados en archivos CSV
df_filtered.to_csv('comparacion_don_tomasino_pizzarte.csv', index=False)
df_pizzarte.to_csv('productos_solo_pizzarte.csv', index=False)