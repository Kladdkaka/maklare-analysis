import scrapy


class BjurforsSpider(scrapy.Spider):
    name = "bjurfors"

    def start_requests(self):
        urls = [
            "https://www.bjurfors.se/sv/tillsalu/vastra-gotaland/goteborg/?type=Apartment"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_search_results)
        
    def parse_search_results(self, response):
        for link in response.css(".c-object-card__link"):
            yield response.follow(link, self.parse_listing)
            
        print(response.css(".c-pagination__next"))
        if response.css(".c-pagination__next"):
            next_page = response.css(".c-pagination__next > a")[0].attrib["href"]
            yield response.follow(next_page, self.parse_search_results)
    
    def parse_listing(self, response):
        for link in response.css("#dokument a.c-link"):
            url = link.attrib["href"]
            url = response.urljoin(url)
            name = link.css(".c-link__text::text").get().strip()
            # name is looking like Energideklaration (PDF, 207 kB), remove the size and type
            name = name.split("(")[0].strip()
            yield {
                "document_name": name,
                "document_url": url
            }