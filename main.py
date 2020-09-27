import time
import random

from http import HTTPStatus
from urllib.parse import urljoin

import yaml
import requests
import pandas as pd


BASE_URL = 'https://apptoogoodtogo.com/'
LOGIN_ENDPOINT = '/api/auth/v1/loginByEmail'
ITEM_ENDPOINT = '/api/item/v6/'

USER_AGENTS = [
    'TGTG/20.9.1 Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus 5 Build/M4B30Z)',
    'TGTG/20.9.1 Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G935F Build/NRD90M)',
    'TGTG/20.9.1 Dalvik/2.1.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) ',
]


class TGTGClient():
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.access_token = None
        self.user_id = None

        self.user_agent = random.choice(USER_AGENTS)

    @property
    def login_url(self):
        return urljoin(BASE_URL, LOGIN_ENDPOINT)

    @property
    def item_url(self):
        return urljoin(BASE_URL, ITEM_ENDPOINT)

    @property
    def headers(self):
        """HTTP headers needed for each request."""
        headers = {
            'user-agent': self.user_agent,
            'accept-language': 'en-US'
        }

        if self.access_token is not None:
            headers['authorization'] = f'Bearer {self.access_token}'

        return headers

    def _login(self):
        """Sign in to obtain access token and user id."""
        if self.access_token is not None:
            print('Already logged in')
            return

        response = requests.post(
            self.login_url,
            headers=self.headers,
            json={
                'device_type': 'ANDROID',
                'email': self.email,
                'password': self.password
            }
        )

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'{response.status_code} -- {response.content}')

        resp_json = response.json()
        self.access_token = resp_json['access_token']
        self.user_id = resp_json['startup_data']['user']['user_id']

    def _convert_item(self, item):
        """Convert single item in JSON to CSV line."""
        cur = {
            'item_id': item['item']['item_id'],

            'display_name': item['display_name'],
            'distance': item['distance'],

            'item_category': item['item']['item_category'],
            'price': item['item']['price']['minor_units'],

            'items_available': item['items_available'],
            'in_sales_window': item['in_sales_window'],

            'address': item['pickup_location']['address']['address_line']
        }

        if cur['items_available'] > 0:
            cur['pickup_start'] = item['pickup_interval']['start']
            cur['pickup_end'] = item['pickup_interval']['end']

        return cur

    def get_item(self, item_id):
        """Get information about given item."""
        response = requests.post(
            urljoin(self.item_url, item_id),
            headers=self.headers,
            json={
                'user_id': self.user_id
            }
        )

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'{response.status_code} -- {response.content}')

        return self._convert_item(response.json())

    def get_items(self, latitude, longitude, page_size=400, radius=10):
        """Retrieve list of many items."""
        # request data
        response = requests.post(
            self.item_url,
            headers=self.headers,
            json={
                'user_id': self.user_id,
                'origin': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'page_size': page_size,
                'radius': radius,

                'diet_categories': [],
                'discover': False,
                'favorites_only': False,
                'hidden_only': False,
                'item_categories': [],
                'page': 1,
                'pickup_earliest': None,
                'pickup_latest': None,
                'search_phrase': None,
                'we_care_only': False,
                'with_stock_only': False
            }
        )

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'{response.status_code} -- {response.content}')

        # convert response to dataframe
        tmp = []
        for item in response.json()['items']:
            tmp.append(self._convert_item(item))

        df = pd.DataFrame(tmp)
        df.sort_values('items_available', ascending=False, inplace=True)
        df['pickup_start'] = pd.to_datetime(df['pickup_start'])
        df['pickup_end'] = pd.to_datetime(df['pickup_end'])

        return df


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
