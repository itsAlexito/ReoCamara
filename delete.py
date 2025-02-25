import os
import asyncio
from config import MESSAGE_LIFETIME
from telegram.ext import ContextTypes

# Envía un video y lo elimina después de un tiempo
async def send_video(chat_id, output_file, context: ContextTypes.DEFAULT_TYPE, reply_to_message_id: int = None):
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        info_message = await context.bot.send_message(
            chat_id=chat_id, 
            text=f"Este video se autodestruirá en {MESSAGE_LIFETIME} segundos."
        )
        with open(output_file, "rb") as video:
            video_message = await context.bot.send_video(chat_id=chat_id, video=video)
        await asyncio.sleep(MESSAGE_LIFETIME)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=video_message.message_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=info_message.message_id)
        except Exception:
            pass
    else:
        await context.bot.send_message(chat_id=chat_id, text="No se pudo grabar el video.")

# Envía una imagen y la elimina después de un tiempo
async def send_image(chat_id, image_file, context: ContextTypes.DEFAULT_TYPE, reply_to_message_id: int = None):
    if os.path.exists(image_file) and os.path.getsize(image_file) > 0:
        info_message = await context.bot.send_message(
            chat_id=chat_id, 
            text=f"Esta imagen se autodestruirá en {MESSAGE_LIFETIME} segundos."
        )
        with open(image_file, 'rb') as image:
            image_message = await context.bot.send_photo(chat_id=chat_id, photo=image)
        await asyncio.sleep(MESSAGE_LIFETIME)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=image_message.message_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=info_message.message_id)
            os.remove(image_file)
        except Exception:
            pass
    else:
        await context.bot.send_message(chat_id=chat_id, text="No se pudo obtener la imagen de la cámara.")
