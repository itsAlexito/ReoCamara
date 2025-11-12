import datetime
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from config import BOT_TOKEN, ALLOWED_CHAT_IDS, GODMODE
from handlers import start_route, unknown_command, get_image, get_video, not_allowed_reply, forward_message
from stats_job import stats_command, stats_job
from stats_logger import log_command

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Filtros de permisos
    allowed_filter = filters.Chat(chat_id=ALLOWED_CHAT_IDS)
    
    #GODMODE filter
    godmode_filter = filters.User(user_id=GODMODE)
    
    # Bloquear comandos en chats no autorizados, excepto si el usuario está en GODMODE
    disallowed_filter = ~filters.Chat(chat_id=ALLOWED_CHAT_IDS) & ~godmode_filter


        # --- STATS JOB ---
    async def _stats_wrapper(context: ContextTypes.DEFAULT_TYPE):
        await stats_job(application)

    try:
        local_tz = datetime.datetime.now().astimezone().tzinfo
    except Exception:
        local_tz = None

    now = datetime.datetime.now().astimezone() if local_tz else datetime.datetime.now()
    try:
        if local_tz:
            today_target = datetime.datetime(now.year, now.month, now.day, 23, 59, tzinfo=local_tz)
        else:
            today_target = datetime.datetime(now.year, now.month, now.day, 23, 59)
    except Exception:
        today_target = datetime.datetime(now.year, now.month, now.day, 23, 59)

    if today_target <= now:
        first_run_stats = today_target + datetime.timedelta(days=1)
    else:
        first_run_stats = today_target

    job_queue = application.job_queue

    # run once immediately (when=0 runs the job asap) so stats are generated on first load
    job_queue.run_once(_stats_wrapper, when=0)
    # schedule the daily repeating job (first run at today's target time or tomorrow)
    job_queue.run_repeating(_stats_wrapper, interval=datetime.timedelta(days=1), first=first_run_stats)


    # Register command handlers from handlers.py
    async def log_all_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.text and update.message.text.startswith("/"):
            user = update.effective_user.full_name if update.effective_user else "Desconocido"
            cmd = update.message.text.split()[0]
            log_command(user, cmd)

    # Put the generic command logger in a later group so CommandHandlers run first
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^/"), log_all_commands), group=1)

    # Agregar handlers para comandos permitidos
    application.add_handler(CommandHandler("getsalseo", start_route, filters=allowed_filter | godmode_filter))
    application.add_handler(CommandHandler("getnevera", start_route, filters=allowed_filter | godmode_filter))
    application.add_handler(CommandHandler("getimage", get_image, filters=allowed_filter | godmode_filter))
    application.add_handler(CommandHandler("getvideo", get_video, filters=allowed_filter | godmode_filter))
    application.add_handler(CommandHandler("say", forward_message, filters=filters.ChatType.PRIVATE & godmode_filter))
    application.add_handler(CommandHandler("stats", stats_command, filters=allowed_filter | godmode_filter))

    # Manejar comandos de chats no permitidos (excepto GODMODE)
    application.add_handler(MessageHandler(filters.COMMAND & disallowed_filter, not_allowed_reply))

    # Para comandos no reconocidos en chats permitidos o por usuarios en GODMODE
    application.add_handler(MessageHandler(filters.COMMAND & (allowed_filter | godmode_filter), unknown_command))

    application.run_polling()

if __name__ == "__main__":
    main()
