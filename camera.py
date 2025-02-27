import time
import requests
import asyncio
from config import CAMERA_IP, USER, PASSWORD, RTSP_URL, TARGET_CHAT_ID
from handlers import send_image

# Variables globales para el token
_cached_token = None
_token_expiry = 0


# Obtiene y cachea el token de la cámara
def get_token():
    global _cached_token, _token_expiry
    if _cached_token and time.time() < _token_expiry:
        return _cached_token

    url = f"http://{CAMERA_IP}/api.cgi?cmd=Login"
    payload = [{
        "cmd": "Login", 
        "param": {"User": {"userName": USER, "password": PASSWORD}}
    }]
    try:
        response = requests.post(url, json=payload, verify=False)
        if response.status_code == 200:
            _cached_token = response.json()[0]["value"]["Token"]["name"]
            _token_expiry = time.time() + 60 * 5  # Token válido por 5 minutos
            return _cached_token
    except requests.RequestException:
        pass

    return None

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
                        "endHour": 10,
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
            await asyncio.sleep(10)
            continue
        
        url = f"http://{CAMERA_IP}/api.cgi?cmd=GetMdState&token={token}"
        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200 and response.json()[0]["value"]["state"] == 1:
                message = "🚨 ¡Movimiento detectado en la cámara! 🚨"
                await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
                
                # Capturar imagen y enviarla SIN borrarla (delete_after=False)
                await send_image(TARGET_CHAT_ID, "motion_detected.jpg", context, delete_after=False)
                
        except requests.RequestException:
            pass

        await asyncio.sleep(5)  # Verifica cada 5 segundos
