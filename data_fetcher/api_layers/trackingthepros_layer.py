import requests
from bs4 import BeautifulSoup
import logging

class TTPLayer:
    def __init__(self):
        self.subdomains = {'[NA]': 'na1', '[EU]': 'euw1', '[EUW]': 'euw1',
                           '[KR]': 'kr', '[EUNE]': 'eun1', '[BR]': 'br1'}
        self.soup = None

    def get_player(self, name):
        r = requests.get('https://www.trackingthepros.com/player/{}'.format(name))
        if 'players' not in r.url:
            return BeautifulSoup(r.text, features='lxml')

    def get_first_account_element(self, soup):
        inner_info = soup.find_all('div', class_='player-info-inner')
        card = [x for x in inner_info if x.find('h4', text='Accounts') is not None][0]
        table = card.find('table')
        return table.find('tr')

    def get_account(self, element):
        td = element.find('td')
        server = self.get_subdomain_for_region(td.find('b').getText().strip())
        account_name = td.getText().split(']')[-1].strip()
        return {'server': server, 'account_name': account_name}

    def get_soloq_ids_from_trackingthepros(self, name):
        result = []
        soup = self.get_player(name)
        if soup == None:
            return None
        element = self.get_first_account_element(soup)
        while element is not None and not (element.has_attr('id') and 'inactive_link' in element['id']):
            if element.has_attr('class') and 'inactive_account' in element['class']:
                element = element.next_sibling
                continue
            result.append(self.get_account(element))
            element = element.next_sibling
        return result

    def get_subdomain_for_region(self, region):
        return self.subdomains[region]
