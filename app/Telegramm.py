import os
import requests


class TelegramBot:
    """
    Класс TelegramBot используется для отправки сообщений в Telegram чат.

    Attributes:
    -----------
    token : str
        Токен вашего бота в Telegram.
    chat_id : str
        ID чата, в который вы хотите отправлять сообщения.

    Methods:
    --------
    send_message(text: str, parse_mode: str = "Markdown") -> None
        Отправляет текстовое сообщение в чат Telegram.
    """

    def __init__(self, token=None, chat_id=None):
        """
        Инициализирует объект TelegramBot с заданными или предопределенными токеном и chat_id.

        Parameters:
        -----------
        token : str, optional
            Токен вашего бота в Telegram. По умолчанию None.
        chat_id : str, optional
            ID чата, в который вы хотите отправлять сообщения. По умолчанию None.
        """
        self.token = token or os.environ.get('TELEGRAM_TOKEN')
        self.chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID')

        if self.token is None or self.chat_id is None:
            print(
                "WARNING: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID environment variable is missing. Cannot send messages to Telegram.")

    def send_message(self, text, parse_mode="Markdown"):
        """
        Отправляет текстовое сообщение в чат Telegram.

        Parameters:
        -----------
        text : str
            Текст сообщения для отправки.
        parse_mode : str, optional
            Форматирование текста сообщения, по умолчанию "Markdown".
        """
        # Валидация текста
        if not isinstance(text, str) or not text.strip():
            print("Ошибка: текст сообщения не может быть пустым или None")
            return

        try:
            url_req = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url_req, data=payload)

            if response.status_code == 200:
                print("Сообщение успешно отправлено в Telegram.")
            else:
                print(f"Ошибка при отправке сообщения в Telegram. Код состояния: {response.status_code}")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
