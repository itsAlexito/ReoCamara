import time
import requests
import asyncio
from config import CAMERA_IP, USER, PASSWORD, RTSP_URL, TARGET_CHAT_ID
from delete import send_image

# Variables globales para el token
_cached_token = None
_token_expiry = 0


# Obtiene y cachea el token de la cámara
def get_token():
    """Obtiene y cachea el token de la cámara"""
    global _cached_token, _token_expiry
    if _cached_token and time.time() < _token_expiry:
        print(f"🔹 Usando token cacheado: {_cached_token}")  # 🔹 DEBUG
        return _cached_token

    print("🟡 Solicitando nuevo token...")  # 🔹 DEBUG
    url = f"http://{CAMERA_IP}/api.cgi?cmd=Login"
    payload = [{
        "cmd": "Login",
        "param": {"User": {"userName": USER, "password": PASSWORD}}
    }]

    try:
        response = requests.post(url, json=payload, verify=False)
        if response.status_code == 200:
            data = response.json()[0]
            if "value" in data and "Token" in data["value"]:
                _cached_token = data["value"]["Token"]["name"]
                _token_expiry = time.time() + data["value"]["Token"]["leaseTime"] - 10  # Restamos 10s para prevenir expiración
                print(f"✅ Nuevo token obtenido: {_cached_token}")  # 🔹 DEBUG
                return _cached_token
            else:
                print("🔴 Error: No se recibió un token válido")  # 🔹 DEBUG
        else:
            print(f"🔴 Error en la autenticación: {response.status_code}")  # 🔹 DEBUG
    except requests.RequestException as e:
        print(f"🔴 Excepción al obtener el token: {e}")  # 🔹 DEBUG

    return None  # Devuelve None si hay un fallo


# Mueve la cámara a un preset específico
# El preset es configurado desde la aplicación de la cámara	o desde el propio navegador
# speed es la velocidad a la que se mueve la cámara

def move_camera(token, preset_id, speed=1):
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

def set_Alarm_schedule (start_hour, end_hour):
    token = get_token()
    if not token:
        return False
    
    url = f"http://{CAMERA_IP}/api.cgi?cmd=SetMdAlarm&token={token}"
    payload = [{
        "cmd": "SetMdAlarm",
        "param": {
            "MdAlarm": {
                "channel": 0,
                "type": "md",
                "enable": 1,
                "sens": [
                    {
                        "beginHour": 9,
                        "beginMin": 0,
                        "endHour": 11,
                        "endMin": 0,
                        "sensitivity": 9
                    }
                ]   
            }
        }
    }]
    response = requests.post(url, json=payload, verify=False)
    return response.status_code == 200

#Monitor de movimiento en la cámara
async def monitor_motion(context):
    """Monitorea la detección de movimiento y envía alertas al grupo de Telegram con una imagen"""
    while True:
        token = get_token()
        if not token:
            print("🔴 No se pudo obtener un token válido.")  # 🔹 DEBUG
            await asyncio.sleep(10)
            continue
        
        url = f"http://{CAMERA_IP}/api.cgi?cmd=GetMdState&token={token}"
        try:
            response = requests.get(url, verify=False)
            data = response.json()[0]

            print(f"🟢 Respuesta de la cámara: {data}")  # 🔹 DEBUG

            # 📌 Si la API dice "please login first", forzamos la renovación del token
            if "error" in data and "rspCode" in data["error"] and data["error"]["rspCode"] == -6:
                print("🔴 Token inválido. Renovando...")  # 🔹 DEBUG
                global _cached_token
                _cached_token = None  # Borra el token cacheado para forzar login
                continue  # Vuelve a intentar en la próxima iteración

            if response.status_code == 200 and "value" in data and data["value"]["state"] == 1:
                print("🚨 ¡Movimiento detectado! Enviando alerta...")  # 🔹 DEBUG
                message = "🚨 ¡Movimiento detectado en la cámara! 🚨"
                await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
                
                # Capturar imagen y enviarla SIN borrarla
                await send_image(TARGET_CHAT_ID, "motion_detected.jpg", context, delete_after=False)
                
        except requests.RequestException as e:
            print(f"🔴 Error en la solicitud a la cámara: {e}")  # 🔹 DEBUG

        await asyncio.sleep(5)  # Verifica cada 5 segundos
