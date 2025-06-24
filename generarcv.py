import requests
import csv
import time
import random
from datetime import datetime, timedelta

def fecha_aleatoria():
    inicio = datetime(2022, 1, 1)
    fin = datetime.now()
    return inicio + timedelta(days=random.randint(0, (fin - inicio).days))

def generar_coordenadas_chile():
    lat = round(random.uniform(-56.0, -17.5), 6)
    lon = round(random.uniform(-75.0, -66.0), 6)
    return lat, lon

with open("direcciones_osm_500.csv", mode="w", newline="", encoding="utf-8") as archivo:
    writer = csv.writer(archivo, delimiter=";")
    writer.writerow(["Nombre del lugar", "Dirección Completa", "Georeferencia", "Fecha de registro"])

    for i in range(500):
        lat, lon = generar_coordenadas_chile()
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {"User-Agent": "Plowui-Test/1.0 (contacto@tudominio.cl)"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if "address" in data:
                address = data["address"]
                nombre = data.get("name") or data.get("display_name", "Lugar sin nombre")
                ciudad = address.get("city") or address.get("town") or address.get("village") or "Desconocido"
                estado = address.get("state", "Desconocido")
                provincia = address.get("region", "Desconocido")
                pais = address.get("country", "Desconocido")
                direccion = f"{ciudad}, {estado}, {provincia}, {pais}"
                fecha = fecha_aleatoria().strftime("%Y-%m-%d")
                writer.writerow([nombre, direccion, f"{lat}, {lon}", fecha])

        except Exception as e:
            print(f"Error en coordenada {lat},{lon}: {e}")

        time.sleep(1)  # Respetar el límite de Nominatim