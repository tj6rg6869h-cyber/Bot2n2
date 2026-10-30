import asyncio
from loguru import logger
from src.twogis_scraper import TwoGISB2BScraper
from src.telegram_bot import TelegramNotifier
from src.excel_exporter import save_leads_to_excel
from config.settings import ALL_TARGET_CITIES

TG_TOKEN = "9204934102:AAFipw0oLNI4Bc7t--b8t4qtp_4I2ersrVQ"
TG_CHAT_ID = "-1003718021277"
PROXY_URL = "http://127.0.0.1:10809"

async def main():
    logger.info("🚀 Запуск тотального сбора B2B базы по всей России (Оренбург исключен)...")
    
    scraper = TwoGISB2BScraper(proxy=PROXY_URL)
    notifier = TelegramNotifier(token=TG_TOKEN, chat_id=TG_CHAT_ID)
    
    all_leads = []
    
    for city in ALL_TARGET_CITIES:
        logger.info(f"Прочесываем город: {city}")
        leads = await scraper.scrape_city(city)
        if leads:
            all_leads.extend(leads)
        await asyncio.sleep(0.3)
    
    # Сохраняем ВСЮ общую базу в один элитный файл
    filename = "vape_leads_all_russia.xlsx"
    excel_path = save_leads_to_excel(all_leads, filename=filename)
    
    # Отправляем итоговый документ в Telegram
    caption = (
        f"🔥 <b>ТОТАЛЬНЫЙ B2B ОТЧЕТ ПО РФ</b>\n"
        f"🚫 <i>Оренбург и область полностью исключены</i>\n"
        f"📊 <b>Всего собрано уникальных точек:</b> {len(all_leads)}\n"
        f"⚡️ <i>Топ-города выделены на самом верху таблицы</i>"
    )
    await notifier.send_document(excel_path, caption=caption)
    
    logger.info("🎉 Полный цикл сбора, оформления и отправки завершен успешно!")

if __name__ == "__main__":
    asyncio.run(main())
