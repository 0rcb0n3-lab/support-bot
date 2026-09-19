import logging
from urllib.parse import urlencode
from urllib.request import urlopen


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot_token: str, chat_id: str):
        super().__init__()
        self.tg_bot_token = tg_bot_token
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        if len(log_entry) > 4000:
            log_entry = log_entry[:4000] + "\n ... (обрезано)"

        url = f"https://api.telegram.org/bot{self.tg_bot_token}/sendMessage"
        payload = urlencode(
            {
                "chat_id": self.chat_id,
                "text": log_entry,
            }
        ).encode()

        try:
            with urlopen(url, data=payload):
                pass
        except Exception:
            pass
