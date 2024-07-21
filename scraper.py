from bs4 import BeautifulSoup
import argparse
import json
import requests
import re
import csv
import random
from time import sleep
import pandas as pd
from math import inf
from geoposition import classify_coords

BASE_URL = "https://www.otodom.pl"
LISTINGS_URL = BASE_URL + "/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw"

# all available properties of properties
PROPERTIES=['area', 'price', 'market', 'rooms_num', 'rent', 'district', 'build_year', 'garage', 'lift', 'basement', 'balcony', 'garden', 'terrace', 'floors_num', 'floor_no', 'construction_status', 'latitude', 'longitude', 'link']
CSV_FILE_NAME = "temp.csv"

# properties are already sorted in the order of PROPERTIES
def retrieve_listing_data(url, properties):
    listing = requests.get(url)
    listing_soup = BeautifulSoup(listing.content, "html.parser")
    
    script_tag = listing_soup.find('script', {'id': '__NEXT_DATA__'})
    json_data = script_tag.contents[0] if script_tag else None

    if not json_data:
        print("Script tag with id='__NEXT_DATA__' not found.")
        print(f"URL: {url}")
        return None

    try:
        props_dict = {p: None for p in properties}
        props_dict['link'] = url

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
        
        props_dict['price'] = target.get('Price', None)
        area = target.get('Area', None)
        props_dict['area'] = float(area) if area is not None else None

        # number of rooms
        rooms_num = target.get('Rooms_num', None)
        props_dict['rooms_num'] = int(rooms_num[0]) if rooms_num is not None else None

        # number of floors in the building
        floors_num = target.get('Building_floors_num', None)
        props_dict['floors_num'] = int(floors_num) if floors_num is not None else None 

        # scraping floor number from descriptive, not numerical field 
        floor_str = target.get('Floor_no', None)
        floor_str = floor_str[0] if floor_str is not None else None
        floor_no = None

        if floor_str is None:
            floor_no = None
        elif floor_str == "ground_floor":
            floor_no = 0
        elif floor_str == "floor_higher_10":
            floor_no = 11
        else:
            prefix = "floor_"
            if floor_str.startswith(prefix):
                try:
                    floor_no = int(floor_str[len(prefix):])
                except ValueError:
                    return None

        props_dict['floor_no'] = floor_no
        props_dict['rent'] = target.get('Rent', None)
        
        location = ad_data.get('location')

        # if the location is not accurate, reject the listing
        mapDetails = location.get('mapDetails')
        isInexact = mapDetails.get('radius', -1)

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
        props_dict['construction_status'] = construction_status[0] if construction_status is not None else None

        # additional information 
        extras = target.get('Extras_types', None)
        if extras:
            props_dict['garage']   = True if "garage" in extras else False
            props_dict['lift']     = True if "lift" in extras else False
            props_dict['basement'] = True if "basement" in extras else False
            props_dict['balcony']  = True if "balcony" in extras else False
            props_dict['garden']   = True if "garden" in extras else False
            props_dict['terrace']  = True if "terrace" in extras else False

        '''
        print(f"ID: {ad_id}")
        #print(f"Description: {ad_description}")
        print(f"Area: {props_dict['area']}")
        print(f"Price: {props_dict['price']}")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"District: {props_dict['district']}")
        print(f"Rent: {props_dict['rent']}")
        print(f"Market: {props_dict['market']}")
        print(f"Floors number: {props_dict['floors_num']}")
        print(f"Floor number: {props_dict['floor_no']}")
        '''

        if isInexact != 0:
            return None
        if(props_dict['area'] is None or props_dict['price'] is None or 
           props_dict['market'] is None or props_dict['rooms_num'] is None):
            return None
        data = [props_dict[p] for p in properties]

        return data
    except AttributeError as e:
        print(f"error when scraping JSON {e}")
        print(f"URL: {url}")
        return None

    return None

def get_max_page(listings_url):
    page = requests.get(listings_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, "html.parser")

    pages_soup = soup.find("nav", attrs={"data-cy" : "pagination", "role" : "navigation"})
    pages_soup = pages_soup.find_all("a", attrs={"data-cy" : re.compile("pagination.go-to-page*")})

    return max(int(page_num.text) for page_num in pages_soup)


def scrape_otodom(listings_mx=None, properties=None, filename=None):

    filename = filename or CSV_FILE_NAME
    visited_listings = set()
    isValid = False
    try:
        df = pd.read_csv(filename, delimiter=';')
        visited_listings = set(df['Link'])
        properties = list(col.lower() for col in df.columns.values)
        isValid = True
    except FileNotFoundError:
        print("The file does not exist.")

    properties = sorted(properties, key=lambda x: PROPERTIES.index(x)) if properties else PROPERTIES

    if not listings_mx:
        listings_mx = inf
    
    lcounter = 0

    with open(filename, "a", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow([p.capitalize() for p in properties]) if not isValid else None
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
                sleeptime = random.uniform(1, 2)
                sleep(sleeptime)
                data = retrieve_listing_data(BASE_URL + link, properties) 
                if not data:
                    continue
                lcounter += 1
                print(f"Listing number: {lcounter}")
                writer.writerow(data)
                if lcounter >= listings_mx:
                    print("Reached the given limit")
                    return None 
                if lcounter % 100 == 0:
                    print(f"Number of listings acquired: {lcounter}")
        print("Reached the end of the listings")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrapes otodom website for flat listings")
    parser.add_argument('-l', '--listings', type=int, metavar = 'n',
                        help='allows specifying how many listing to scrapes')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--properties', nargs='+', choices=PROPERTIES, 
                        help='allows choosing which properties to scrape')
    group.add_argument('-f', '--file', type=str, metavar = 'filename',
                        help='allows specifying the filename to load the data from')
    args = parser.parse_args()
    scrape_otodom(args.listings, args.properties, args.file)
