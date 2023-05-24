import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import json
import time
import random


def get_scraped_data(track_targets, session_data):
    """Scrapes track_targets object url - keyword - column number values. Returns JSON keyword-values"""
    if not track_targets:
        return None
    deserialized_session_data = json.loads(session_data)
    session = requests.Session()
    session.cookies = requests.utils.cookiejar_from_dict(deserialized_session_data)
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    }
    grouped_targets = {}
    for track_key in track_targets:
        link = track_key.link
        if link in grouped_targets:
            grouped_targets[link].append(track_key)
        else:
            grouped_targets[link] = [track_key]
    link_count = len(grouped_targets)
    result = {}
    for i, (link, group) in enumerate(grouped_targets.items()):
        try:
            response = session.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            captcha_element = soup.find('div', {'class': 'recaptcha-checkbox-border Animation'})
            if captcha_element:
                json_data = json.dumps({'captcha': 'detected'})
                return json_data
            for track_key in group:
                try:
                    keyword_td = soup.find('td', string=track_key.keyword)
                    if keyword_td:
                        res = int(keyword_td.find_next_siblings('td')[track_key.iterator_value].get_text(strip=True).replace(',', ''))
                        result[str(track_key)] = res
                except IndexError:
                    print(f"Error: Invalid iterator value for track_key: {track_key}")
        except RequestException as e:
            print(f"Error: Failed to fetch data for link: {link}, Error message: {str(e)}")
        if i != link_count - 1:
            time.sleep(random.randint(1, 3))
    json_data = json.dumps(result)
    return json_data
