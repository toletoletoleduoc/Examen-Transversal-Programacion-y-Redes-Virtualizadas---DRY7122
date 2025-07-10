import requests
import json
import time

def cargar_api_key(archivo="ORSapikey.txt"):
    """Carga la API key desde un archivo de texto."""
    try:
        with open(archivo, 'r') as f:
            # .strip() elimina espacios o saltos de línea accidentales
            key = f.read().strip()
            if not key:
                print(f"Error: El archivo '{archivo}' está vacío.")
                return None
            return key
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo}'.")
        print("Asegúrese de que el archivo exista en el mismo directorio y contenga su API key de OpenRouteService.")
        return None

# Cargar la API Key al inicio del script
API_KEY = cargar_api_key()

# Detener la ejecución si no se pudo cargar la key
if not API_KEY:
    exit()

def obtener_coordenadas(ciudad):
    """
    Convierte el nombre de una ciudad en coordenadas y obtiene su nombre completo 
    (ej: 'Santiago, Chile') usando la API de geocodificación de ORS.
    """
    url = f"https://api.openrouteservice.org/geocode/search?api_key={API_KEY}&text={ciudad}"
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanza un error si la solicitud falla (código 4xx o 5xx)
        datos = respuesta.json()
        if datos['features']:
            feature = datos['features'][0]
            coordenadas = feature['geometry']['coordinates']
            nombre_completo = feature['properties']['label']
            return {
                "coordenadas": coordenadas,
                "nombre_completo": nombre_completo
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de geocodificación: {e}")
        return None


def obtener_ruta(coord_origen, coord_destino, perfil_transporte):
    """Obtiene la ruta, distancia, duración y narrativa del viaje entre dos coordenadas."""
    # La URL ahora usa el perfil de transporte elegido (auto, bicicleta, etc.)
    url = f"https://api.openrouteservice.org/v2/directions/{perfil_transporte}"
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [coord_origen, coord_destino]
    }
    try:
        respuesta = requests.post(url, json=body, headers=headers)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de direcciones: {e}")
        return None

def main():
    print("\n--- Programa para calcular Viajes Nacionales o Internacionales ---")
    
   
    modos_transporte = {
        "auto": "driving-car",
        "bicicleta": "cycling-regular",
        "caminar": "foot-walking"
    }
    # --- SELECCIÓN DE ORIGEN Y DESTINO ---
    while True:
        origen = input("Ingrese la Ciudad de Origen (o 's' para salir): ")
        if origen.lower() == 's':
            break
        
        destino = input("Ingrese la Ciudad de Destino (o 's' para salir): ")
        if destino.lower() == 's':
            break

        # --- SELECCIÓN DE TRANSPORTE ---
        perfil_ruta = ""
        while perfil_ruta not in modos_transporte.values():
            eleccion = input("Elija el medio de transporte (auto, bicicleta, caminar): ").lower()
            if eleccion in modos_transporte:
                perfil_ruta = modos_transporte[eleccion]
            else:
                print("Opción no válida. Por favor, elija entre auto, bicicleta o caminar.")

        info_origen = obtener_coordenadas(origen)
        info_destino = obtener_coordenadas(destino)

        if not info_origen:
            print(f"No se pudo encontrar la ciudad de origen: '{origen}'. Intente de nuevo.")
            continue
        if not info_destino:
            print(f"No se pudo encontrar la ciudad de destino: '{destino}'. Intente de nuevo.")
            continue

        print("\nCalculando la ruta...")
        # Pasamos el perfil de ruta elegido a la función
        ruta_info = obtener_ruta(info_origen['coordenadas'], info_destino['coordenadas'], perfil_ruta)

        if ruta_info:
            ruta = ruta_info['routes'][0]
            resumen = ruta['summary']
            segmentos = ruta['segments'][0]

            # 1. Distancia en kilómetros y millas
            distancia_km = resumen['distance'] / 1000
            distancia_millas = distancia_km * 0.621371

            # 2. Duración en HH:MM:SS
            segundos_totales = resumen['duration']
            horas = int(segundos_totales // 3600)
            minutos = int((segundos_totales % 3600) // 60)
            segundos = int(segundos_totales % 60)

            # --- PRINT DE DETALLES DEL VIAJE ---
            print("\n--- RESULTADOS DEL VIAJE ---")
            print(f"Ciudad de origen: {info_origen['nombre_completo']}")
            print(f"Ciudad de destino: {info_destino['nombre_completo']}")
            print(f"Medio de transporte: {eleccion.capitalize()}")
            print(f"Distancia total: {distancia_km:.2f} km ({distancia_millas:.2f} millas)")
            print(f"Duración del viaje: {horas:02d} horas, {minutos:02d} minutos y {segundos:02d} segundos")

            # 3. Combustible requerido (solo para 'auto')
            if perfil_ruta == 'driving-car':
                consumo_promedio_km_l = 12.0
                combustible_litros = distancia_km / consumo_promedio_km_l
                print(f"Combustible requerido: {combustible_litros:.2f} litros (estimado)")
            
            # 4. Narrativa del viaje
            print("\n--- NARRATIVA DEL VIAJE ---")
            for i, paso in enumerate(segmentos['steps']):
                print(f"{i + 1}. {paso['instruction']} ({paso['distance'] / 1000:.2f} km)")
            
            print("\n" + "="*40 + "\n")
        else:
            print("No se pudo calcular la ruta. Verifique las ciudades e intente de nuevo.")

    print("Programa finalizado. ¡Buen viaje!")

if __name__ == "__main__":
    main()
