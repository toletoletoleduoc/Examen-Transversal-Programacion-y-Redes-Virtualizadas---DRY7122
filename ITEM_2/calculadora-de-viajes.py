import requests
import json

def cargar_api_key(archivo="GraphHopperApiKey.txt"):
    """Carga la API key de GraphHopper desde un archivo de texto."""
    try:
        with open(archivo, 'r') as f:
            key = f.read().strip()
            if not key:
                print(f"Error: El archivo '{archivo}' está vacío.")
                return None
            return key
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo}'.")
        print("Asegúrese de que el archivo exista y contenga su API key de GraphHopper.")
        return None

# Cargar la API Key al inicio del script
API_KEY = cargar_api_key()

# Detener la ejecución si no se pudo cargar la key
if not API_KEY:
    exit()

def obtener_info_lugar(lugar):
    """
    Convierte el nombre de un lugar en coordenadas (lat, lon) y obtiene su nombre 
    completo usando la API de Geocodificación de GraphHopper.
    """
    url = "https://graphhopper.com/api/1/geocode"
    params = {
        'q': lugar,
        'key': API_KEY,
        'locale': 'es' # Para obtener resultados en español
    }
    try:
        respuesta = requests.get(url, params=params)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if datos['hits']:
            # Tomamos el primer resultado, que suele ser el más relevante
            hit = datos['hits'][0]
            coordenadas = (hit['point']['lat'], hit['point']['lng'])
            nombre_completo = hit.get('name', lugar)
            # A veces el nombre es más descriptivo si combinamos campos
            if 'city' in hit and 'country' in hit:
                nombre_completo = f"{hit.get('city', hit.get('name'))}, {hit['country']}"

            return {
                "coordenadas": coordenadas,
                "nombre_completo": nombre_completo
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Geocodificación: {e}")
        return None

def obtener_ruta(coord_origen, coord_destino, perfil_transporte):
    """Obtiene la ruta desde la API de Routing de GraphHopper."""
    url = "https://graphhopper.com/api/1/route"
    
    # Formateamos las coordenadas como "lat,lon"
    punto_origen = f"{coord_origen[0]},{coord_origen[1]}"
    punto_destino = f"{coord_destino[0]},{coord_destino[1]}"

    params = {
        'point': [punto_origen, punto_destino],
        'vehicle': perfil_transporte,
        'key': API_KEY,
        'instructions': 'true', # Para obtener la narrativa
        'locale': 'es' # Para que la narrativa esté en español
    }
    try:
        respuesta = requests.get(url, params=params)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Rutas: {e}")
        return None

def main():
    print("\n--- Calculadora de Viajes Nacionales e Internacionales (con API de GraphHopper) ---")
    
    # Mapeo de la elección del usuario a los perfiles de GraphHopper
    modos_transporte = {
        "auto": "car",
        "bicicleta": "bike",
        "caminar": "foot"
    }

    while True:
        origen = input("Ingrese la Ciudad de Origen (o 's' para salir): ")
        if origen.lower() == 's':
            break
        
        destino = input("Ingrese la Ciudad de Destino (o 's' para salir): ")
        if destino.lower() == 's':
            break

        perfil_ruta = ""
        eleccion = ""
        while not perfil_ruta:
            eleccion_input = input("Elija el medio de transporte (auto, bicicleta, caminar): ").lower()
            if eleccion_input in modos_transporte:
                perfil_ruta = modos_transporte[eleccion_input]
                eleccion = eleccion_input
            else:
                print("Opción no válida. Por favor, elija entre auto, bicicleta o caminar.")

        info_origen = obtener_info_lugar(origen)
        info_destino = obtener_info_lugar(destino)

        if not info_origen:
            print(f"No se pudo encontrar la ciudad de origen: '{origen}'. Intente de nuevo.")
            continue
        if not info_destino:
            print(f"No se pudo encontrar la ciudad de destino: '{destino}'. Intente de nuevo.")
            continue

        print("\nCalculando la ruta...")
        ruta_info = obtener_ruta(info_origen['coordenadas'], info_destino['coordenadas'], perfil_ruta)

        if ruta_info and 'paths' in ruta_info:
            ruta = ruta_info['paths'][0]
            
            # 1. Distancia en km y millas (viene en metros)
            distancia_km = ruta['distance'] / 1000
            distancia_millas = distancia_km * 0.621371

            # 2. Duración en HH:MM:SS (viene en milisegundos)
            segundos_totales = ruta['time'] / 1000
            horas = int(segundos_totales // 3600)
            minutos = int((segundos_totales % 3600) // 60)
            segundos = int(segundos_totales % 60)

            print("\n--- RESULTADOS DEL VIAJE ---")
            print(f"Ciudad de origen: {info_origen['nombre_completo']}")
            print(f"Ciudad de destino: {info_destino['nombre_completo']}")
            print(f"Medio de transporte: {eleccion.capitalize()}")
            print(f"Distancia total: {distancia_km:.2f} km ({distancia_millas:.2f} millas)")
            print(f"Duración del viaje: {horas:02d} horas, {minutos:02d} minutos y {segundos:02d} segundos")

            # 3. Combustible (solo para auto)
            if perfil_ruta == 'car':
                consumo_promedio_km_l = 12.0
                combustible_litros = distancia_km / consumo_promedio_km_l
                print(f"Combustible requerido: {combustible_litros:.2f} litros (estimado)")
            
            # 4. Narrativa del viaje
            print("\n--- NARRATIVA DEL VIAJE ---")
            for i, paso in enumerate(ruta['instructions']):
                dist_paso_km = paso['distance'] / 1000
                print(f"{i + 1}. {paso['text']} ({dist_paso_km:.2f} km)")
            
            print("\n" + "="*40 + "\n")
        else:
            print("No se pudo calcular la ruta. Verifique las ciudades e intente de nuevo.")
            if ruta_info and 'message' in ruta_info:
                print(f"Mensaje de la API: {ruta_info['message']}")


    print("Programa finalizado. ¡Buen viaje!")

if __name__ == "__main__":
    main()
