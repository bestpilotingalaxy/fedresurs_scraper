import json

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .config.config import HEADERS

# Headers necessary for requests
headers = HEADERS

gecodriver_path = '/parser/service/WebDriver/geckodriver'


def set_driver_options():
    """
    Headless option for webdriver.
    """
    options = Options()
    options.headless = True
    return options


def collect_guids(keyword):
    """
    Method collects guids of bankrupt companies.
    """
    url = 'https://fedresurs.ru/backend/companies/search'

    # Params to filter bankrupts
    json_body = {
        "entitySearchFilter": {
            "pageSize": 99999,
            "name": keyword,
        },
        'onlyActive': False,
        'isCompany': False,
        # Main bankrupt parameter
        'isFirmBankrupt': True,

    }
    response = requests.post(url=url, headers=headers,  json=json_body)
    companies = response.json()['pageData']

    # Make guid list of bankrupts
    guid_list = [i['guid'] for i in companies]

    return guid_list


def collect_bankrupts_messages(guid_list):
    """
    Method find latest court's decision for every company in 
    [guid_list] if such decision exist.
    """
    url = 'https://fedresurs.ru/backend/companies/publications'

    messages = []
    for guid in guid_list:
        json_body = {
            'guid': guid,
            'searchAmReport': False,
            'searchFirmBankruptMessage': True,
            'searchSfactsMessage': False,
            'searchSroAmMessage': False,
            'searchTradeOrgMessage': False,
            'pageSize': 99999,
            # This param affects on messages categories
            # "ArbitralDecree" - filter only court's decisions
            'bankruptMessageType': 'ArbitralDecree',
        }

        response = requests.post(url, headers=headers, json=json_body)
        publications = json.loads(response.content)

        try:
            message = publications['pageData'][0]
            messages.append(message)
        # IndexError raise if 
        except IndexError:
            pass

    return messages


def parse_messages_data(keyword):
    """
    Main funk, successively calls other funks, iterates over messages
    and gets required information.
    """
    bankrupts_guids = collect_guids(keyword)
    messages = collect_bankrupts_messages(bankrupts_guids)
    result = []

    # Driver object
    driver = webdriver.Firefox(
        executable_path=gecodriver_path,
        options=set_driver_options()
    )
    for message in messages:
        guid = message['guid']
        url = f'https://bankrot.fedresurs.ru/MessageWindow.aspx?ID={guid}'

        # Handle no-response situations
        try:
            # get page + redirect
            driver.get(url)
            driver.refresh()

            # Message text parsing and collecting other data
            text = driver.find_element_by_class_name('msg').text
            text = text.replace('\n', '')
        except Exception:
            continue

        # Result object for every message
        data_object = {
            'guid': guid,
            'text': text,
            'date': message['datePublish'],
            'url': url
            }
        result.append(data_object)

    # Checks for empty list
    if len(result) == 0:
        return 'No messages found'

    return result
