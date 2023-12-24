from bs4 import BeautifulSoup
import requests
import re

BASE_URL = "https://www.otodom.pl"
LISTINGS_URL = BASE_URL + "/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw"

page = requests.get(LISTINGS_URL)
soup = BeautifulSoup(page.content, "html.parser")

pages_soup = soup.find("nav", attrs={"data-cy" : "pagination", "role" : "navigation"})
pages_soup = pages_soup.find_all("a", attrs={"data-cy" : re.compile("pagination.go-to-page*")})

max_page = max(int(page_num.text) for page_num in pages_soup)

print(max_page)

visited_listings = set()

for page_num in range(1, max_page + 1):
    page = requests.get(LISTINGS_URL + "?page=" + str(page_num))
    page_soup = BeautifulSoup(page.content, "html.parser")
    a_tags = page_soup.find_all("a", attrs={"data-cy" : "listing-item-link"})
    for tag in a_tags:
        link = tag["href"]
        if link not in visited_listings:
            visited_listings.add(link)
            # retrieve_data(link) -- implement retrieve data

print(len(visited_listings))

