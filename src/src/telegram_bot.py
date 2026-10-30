from loguru import logger

class TelegramNotifier:
    def __init__(self, token: str):
        self.token = token

    def send_message(self, chat_id: str, text: str):
        logger.info(f"Отправка сообщения в чат {chat_id}")
