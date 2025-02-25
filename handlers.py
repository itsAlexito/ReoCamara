import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import CAMERA_IP, ROUTES, COMMANDS_DESCRIPTIONS, MESSAGE_LIFETIME
from camera import get_token, record_video, execute_route
from delete import send_video, send_image

# Inicia la ejecución de una ruta de cámara según el comando recibido
async def start_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.split('@')[0].replace("/", "")
    if command in ROUTES:
        route = ROUTES[command]
        output_file = f"{command}.mp4"
        await execute_route(route, output_file)
        await send_video(update.effective_chat.id, output_file, context)
    else:
        await unknown_command(update, context)

# Respuesta para comandos no reconocidos
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in COMMANDS_DESCRIPTIONS.items()])
    error_message = (
        "Comando no reconocido. Por favor, utiliza uno de los siguientes comandos disponibles:\n\n"
        f"{commands_list}"
    )
    await update.message.reply_text(error_message)

# Obtiene una imagen de la cámara y la envía
async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = get_token()
    if not token:
        await update.message.reply_text("Error al obtener el token de la cámara.")
        return

    url = f"https://{CAMERA_IP}/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=flsYJfZgM6RTB_os&token={token}"
    image_file = "getImage.jpg"

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        with open(image_file, 'wb') as f:
            f.write(response.content)
    except requests.RequestException:
        await update.message.reply_text("Error al obtener la imagen de la cámara.")
        return

    await send_image(update.effective_chat.id, image_file, context)

# Obtiene un video de la cámara y lo envía
async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output_file = "getVideo.mp4"
    duration = 10

    try:
        await record_video(output_file, duration)
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            await update.message.reply_text("No se pudo grabar el video.")
            return
        await send_video(update.effective_chat.id, output_file, context)
    except Exception:
        await update.message.reply_text("Ocurrió un error al grabar el video.")

# Respuesta para chats que no están permitidos
async def not_allowed_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "No sé quién chuchas eres, si tienes algún problema contacta con el equipo de IT de eurielec."
    )
