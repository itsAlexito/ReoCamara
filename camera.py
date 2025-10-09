import time
import requests
import asyncio
from config import CAMERA_IP, USER, PASSWORD, RTSP_URL

# Variables globales para el token
_cached_token = None
_token_expiry = 0


# Obtiene y cachea el token de la cámara
def get_token():
    global _cached_token, _token_expiry
    if _cached_token and time.time() < _token_expiry:
        print(f"🔹 Usando token cacheado: {_cached_token}")
        return _cached_token

    url = f"http://{CAMERA_IP}/api.cgi?cmd=Login"
    payload = [{
        "cmd": "Login",
        "param": {"User": {"userName": USER, "password": PASSWORD}}
    }]

    try:
        print(f"🟡 Solicitando token a {url} con payload {payload}")
        response = requests.post(url, json=payload, verify=False)
        print(f"🔹 Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"🔹 Respuesta JSON: {data}")

            if data and isinstance(data, list) and "value" in data[0] and "Token" in data[0]["value"]:
                _cached_token = data[0]["value"]["Token"]["name"]
                _token_expiry = time.time() + 60 * 5  # Token válido por 5 minutos
                print(f"✅ Token obtenido: {_cached_token}")
                return _cached_token
            else:
                print("🔴 Error: Respuesta no contiene token válido")
        else:
            print(f"🔴 Error: Código de estado inesperado {response.status_code}")

    except requests.RequestException as e:
        print(f"🔴 Excepción en la solicitud: {e}")

    return None

# Mueve la cámara a un preset específico
# El preset es configurado desde la aplicación de la cámara	o desde el propio navegador
# speed es la velocidad a la que se mueve la cámara

def move_camera(token, preset_id, speed=2):
    print(f"🔹 Moviendo cámara al preset {preset_id} con velocidad {speed}")
    url = f"http://{CAMERA_IP}/api.cgi?cmd=PtzCtrl&token={token}"
    payload = [{
        "cmd": "PtzCtrl", 
        "param": {"channel": 0, "op": "ToPos", "id": preset_id, "speed": speed}
    }]
    try:
        requests.post(url, json=payload, verify=False)
    except requests.RequestException:
        pass


# Graba un video de la cámara por un tiempo determinado
async def record_video(output_file, duration):
    try:
        command = [
            "ffmpeg", "-y", "-i", RTSP_URL,
            "-t", str(duration), "-vf", "scale=640:360",
            "-preset", "ultrafast", "-c:v", "libx264", output_file
        ]
        process = await asyncio.create_subprocess_exec(*command)
        await process.wait()
    except Exception:
        pass

# Ejecuta una ruta de movimiento de cámara
async def execute_route(route, output_file):
    token = get_token()
    if not token:
        return

    duration_per_movement = 5
    total_duration = duration_per_movement * len(route)

    # Iniciar grabación en paralelo
    # Se graba en paralelo para aumentar la eficiencia
    record_task = asyncio.create_task(record_video(output_file, total_duration))

    for preset in route:
        move_camera(token, preset)
        await asyncio.sleep(duration_per_movement)

    await record_task  # Espera a que la grabación finalice
