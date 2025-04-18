import time
import random

import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0'
}

east_county = {'Santee': '17939', 'El Cajon': '5597', 'La Mesa': '10202', 'Poway': '15153', 'Lemon Grove': '10476', 'Lakeside': '23714', 'Spring Valley': '26127', 'Alpine': '21164', 'Jamul': '23506'}

redfin_url = 'https://www.redfin.com/city/'

data = {'price': [], 'beds': [], 'baths': [], 'square_feet': [], 'address': [], 'city_and_zipcode_scrape': [], 'city': []}

def scrape_card(soup, city):
    home_cards = soup.select('.HomeCardsContainer')[0].find_all('div', 'bp-Homecard__Content')

    for card in home_cards:
        card_children = list(card.children)

        house_price = card_children[0].text # data

        house_stats = card_children[1].find_all('span')
        number_of_beds = house_stats[0].text # data
        number_of_baths = house_stats[1].text # data
        square_feet = house_stats[2].text # data

        house_address = card_children[2].text.split(',', 1) # data

        data['price'].append(house_price)
        data['beds'].append(number_of_beds)
        data['baths'].append(number_of_baths)
        data['square_feet'].append(square_feet)
        data['address'].append(house_address[0])
        data['city_and_zipcode_scrape'].append(house_address[1])
        data['city'].append(city)

print('Getting data...')
for city in east_county.keys():
    url = f'{redfin_url}{east_county[city]}/CA/{city}/filter/property-type=house/'

    req = requests.get(url, headers=headers)

    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')

        scrape_card(soup, city)

        # get number of pages at bottom of cards and loop through rest of house pages if number>1
        pages = soup.find_all('div', 'PageNumbers')

        if len(pages) > 0:
            pages = pages[0]
            time.sleep(1)
            for i in range(1, len(pages)+1):
                req = requests.get(f'{url}page-{i}', headers=headers)

                if req.status_code == 200:
                    soup = BeautifulSoup(req.content, 'html.parser')

                    scrape_card(soup, city)
                else:
                    print('error')

                time.sleep(random.randint(1, 4))
    else:
        print('error')

houses_df = pd.DataFrame(data)
houses_df.to_csv('EastCounty_House_Prices_scraped.csv', index=False)
print('Saved data to csv.')