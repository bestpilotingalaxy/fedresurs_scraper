import json

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from config import HEADERS


headers = HEADERS

gecodriver_path = '/home/engi/PycharmProjects/fedresurs_scraper/WebDriver/geckodriver'


def set_driver_options():
    options = Options()
    options.headless = True
    return options


def collect_guids(keyword, headers):
    """"""
    url = 'https://fedresurs.ru/backend/companies/search'
    json_body = {
        "entitySearchFilter": {
            "pageSize": 99999,
            "name": keyword,
        },
        'onlyActive': False,
        'isCompany': False,
        'isFirmBankrupt': True,
        # не меняет кол во найденых юр.лиц в примере с РОМАШКА
        'isFirmTradeOrg': False,
        # не меняет кол во найденых юр.лиц в примере с РОМАШКА
        'isSro': False,
        # не меняет кол во найденых юр.лиц в примере с РОМАШКА
        'isSroTradePlace': False,
        # не меняет кол во найденых юр.лиц в примере с РОМАШКА
        'isTradePlace': False,
    }
    response = requests.post(url=url, headers=headers,  json=json_body)
    companies = response.json()['pageData']
    guid_list = [i['guid'] for i in companies]

    return guid_list


def collect_bankrupts_messages(guid_list, headers):
    """"""
    url = 'https://fedresurs.ru/backend/companies/publications'

    messages = []
    for guid in guid_list:
        params = {
            'guid': guid,
            'searchAmReport': False,
            'searchFirmBankruptMessage': True,
            'searchSfactsMessage': False,
            'searchSroAmMessage': False,
            'searchTradeOrgMessage': False,
            'pageSize': 99999,
            # Параметр влияет на подкатегорию банкротских сообщений
            'bankruptMessageType': 'ArbitralDecree',
        }

        publications = requests.post(url, headers=headers, json=params)
        publications = json.loads(publications.content)
        try:
            message = publications['pageData'][0]
            messages.append(message)
        except IndexError:
            pass

    return messages


def parse_messages_data(keyword):
    """"""
    bankrupts_guids = collect_guids(keyword, headers)
    messages = collect_bankrupts_messages(bankrupts_guids, headers)
    result = []
    driver = webdriver.Firefox(
        executable_path=gecodriver_path,
        options=set_driver_options()
    )
    for message in messages:
        guid = message['guid']
        url = f'https://bankrot.fedresurs.ru/MessageWindow.aspx?ID={guid}'
        driver.get(url)
        driver.refresh()
        text = driver.find_element_by_class_name('msg').text
        text = text.replace('\n', '')
        data_object = {
            'guid': guid,
            'text': text,
            'date': message['datePublish'],
            'url': url
            }
        result.append(data_object)

    return result


