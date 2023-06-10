import requests
from bs4 import BeautifulSoup


def getFavicon(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    icon_link = soup.find('link', rel='icon') or soup.find(
        'link', rel='shortcut icon')
    if icon_link:
        favicon = icon_link['href']
        if favicon.startswith('http'):  # absolute URL
            print(favicon)
            return favicon
        else:  # relative URL
            return requests.compat.urljoin(url, favicon)
    else:
        return None
