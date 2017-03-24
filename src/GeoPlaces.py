import googlemaps as gm
import pandas as pd

# Generamos el cliente con la API Key
gmaps = gm.Client(key='AIzaSyBeI-eXp9ta99Fv6HwZ7JeQQ_sRQnrYo2E')

# Guardamos la respuesta de la llamada a la API Geocoding
geocode_result = gmaps.geocode("28035", region="es")

# Guardamos latitud y longitud 
lat = geocode_result[0]["geometry"]["location"]["lat"]
lng = geocode_result[0]["geometry"]["location"]["lng"]

# Nos quedamos con los lugares (places) cercanos a esa latitud y longitud
places = gmaps.places('restaurante', location=[lat, lng], radius=100, language="es-ES")["results"]

# Generamos un diccionario con los datos que nos interesan y luego un DataFrame a partir del diccionario
d = {}
for index, place in enumerate(places):
    try:
        url = gmaps.place(place["place_id"], language="es-ES")["result"]["url"] #Get the url
    except:
        url = "No URL from Google Places"
        
    try:
        name = place["name"]
    except:
        name = "No name from Google Places"
        
    try:
        rating = place["rating"]
    except:
        rating = None
        
    d[index] =  {"name": name,"rating": rating, "url": url}

df = pd.DataFrame(d).transpose()

# Sacamos el los 10 con mejor rating y los 10 con peor rating
top10 = df.sort_values(by="rating", ascending=False, na_position="last").head(10).reset_index().drop("index", axis=1)
last10 = df.sort_values(by="rating", ascending=True, na_position="first").head(10).reset_index().drop("index", axis=1)




