import json

import scrapy

from ..items import BankruptItem


class MessageSpider(scrapy.Spider):
    """"""
    name = 'find_bankrupts'

    star_urls = ['https://fedresurs.ru/']

    def start_requests(self):
        """"""

        url = 'https://fedresurs.ru/backend/companies/search'
        json_req_body = {
            "entitySearchFilter": {
                "pageSize": 99999, "name": "РОМАШКА", "onlyActive": False
            },
            'onlyActive': False,
            'isCompany': False,
            'isFirmBankrupt': True,
            'isFirmTradeOrg': False,
            'isSro': False,
            'isSroTradePlace': False,
            'isTradePlace': False,
        }
        request = scrapy.Request(
            url=url,
            method='POST',
            body=json.dumps(json_req_body),
            callback=self.parse
        )

        yield request

    def parse(self, response, **kwargs):
        """"""

        url = 'https://fedresurs.ru/backend/companies/publications'
        data = json.loads(response.body)
        for company_data in data['pageData']:
            guid = company_data['guid']
            json_req_body = {
                'guid': guid,
                'searchAmReport': True,
                'searchFirmBankruptMessage': True,
                'searchSfactsMessage': True,
                'searchSroAmMessage': True,
                'searchTradeOrgMessage': True,
                'pageSize': 99999,
                # Изменение этого параметра влияет на подкатегорию банкротских сообщений
                'bankruptMessageType': 'ArbitralDecree',
            }
            request = scrapy.Request(
                url=url,
                method='POST',
                body=json.dumps(json_req_body),
                callback=self.parse_message_link
            )
            yield request

    def parse_message_link(self, response):
        """"""
        item = BankruptItem
        data = json.loads(response.body)
        last_message = data['pageData'][0]
        guid = last_message['guid']
        url = f'https://bankrot.fedresurs.ru/MessageWindow.aspx?ID={guid}'

        item['guid'] = guid
        item['publish_date'] = last_message['datePublish']
        item['url'] = url

        request = scrapy.Request(
            url=url, meta={'item': item},
            callback=self.parse_message
        )
        yield request

    def parse_message(self, response):
        """"""
        item = response.meta['item']
        # !!!
        text_selector = 'div.msg ::text'
        text = response.css(text_selector).get()
        item['text'] = text

        yield item
