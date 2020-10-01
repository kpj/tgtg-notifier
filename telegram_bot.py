"""
How to obtain an API token: https://core.telegram.org/bots#6-botfather
Get chat id: https://stackoverflow.com/a/32572159/1474740
Get bot updates: https://api.telegram.org/bot<YourBOTToken>/getUpdates
"""


import telegram


class TelegramBot:
    def __init__(self, chat_id, api_token):
        self.chat_id = chat_id
        self._bot = telegram.Bot(token=api_token)

    def announce(self, msg):
        self._bot.send_message(self.chat_id, msg)

