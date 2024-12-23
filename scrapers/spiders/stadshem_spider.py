import scrapy

class StadshemSpider(scrapy.Spider):
    name = "stadshem"

    def start_requests(self):
        urls = [
            'https://stadshem.se/till-salu/?typ=lagenhet&sortering=inkommet&riktning=fallande&kust=vastkusten'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_search_results)
    
    def parse_search_results(self, response):
        for link in response.css('.fasad-object-in-list > a'):
            yield response.follow(link, self.parse_listing)
    
    def parse_listing(self, response):
        for link in response.css('.documents > a.document'):
            url = link.attrib['href']
            name = link.css('.document-alias::text').get().strip()
            yield {
                'document_name': name,
                'document_url': url
            }