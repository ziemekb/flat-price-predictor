from bs4 import BeautifulSoup
import json
import requests
import re

BASE_URL = "https://www.otodom.pl"
LISTINGS_URL = BASE_URL + "/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw"

def retrieve_data(url):
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

page = requests.get(LISTINGS_URL)
soup = BeautifulSoup(page.content, "html.parser")

pages_soup = soup.find("nav", attrs={"data-cy" : "pagination", "role" : "navigation"})
pages_soup = pages_soup.find_all("a", attrs={"data-cy" : re.compile("pagination.go-to-page*")})

max_page = max(int(page_num.text) for page_num in pages_soup)

visited_listings = set()

for page_num in range(1, max_page + 1):
    page = requests.get(LISTINGS_URL + "?page=" + str(page_num))
    page_soup = BeautifulSoup(page.content, "html.parser")
    a_tags = page_soup.find_all("a", attrs={"data-cy" : "listing-item-link"})
    for tag in a_tags:
        link = tag["href"]
        if link not in visited_listings:
            visited_listings.add(link)
            retrieve_data(BASE_URL + link) 
    input()
