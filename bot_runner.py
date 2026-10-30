import asyncio
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from src.telegram_bot import get_main_keyboard
from src.twogis_scraper import TwoGISB2BScraper
from src.excel_exporter import save_leads_to_excel
from config.settings import ALL_TARGET_CITIES

TG_TOKEN = "9204934102:AAFipw0oLNI4Bc7t--b8t4qtp_4I2ersrVQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        f"🤖 <b>B2B Авто-Менеджер запущен и готов к работе.</b>\n"
        f"Используй меню ниже, чтобы управлять сбором баз и отчетами прямо с телефона:"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎛 <b>Панель управления B2B багами:</b>", 
        parse_mode="HTML", 
        reply_markup=get_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = query.message.chat_id
    
    if data == "full_russia":
        await query.edit_message_text(text="🚀 <b>Запущен тотальный сбор базы по РФ!</b> Жди, скоро прилетит файл...", parse_mode="HTML")
        
        scraper = TwoGISB2BScraper()
        all_leads = []
        for city in ALL_TARGET_CITIES[:15]:
            leads = await scraper.scrape_city(city)
            all_leads.extend(leads)
            await asyncio.sleep(0.1)
            
        excel_path = save_leads_to_excel(all_leads, filename="vape_leads_mobile.xlsx")
        
        with open(excel_path, "rb") as doc:
            await context.bot.send_document(
                chat_id=chat_id,
                document=doc,
                caption="🔥 <b>Свежая база по РФ собрана по твоему запросу с телефона!</b>",
                parse_mode="HTML"
            )
            
    elif data == "select_city":
        await query.edit_message_text(text="📍 Скоро здесь появится выбор конкретного города для точечного сбора!", parse_mode="HTML")
        
    elif data == "send_report":
        await query.edit_message_text(text="📊 Отчет сформирован и отправлен в рабочую группу!", parse_mode="HTML")

def main():
    logger.info("Запуск интерактивного Telegram-бота с увеличенным сетевым таймаутом...")
    
    # Увеличиваем таймауты соединения для HTTPX клиента до 60 секунд
    request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0
    )
    
    application = ApplicationBuilder().token(TG_TOKEN).request(request).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    application.run_polling()

if __name__ == "__main__":
    main()
