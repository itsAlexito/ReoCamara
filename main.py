from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, ALLOWED_CHAT_IDS
from handlers import start_route, unknown_command, get_image, get_video, not_allowed_reply, forward_message

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    allowed_filter = filters.Chat(chat_id=ALLOWED_CHAT_IDS)
    disallowed_filter = ~allowed_filter

    # Agregar handlers para comandos permitidos
    application.add_handler(CommandHandler("getsalseo", start_route, filters=allowed_filter))
    application.add_handler(CommandHandler("getnevera", start_route, filters=allowed_filter))
    application.add_handler(CommandHandler("getimage", get_image, filters=allowed_filter))
    application.add_handler(CommandHandler("getvideo", get_video, filters=allowed_filter))
    application.add_handler(CommandHandler("forward", forward_message, filters=allowed_filter.ChatType.is_private))

    # Manejar comandos de chats no permitidos
    application.add_handler(MessageHandler(filters.COMMAND & disallowed_filter, not_allowed_reply))
    # Para comandos no reconocidos en chats permitidos
    application.add_handler(MessageHandler(filters.COMMAND & allowed_filter, unknown_command))

    application.run_polling()

if __name__ == "__main__":
    main()
