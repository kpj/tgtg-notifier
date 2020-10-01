import time
import random
import textwrap

import yaml

from tgtg_client import TGTGClient
from telegram_bot import TelegramBot


def format_message(item):
    return textwrap.dedent(f"""
        New Offer ({item['items_available']} remaining):
            Name: {item['display_name']}
            Location: {item['address']}
            Time: {item['pickup_start']} - {item['pickup_end']}
    """)


def main():
    # load config
    with open('config.yaml') as fd:
        config = yaml.load(fd, Loader=yaml.FullLoader)

    # login
    client = TGTGClient(config['email'], config['password'])
    client._login()

    # df = client.get_items(latitude=None, longitude=None)
    # print(df.head())

    import IPython; IPython.embed()

    # setup telegram bot
    bot = TelegramBot(config['telegram_chat_id'], config['telegram_api_token'])

    # check for news
    while True:
        for item_id in config['item_list']:
            item = client.get_item(str(item_id))

            if item['items_available'] > 0:
                msg = format_message(item)

                print(msg)
                bot.announce(msg)

            time.sleep(random.random())

        print(f'--- waiting {config["interval"]}s ---')
        time.sleep(config['interval'])  # this will drift


if __name__ == '__main__':
    main()
