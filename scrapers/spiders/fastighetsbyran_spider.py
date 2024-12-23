import scrapy
import json

# search api is https://www.fastighetsbyran.com/HemsidanAPI/api/v1/soek/objekt/1/false/
# request body is {"valdaMaeklarObjektTyper":[],"valdaNyckelord":[],"valdaLaen":[],"valdaKontor":[],"valdaKommuner":[],"valdaNaeromraaden":[],"valdaPostorter":[],"inkluderaNyproduktion":true,"inkluderaPaaGaang":true,"positioner":[]}
# response body is like
# {
#     "results": [
#         {
#             "maeklarObjektId": 2315402,
#             "bildUrl": "https://media.fastighetsbyran.se/44720249.jpg",
#             "bildUrlLista": [
#                 "https://media.fastighetsbyran.se/44720249.jpg",
#                 "https://media.fastighetsbyran.se/44720245.jpg",
#                 "https://media.fastighetsbyran.se/44720247.jpg",
#                 "https://media.fastighetsbyran.se/44720251.jpg",
#                 "https://media.fastighetsbyran.se/44720252.jpg"
#             ],
#             "litenRubrik": "Tuve",
#             "storRubrik": "Brunnehagen 63",
#             "metaData": [
#                 "",
#                 "5 rum",
#                 "118/0 kvm"
#             ],
#             "xKoordinat": 57.7479777495,
#             "yKoordinat": 11.9258718166,
#             "paaGang": true,
#             "budgivningPagaar": false,
#             "aerNyproduktion": false,
#             "aerProjekt": false,
#             "aerReferensobjekt": false,
#             "harDigitalLiveVisning": false,
#             "maeklarId": 7329220,
#             "avtalsdag": null,
#             "senasteTidObjektetBlevTillSalu": null,
#             "senasteTidpunktSomObjektetBlevIntagetOchSkallAnnoserasFastStatusBaraIntaget": "2024-12-23T08:57:40.51",
#             "bostadsTyp": "Villa",
#             "boendeform": 2,
#             "delomraaden": [
#                 1609
#             ],
#             "tidFoerNaestaAktuellaVisning": null,
#             "naestaVisningAerDigitalLiveVisning": false,
#             "url": "https://www.fastighetsbyran.com/sv/sverige/till-salu/vastra-gotalands-lan/goteborgs-stad/objekt/?objektID=2315402"
#         }
#     ],
#     "currentPage": 3,
#     "pageCount": 441,
#     "pageSize": 50,
#     "rowCount": 22017
# }

# paging is in url, like https://www.fastighetsbyran.com/HemsidanAPI/api/v1/soek/objekt/3/false/


def make_search_request_body():
    return json.dumps(
        {
            "valdaMaeklarObjektTyper": [2],
            "valdaNyckelord": [],
            "valdaLaen": [],
            "valdaKontor": [],
            "valdaKommuner": ["454"],
            "valdaNaeromraaden": [],
            "valdaPostorter": [],
            "inkluderaNyproduktion": True,
            "inkluderaPaaGaang": True,
            "positioner": [],
        }
    )


class FastighetsbyranSpider(scrapy.Spider):
    name = "fastighetsbyran"

    def start_requests(self):
        urls = [
            "https://www.fastighetsbyran.com/HemsidanAPI/api/v1/soek/objekt/1/false/"
        ]

        for url in urls:
            # post, body

            yield scrapy.Request(
                url=url,
                method="POST",
                body=make_search_request_body(),
                callback=self.parse_search_results,
                headers={"Content-Type": "application/json"},
            )

    def parse_search_results(self, response):
        data = response.json()
        for result in data["results"]:
            yield response.follow(result["url"], self.parse_listing)

        if data["currentPage"] < data["pageCount"]:
            next_page = f"https://www.fastighetsbyran.com/HemsidanAPI/api/v1/soek/objekt/{data['currentPage']+1}/false/"
            yield response.follow(
                next_page,
                self.parse_search_results,
                method="POST",
                body=make_search_request_body(),
                headers={"Content-Type": "application/json"},
            )
    
    def parse_listing(self, response):
        # find span > h5 with text "Dokument", get parent of span, look all a in that parent
        for link in response.css('span > h5:contains("Dokument")').xpath('../../a'):
            url = link.attrib["href"]
            url = response.urljoin(url)
            name = link.css('.text-fb-brown-text::text').get().strip()
            yield {
                "document_name": name,
                "document_url": url
            }