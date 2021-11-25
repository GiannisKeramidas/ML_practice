from bs4 import BeautifulSoup
from urllib.request import urlopen
import request
import json
import pandas as pd

# Leaders webpages that we need to scrape for player url's
base_url = "https://www.euroleague.net"

url_leaders_1 = "https://www.euroleague.net/main/statistics?agg=PerGame&mode=Leaders&seasonmode=Single&entity=Players&cat=Score&seasoncode=E2021&page=1"

url_leaders_2 = "https://www.euroleague.net/main/statistics?agg=PerGame&mode=Leaders&seasonmode=Single&entity=Players&cat=Score&seasoncode=E2021&page=2"

leaders_urls = [url_leaders_1,url_leaders_2]

def create_soup(url):
    """Create a soup object from a url."""
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html5lib")
    return soup

def player_dictionary_creation(soup):
    """Function that takes a soup object from a player url and returning a dictionary with his stats."""
    player_data_dict = {}
    player_data = soup.find_all(class_="player-data")
    name_of_player = player_data[0].find_all(class_="name")[0].get_text().split(",")
    player_data_dict['name'] = name_of_player[1] + " " + name_of_player[0]
    first_summary_spans = player_data[0].find_all(class_="summary-first")[0].find_all("span")
    player_data_dict['position'] = first_summary_spans[1].find_all("span")[1].get_text()
    second_summary_spans = player_data[0].find_all(class_='summary-second')[0].find_all("span")
    player_data_dict['height'] = second_summary_spans[0].get_text().split(":")[1]
    player_data_dict['dob'] = second_summary_spans[1].get_text().split(":")[1]
    stats_table = soup.find('table', id = "tblPlayerPhaseStatistics" )
    stats = stats_table.find_all(class_="PlayerGridRow")[0].find_all("td")
    headers = stats_table.find_all("tr")[1].find_all("th") 
    for i, (stat, header) in enumerate(zip(stats,headers)):
        if i!=0:
            player_data_dict[header.get_text()] = stat.get_text()
    return player_data_dict

def players_urls():
    """Function that grabs individual players urls."""
    players_url_list = []
    for url in leaders_urls:
        html_leaders = requests.get(url)
        soup_leaders = BeautifulSoup(html_leaders.text, "html5lib")
        player_tags_even = soup_leaders.find_all("table")[0].find_all("tr",class_="StatsAlternatingGridResults")
        player_tags_odd = soup_leaders.find_all("table")[0].find_all("tr",class_="StatsRowAlternatingGridResults")
        player_tags = player_tags_even + player_tags_odd
        players_url_list.extend([tag.find_all("a")[0].get('href') for tag in player_tags])
    return players_url_list

def json_dump(Player_List):
    """Function that dumps the list of players dicts in a json file.""""
    with open("Players.json","w") as f:
        json.dump(Player_List,f)
        
def scrapping_wrapper():
    """"Function that returns list of player dicts."""
    player_list = []
    players_url_list = players_urls()
    for relative_url in players_url_list:
        absolute_url = base_url + relative_url
        soup = create_soup(absolute_url)
        player_dict = player_dictionary_creation(soup)
        player_list.append(player_dict)
    return player_list
