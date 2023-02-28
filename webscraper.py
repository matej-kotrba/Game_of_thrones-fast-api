# https://realpython.com/beautiful-soup-web-scraper-python/
# Modul requests (pip install requests)
import requests
# Import knihovny BeautifulSoup4 (pip install beautifulsoup4), která usnadňuje web scraping
from bs4 import BeautifulSoup
import json
import re

# Konstanta obsahující adresu webu, z něhož chceme získávat data
# Žebříček 250 nejlépe hodnocených filmů podle serveru imdb.com
URL = 'https://en.wikipedia.org/wiki/List_of_Game_of_Thrones_characters'
# URL = 'https://www.csfd.cz/zebricky/filmy/nejlepsi/'

# Odeslání požadavku metodou get na určenou URL adresu - HTTP server vrací zpět obsah stránky
# page = requests.get(URL, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'})
page = requests.get(URL)
# Vytvoření objektu parseru stránky
soup = BeautifulSoup(page.content, 'html.parser')
link_to_characters_pages = [f"https://en.wikipedia.org{item['href']}"
                             for item in soup.select('.wikitable:nth-of-type(1)>tbody>tr>td:nth-child(2)>a[href]')]

with open("characters.json",  "w", encoding='utf-8') as file:
    file.write('[\n')
    for i in range(len(link_to_characters_pages)):
        detail_page = requests.get(link_to_characters_pages[i], headers={'User-agent': 'Mozilla/5.0'})
        dsoup = BeautifulSoup(detail_page.content, 'html.parser')
        if dsoup.find('th', string='Portrayed by') is None or dsoup.select('.mw-page-title-main') == []: 
            continue
        name = dsoup.select('.mw-page-title-main')[0].text.replace(" (character)", "")
        image_url = dsoup.select('.infobox-image img')
        if image_url != []:
            image_url = image_url[0]['src']
        elif dsoup.select('.thumbimage') != []:
            image_url = dsoup.select('.thumbimage')[0]['src']
        else:
            continue
        actor_element = dsoup.find('th', string='Portrayed by').find_next_sibling('td')
        actor = None
        if actor_element.select("li") != []:
            actor = actor_element.select("li")[0].text
        else:
            actor = actor_element.select("a")[0].text
        familys = [""]
        if dsoup.find('th', string='Family'):
            familys_element = dsoup.find('th', string='Family').find_next_sibling('td')
            if familys_element.select("a") != []:
                familys = [item.text for item in familys_element.select("a")]
            else:
                familys = [familys_element.text]

        first_episode_name = ""
        first_episode_year = 0

        if dsoup.find('b', string='Television') is not None and len(dsoup.find('b', string='Television').findParent('li').find_next_sibling('li').select("a")) > 0:
            first_episode_element = dsoup.find('b', string='Television').findParent('li').find_next_sibling('li')
            first_episode_name = first_episode_element.select("a")[0].text
            first_episode_year = first_episode_element.text[first_episode_element.text.find('(') + 1:first_episode_element.text.find(')')]
        else:
            first_episode_element = dsoup.find('th', string='First appearance').find_next_sibling('td')
            first_episode_name = first_episode_element.select("a")[1].text
            first_episode_year = first_episode_element.text[first_episode_element.text.replace("(", "", 1).replace(")", "", 1).find('(') + 3
                                                            :first_episode_element.text.replace("(", "", 1).replace(")", "", 1).find(')') + 2]
            
        character_description = re.sub(r'\[\d\]|\"', '', dsoup.select("h2 > span:nth-child(1)")[0].find_next("p").text)
        character_description = character_description.rstrip("\n")

        row = f'"name": "{name}", "image_url": "{image_url}", "actor": "{actor}", "familys": {json.dumps(familys)}, "first_episode_name": "{first_episode_name}", "first_episode_year": {first_episode_year}, "character_description": "{character_description}"'
        row = '{' + row + '}'
        row = row + ',\n' if i != len(link_to_characters_pages) - 2 else row + "\n"
        file.write(row)
    file.write(']')


# content = dsoup.select('[data-testid=plot]>span[data-testid=plot-xs_to_m]')
# runtime = (dsoup.select('[data-testid=hero-title-block__metadata]>li:last-child'))[0].text[0:-1].split('h ')
# genre_links = dsoup.select('[data-testid=genres] a')
# genres = [genre.text for genre in genre_links]
# print(genres)
# if len(runtime) > 1:
#     runtime = int(runtime[0]) * 60 + int(runtime[1])
# else:
#     runtime = int(runtime[0]) * 60
# row = f'"title": "{titles[i]}", "year": {years[i]}, "runtime": {runtime}, "rating": {ratings[i]}, "description": "{content[0].text}", "director": "{directors[i]}", "actors": {json.dumps(actors[i])}, "url": "{urls[i]}", "genres": {json.dumps(genres)}'
# row = '{' + row + '}, '
# print(row)
# file.write(row)

    # movie_links = soup.select('article .film-title-norating')
# year_links = soup.select('td.titleColumn>span')
# rating_links = soup.select('td.ratingColumn>strong')
# # Získání názvů filmů
# titles = [tag.text for tag in movie_links]
# # Získání roků vzniku filmů
# years = [int(tag.text[1:-1]) for tag in year_links]
# # Získání hodnocení
# ratings = [float(tag.text) for tag in rating_links]
# # Získání režisérů
# directors = [tag['title'].split(',')[0][:-7] for tag in movie_links]
# # Získání herců
# actors = [tag['title'].split(', ')[1:] for tag in movie_links]
# # Odkazy na detaily filmů
# urls = [f'https://www.imdb.com{tag["href"]}' for tag in movie_links]
# # Kontrolní výpis získaných údajů