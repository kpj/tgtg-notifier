import time
import random

import yaml

from tgtg_client import TGTGClient


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

    while True:
        for item_id in config['item_list']:
            item = client.get_item(str(item_id))

            if item['items_available'] > 0:
                print(f'Check out "{item["display_name"]}"')

            time.sleep(random.random())

        print(f'--- waiting {config["interval"]}s ---')
        time.sleep(config['interval'])  # this will drift


if __name__ == '__main__':
    main()
