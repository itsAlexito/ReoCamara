import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(".env")
load_dotenv(".env.chats")

# Configuración de la cámara y bot
CAMERA_IP = os.getenv("CAMERA_IP")
USER = os.getenv("USERBOT")
PASSWORD = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
RTSP_URL = f"rtsp://{USER}:{PASSWORD}@{CAMERA_IP}:{PORT}/h264Preview_01_main"
BOT_TOKEN = os.getenv("TOKEN")

# Chat permitidos
ALLOWED_CHAT_IDS = [int(chat_id) for chat_id in os.getenv("ALLOWED_CHATS").split(",")]
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))  # Grupo donde se enviarán los mensajes

# Usuarios autorizados para ciertas acciones
GODMODE = [int(user_id) for user_id in os.getenv("GODMODE").split(",")]


# Rutas de movimiento de cámara (presets)
ROUTES = {
    "getsalseo": [0, 1, 0],
    "getnevera": [0, 2, 0],
    # Puedes agregar más rutas aquí
}

# Comandos disponibles y sus descripciones
COMMANDS_DESCRIPTIONS = {
    "getsalseo": "Video del club en general.",
    "getnevera": "Video que apunta a la nevera.",
    "getimage": "Imagen del punto que esté mirando la cámara.",
    "getvideo": "Video del punto que esté mirando la cámara.",
}

# Tiempo de vida de los mensajes (segundos)
MESSAGE_LIFETIME = 40
