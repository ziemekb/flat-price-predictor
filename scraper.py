from bs4 import BeautifulSoup
import argparse
import json
import requests
import re
import csv
import pandas as pd
from math import inf
from geoposition import classify_coords

BASE_URL = "https://www.otodom.pl"
LISTINGS_URL = BASE_URL + "/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw"

# all available properties of properties
PROPERTIES=['area', 'price', 'rent', 'district', 'latitude', 'longitude', 'market', 'build_year', 'garage', 'lift', 'basement', 'balcony', 'garden', 'terrace']

def retrieve_listing_data(url, properties):
    listing = requests.get(url)
    listing_soup = BeautifulSoup(listing.content, "html.parser")
    
    script_tag = listing_soup.find('script', {'id': '__NEXT_DATA__'})
    json_data = script_tag.contents[0] if script_tag else None

    if not json_data:
        print("Script tag with id='__NEXT_DATA__' not found.")
        return None

    try:
        props_dict = {p: None for p in properties}

        data = json.loads(json_data)
        props = data.get('props', {})
        # extract page properties
        page_props = props.get('pageProps', {})
        # extract ad id
        ad_id = page_props.get('id')
        ad_data = page_props.get('ad', {})
        # extract ad description
        # ad_description = ad_data.get('description')
        
        # extract 'target'; fields which interest us the most
        target = ad_data.get('target')
        
        props_dict['area'] = float(target.get('Area', None))
        floors_num = target.get('Building_floors_num', None)
        props_dict['floors_num'] = int(floors_num) if floors_num is not None else None 
        #props_dict['floor_num'] = target.get('Floor_no') 
        # keep in mind strange formating e.g. ["floor_5"]
        props_dict['price'] = target.get('Price', None)
        props_dict['rent'] = target.get('Rent', None)
        
        location = ad_data.get('location')

        # if the location is not accurate, reject the listing
        mapDetails = location.get('mapDetails')
        isInexact = mapDetails.get('radius', -1)
        if(isInexact != 0):
            return None

        coords = location.get('coordinates')

        latitude = coords.get('latitude', None)
        longitude = coords.get('longitude', None)
        props_dict['district'] = classify_coords(latitude, longitude)
        props_dict['latitude'] = latitude
        props_dict['longitude'] = longitude
        characteristics = ad_data.get('characteristics')
        market = None # secondary or primary -- wtórny lub pierwotny
        for c in characteristics:
            if c.get('key', None) == "market":
                props_dict['market'] = c.get('value', None)
                break
        
        # build year
        build_year = target.get('Build_year', None)
        props_dict['build_year'] = int(build_year) if build_year is not None else None 

        # constructions status: "ready_to_use", "to_completion", "to_renovation" or None
        # stan wykończenia odpowiednio: "do zamieszkania", "do wykończenia", "do remontu"
        construction_status = target.get('Construction_status', None)
        if construction_status:
            props_dict['construction_status'] = construction_status[0]

        # informacje dodatkowe
        extras = target.get('Extras_types', None)
        if extras:
            props_dict['garage']   = True if "garage" in extras else False
            props_dict['lift']     = True if "lift" in extras else False
            props_dict['basement'] = True if "basement" in extras else False
            props_dict['balcony']  = True if "balcony" in extras else False
            props_dict['garden']   = True if "garden" in extras else False
            props_dict['terrace']  = True if "terrace" in extras else False

        print(f"ID: {ad_id}")
        #print(f"Description: {ad_description}")
        print(f"Area: {props_dict['area']}")
        print(f"Price: {props_dict['price']}")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"District: {props_dict['district']}")
        print(f"Rent: {props_dict['rent']}")
        print(f"Market: {props_dict['market']}")
        
        if(props_dict['area'] is None or props_dict['price'] is None):
            return None
        data = [props_dict[p] for p in properties]

        #return data if all(data) else None
        return data
    except AttributeError as e:
        print(f"error when scraping JSON {e}")
        return None

    return None

def get_max_page(listings_url):
    page = requests.get(listings_url)
    soup = BeautifulSoup(page.content, "html.parser")

    pages_soup = soup.find("nav", attrs={"data-cy" : "pagination", "role" : "navigation"})
    pages_soup = pages_soup.find_all("a", attrs={"data-cy" : re.compile("pagination.go-to-page*")})

    return max(int(page_num.text) for page_num in pages_soup)


def scrape_otodom(properties=None, listings_mx=None):

    if not properties:
        properties=PROPERTIES
    else:
        properties = sorted(properties, key=lambda x: PROPERTIES.index(x))
    if not listings_mx:
        listings_mx = inf
    
    visited_listings = set()
    lcounter = 0

    with open(r"listings.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
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
                if lcounter >= listings_mx:
                    print("Reached the given limit")
                    return None 
        print("Reached the end of the listings")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrapes otodom website for flat listings")
    parser.add_argument('-p', '--properties', nargs='+', choices=PROPERTIES, 
                        help='allows choosing which properties to scrape')
    parser.add_argument('-l', '--listings', type=int, metavar = 'n',
                        help='allows specifying how many listing to scrapes')
    args = parser.parse_args()
    scrape_otodom(args.properties, args.listings)
