import requests
from bs4 import BeautifulSoup
import re
import csv
import time

class StreetEasyScraper(): 
    results = []
    # developer tools -> network -> name=url -> request headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': '_gcl_au=1.1.1916908104.1653508835; _ga=GA1.2.1412812313.1653508835; _cc_id=3ab45dcc033a23615af701fe09fbaf7d; zjs_user_id=null; zg_anonymous_id="8d28abb4-9448-4ed8-b374-e279dfa9b225"; _actor=eyJpZCI6Im8zczIzQXNwN05NRitkMnQ1QXFKK1E9PSJ9--0ed896c538af8ff2741dbba91cd3174966055079; _se_t=536d4cc0-2dc8-4f05-99b2-988a81d7814f; _pxvid=f6c35dad-f1c8-11ec-84e1-4d4849796653; zjs_anonymous_id="536d4cc0-2dc8-4f05-99b2-988a81d7814f"; __gads=ID=cd1aad5016a699ef:T=1655860598:S=ALNI_MZPSfCP3Yc7vBjugiPVz4_iomDIQQ; ki_r=; KruxPixel=true; _gid=GA1.2.1605470631.1656354747; post_views=1; panoramaId_expiry=1657075579787; panoramaId=f61e0eed860097036a1f0e27b60f4945a7027fa039f7391d329199723062a46f; _uetsid=cf3f88d0f75511ec948f5108975040f9; _uetvid=2b79de20ac5611ecb0ff4b97fa7a171d',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers'
        }
    # default pages is 1
    max_page = 1
    
    def fetch(self, url):
        response = requests.get(url, headers=self.headers)
        print(response)
        return(response)

    # parses the first webpage to find the total number of pages to be scraped
    def parse_pagenum(self, response):
        content = BeautifulSoup(response, features="lxml")
        deck = content.find('ul', {'class': 'pagination-list-container'})
        page_nums = []
        for card in deck.select('li'): 
            if card.a is not None: 
                page = card.a.text if re.search("[0-9]", card.a.text) else 0
            else: 
                page = 0
            
            page_nums.append(page)
        self.max_page = max([int(item) for item in page_nums])
        print(self.max_page)
    
    # parses each page to pull type, beds, baths, url, etc. 
    def parse(self, response):
        content = BeautifulSoup(response, features="lxml")
        deck = content.find('ul', {'class': 'searchCardList'})

        for card in deck.select('li'):
            # type and neighborhood
            type_neighborhood = card.find('div', {'class': 'listingCard listingCard--rentalCard jsItem'}).span.text
            type = re.search("(.+) in", type_neighborhood).group(1) if re.search("(.+) in", type_neighborhood) else 'NA'
            neigh = re.search("in (.+) at", type_neighborhood).group(1) if re.search("in (.+) at", type_neighborhood) else 'NA'
            # address and url
            address_url = card.find('address', {'class': 'listingCard-addressLabel listingCard-upperShortLabel'}) 
            address = address_url.a.text if address_url else 'NA'
            url = address_url.a['href'] if address_url else 'NA'
            # price
            price = card.find('div', {'class': 'listingCardBottom-emphasis'}).span.text if card.find('div', {'class': 'listingCardBottom-emphasis'}) else 'NA'
            # lat/lon
            geo = card.find('div', {'class': 'listingCard listingCard--rentalCard jsItem'}).a['se:map:point'] if card.find('div', {'class': 'listingCard listingCard--rentalCard jsItem'}) else 'NA'
            # beds, baths, sqft
            beds_bath_sqft = card.find_all('div', {'class': 'listingDetailDefinitionsItem'})
            if len(beds_bath_sqft)==3:
                beds = beds_bath_sqft[0].find('span', {'class':'listingDetailDefinitionsText'}).text if beds_bath_sqft[0].find('span', {'class':'listingDetailDefinitionsText'}) else 'NA'
                baths = beds_bath_sqft[1].find('span', {'class':'listingDetailDefinitionsText'}).text if beds_bath_sqft[1].find('span', {'class':'listingDetailDefinitionsText'}) else 'NA'
                sqft = re.search("[0-9]+", beds_bath_sqft[2].find('span', {'class':'listingDetailDefinitionsText'}).text).group(0) if beds_bath_sqft[2].find('span', {'class':'listingDetailDefinitionsText'}) else 'NA'
            elif len(beds_bath_sqft)==2:
                beds = beds_bath_sqft[0].find('span', {'class':'listingDetailDefinitionsText'}).text if beds_bath_sqft[0].find('span', {'class':'listingDetailDefinitionsText'}) else 'NA'
                baths = beds_bath_sqft[1].find('span', {'class':'listingDetailDefinitionsText'}).text if beds_bath_sqft[1].find('span', {'class':'listingDetailDefinitionsText'}) else 'NA'
                sqft = 'NA'
            elif len(beds_bath_sqft)==1:
                beds = beds_bath_sqft[0].find('span', {'class':'listingDetailDefinitionsText'}).text if beds_bath_sqft[0].find('span', {'class':'listingDetailDefinitionsText'}) else 'NA'
                baths = 'NA', 
                sqft = 'NA'
            else:
                beds = 'NA'
                baths = 'NA'
                sqft = 'NA'

            # combine into dictionary
            self.results.append({
                    'type': type,
                    'neighborhood': neigh,
                    'address': address, 
                    'price': price,
                    'geo': geo,
                    'beds': beds, 
                    'baths': baths, 
                    'sqft': sqft,
                    'url': url
            })

    def to_csv(self):
        with open('data/streeteasy.csv', 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
            writer.writeheader()

            for row in self.results:
                writer.writerow(row)

    def run(self):
        url = 'https://streeteasy.com/for-rent/nyc/price:-2400%7Carea:336,331,310,334,306,338,305,321,364,322,328,325,307,303,332,304,320,301,367,340,339,365,319,326,329,355,318,323,302,324,102,119,139,135,155,148,147,165,149,153,401,416,415,424,420,402,411,414,403,404%7Cbeds%3C=1%7Camenities:laundry?page=1'
        res = self.fetch(url)
        self.parse_pagenum(res.text)
        time.sleep(3)

        for page in range(1,self.max_page + 1):
            url = f'https://streeteasy.com/for-rent/nyc/price:-2400%7Carea:336,331,310,334,306,338,305,321,364,322,328,325,307,303,332,304,320,301,367,340,339,365,319,326,329,355,318,323,302,324,102,119,139,135,155,148,147,165,149,153,401,416,415,424,420,402,411,414,403,404%7Cbeds%3C=1%7Camenities:laundry?page={page}'
            res = self.fetch(url)
            self.parse(res.text)
            time.sleep(3)
        self.to_csv()


    
if __name__ == '__main__':
    scraper = StreetEasyScraper()
    scraper.run()