from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from config import BOT_TOKEN, MY_CHAT_ID
from signals import analyze
from utils import format_signal
import asyncio

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]

async def start(update, context):
    await update.message.reply_text("Бот активен. Используй /signal для анализа.")

async def signal(update, context):
    await update.message.reply_text("Анализирую монеты...")
    for symbol in SYMBOLS:
        data = analyze(symbol)
        msg = format_signal(data)
        await update.message.reply_text(msg)

async def send_signals(app):
    for symbol in SYMBOLS:
        data = analyze(symbol)
        msg = format_signal(data)
        await app.bot.send_message(chat_id=MY_CHAT_ID, text=msg)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(send_signals(app)), 'interval', minutes=15)
    scheduler.start()

    print("Бот работает. Сигналы каждые 15 минут.")
    app.run_polling()

if __name__ == "__main__":
    main()
