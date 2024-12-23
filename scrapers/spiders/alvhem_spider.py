import scrapy
from scrapy.selector import Selector
import json


class AlvhemSpider(scrapy.Spider):
    name = "alvhem"

    def start_requests(self):
        urls = [
            'https://www.alvhem.com/wp-json/alvhem/v1/estates?count=0&number=100000&type=housingcooperative&status=for-sale'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_search_results)
    
    def parse_search_results(self, response):
        sel = Selector(text=json.loads(response.body))
        for link in sel.css('a.link-absolute'):
            yield response.follow(link, self.parse_listing)
    
    def parse_listing(self, response):
        for link in response.css('a.link-document'):
            url = link.attrib['href']
            url = response.urljoin(url)
            # get all text inside the a tag as name, combine it
            name = ''.join(link.css('::text').getall()).strip()
            yield {
                'document_name': name,
                'document_url': url
            }