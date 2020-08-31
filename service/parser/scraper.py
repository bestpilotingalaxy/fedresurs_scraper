import json

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .config.config import HEADERS

# Заголовки необходимые для запросов
headers = HEADERS

gecodriver_path = '/parser/service/WebDriver/geckodriver'


def set_driver_options():
    """
    headless параметр для драйвера
    """
    options = Options()
    options.headless = True
    return options


def collect_guids(keyword):
    """
    Функция для сбора guid листа фирм банкротов
    """
    url = 'https://fedresurs.ru/backend/companies/search'

    # Параметры фильтра, влияющие на подбор юр.лиц
    json_body = {
        "entitySearchFilter": {
            "pageSize": 99999,
            "name": keyword,
        },
        'onlyActive': False,
        'isCompany': False,
        # Является ли фирма банкротом
        'isFirmBankrupt': True,

    }
    response = requests.post(url=url, headers=headers,  json=json_body)
    companies = response.json()['pageData']

    # Создание списка guid значений юр.лиц
    guid_list = [i['guid'] for i in companies]

    return guid_list


def collect_bankrupts_messages(guid_list):
    """
    Функция находит последнее по дате решение арбитражного суда
    о банкротстве для каждого юр.лица из списка [guid_list],
    если такое решение пристуствует
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
            # Параметр влияет на подкатегорию банкротских сообщений
            # "ArbitralDecree" - решения арбитражного суда
            'bankruptMessageType': 'ArbitralDecree',
        }

        response = requests.post(url, headers=headers, json=json_body)
        publications = json.loads(response.content)

        try:
            message = publications['pageData'][0]
            messages.append(message)
        # IndexError возникает если нет решения суда о банкротстве
        except IndexError:
            pass

    return messages


def parse_messages_data(keyword):
    """
    Главная функция, последовательно вызывает две предыдущих,
    итерируется по списку сообщений парся текст сообщения с помощью
    веб-драйвера
    """
    bankrupts_guids = collect_guids(keyword)
    messages = collect_bankrupts_messages(bankrupts_guids)
    result = []

    # Обьект драйвера
    driver = webdriver.Firefox(
        executable_path=gecodriver_path,
        options=set_driver_options()
    )
    for message in messages:
        guid = message['guid']
        url = f'https://bankrot.fedresurs.ru/MessageWindow.aspx?ID={guid}'

        # Получение страницы + редирект
        driver.get(url)
        driver.refresh()

        # Парсинг текста сообщения и сбор других данных
        text = driver.find_element_by_class_name('msg').text
        text = text.replace('\n', '')

        # Формирование обьекта результата парсинга
        data_object = {
            'guid': guid,
            'text': text,
            'date': message['datePublish'],
            'url': url
            }
        result.append(data_object)

    # Проверка на пустой результат
    if len(result) == 0:
        return 'No messages found'

    return result
