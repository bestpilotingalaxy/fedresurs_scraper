import json

import requests
from bs4 import BeautifulSoup

from .config import HEADERS


keyword = "РОМАШКА"

headers = HEADERS


def collect_guids(keyword, headers):
    """"""
    url = 'https://fedresurs.ru/backend/companies/search'
    guid_list = []
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

    resp = requests.post(url=url, headers=headers,  json=json_body)
    companies = resp.json()['pageData']
    # guid_list = tuple(i['guid'] for i in companies)
    for company_data in companies:
        guid = company_data['guid']
        guid_list.append(guid)
    return guid_list


def collect_bankrupts_messages(guid_list, headers):
    """"""
    url = 'https://fedresurs.ru/backend/companies/publications'

    message_guids = []
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
            message_guids.append(message['guid'])
        except IndexError:
            pass
    return message_guids


data = collect_guids(keyword, headers)
print(data, len(data), sep='\n')
message_guids = collect_bankrupts_messages(data, headers)
print(message_guids)


link = 'http://bankrot.fedresurs.ru/MessageWindow.aspx?ID=274C523EEF86FDBB20445E9620774983&attempt=1'
page = requests.get(url=link)
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())

# TODO: Извлечь из сообщения:
#           1. GUID
#           2. Текст сообщения
#           3. Дату публикации
#           4. URL
