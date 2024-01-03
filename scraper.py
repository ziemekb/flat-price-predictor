from bs4 import BeautifulSoup
import argparse
import json
import requests
import re
import csv
import pandas as pd
from math import inf

BASE_URL = "https://www.otodom.pl"
LISTINGS_URL = BASE_URL + "/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw"

PROPERTIES=['area', 'price', 'district', 'rent', 'market', 'garage', 'balcony']
# returns pandas Series with default columns price, metric area 
# and parameters specified in args
def retrieve_listing_data(url, properties):
    listing = requests.get(url)
    listing_soup = BeautifulSoup(listing.content, "html.parser")
    
    #top_info = listing_soup.find("div", attrs={"data-testid" : "ad.top-information.table"})
    script_tag = listing_soup.find('script', {'id': '__NEXT_DATA__'})
    json_data = script_tag.contents[0] if script_tag else None

    if json_data:
        try:
            data = json.loads(json_data)
            props = data.get('props', {})
            # extract page properties
            page_props = props.get('pageProps', {})
            # extract ad id
            ad_id = page_props.get('id')
            ad_data = page_props.get('ad', {})
            # extract ad description
            ad_description = ad_data.get('description')
            
            # extract 'target'; fields which interest us the most
            target = ad_data.get('target')
            
            area = float(target.get('Area', 0))
            #build_year = int(target.get('Build_year', 0)) 
            #floors_num = int(target.get('Building_floors_num', 0))
            #floor_num = target.get('Floor_no') # keep in mind strange formating e.g. ["floor_5"]
            price = target.get('Price', 0)
            rent = target.get('Rent', 0)

            print(f"ID: {ad_id}")
            #print(f"Description: {ad_description}")
            print(f"Area: {area}")
            print(f"Price: {price}")
            print(f"Rent: {rent}")

            characteristics = ad_data.get('characteristics')
            market = None # secondary or primary -- wtórny lub pierwotny
            for c in characteristics:
                if c.get('key', None) == "market":
                    market = c.get('value', None)
                    break

            print(f"Market: {market}")
            location = ad_data.get('location')
            coords = location.get('coordinates')

            latitude = coords.get('latitude', 0.0)
            longitude = coords.get('longitude', 0.0)
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print("Script tag with id='__NEXT_DATA__' not found.")

    return None

def get_max_page(listings_url):
    page = requests.get(listings_url)
    soup = BeautifulSoup(page.content, "html.parser")

    pages_soup = soup.find("nav", attrs={"data-cy" : "pagination", "role" : "navigation"})
    pages_soup = pages_soup.find_all("a", attrs={"data-cy" : re.compile("pagination.go-to-page*")})

    return max(int(page_num.text) for page_num in pages_soup)


def scrape_otodom(properties=None, listings_mx=None):

    if not properties:
        properties=PROPERTIES[:2]
    else:
        properties = sorted(properties, key=lambda x: PROPERTIES.index(x))
    if not listings_mx:
        listings_mx = inf
    
    visited_listings = set()
    lcounter = 0

    with open(r"listings.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow([p.capitalize() for p in properties])
        max_page = get_max_page(LISTINGS_URL)
        for page_num in range(1, max_page + 1):
            page = requests.get(LISTINGS_URL + "?page=" + str(page_num))
            page_soup = BeautifulSoup(page.content, "html.parser")
            a_tags = page_soup.find_all("a", href=True, attrs={"data-cy" : "listing-item-link"})
            for tag in a_tags:
                link = tag["href"]
                if link in visited_listings:
                    continue
                visited_listings.add(link)
                data = retrieve_listing_data(BASE_URL + link, properties) 
                if not data:
                    continue
                lcounter += 1
                writer.writerow(data)
                # here write data to csv file
                if lcounter > listings_mx:
                    return None 
            input()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrapes otodom website for flat listings")
    parser.add_argument('-p', '--properties', nargs='+', choices=PROPERTIES, 
                        help='allows choosing which properties to scrape')
    parser.add_argument('-l', '--listings', type=int,
                        help='allows specifying how many listing to scrapes')
    args = parser.parse_args()
    scrape_otodom(args.properties, args.listings)


