import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import json
import time
import random
import re


class DropdownError(Exception):
    pass


class SubmitError(Exception):
    pass


def process_result(result):
    """Handling both strings and integers as result"""
    if result:
        if result[0].isdigit():
            return re.search(r'([\d,]+)', result).group().replace(',', '')
        else:
            return result


def create_session(target_url, session_data):
    deserialized_session_data = json.loads(session_data)
    session = requests.Session()
    session.cookies = requests.utils.cookiejar_from_dict(deserialized_session_data)
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    }
    response = session.get(target_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return session, soup


def detect_captcha(soup):
    """Can be updated with different captcha elements, if new are created"""
    captcha_element = soup.find('div', {'class': 'recaptcha-checkbox-border Animation'})
    if captcha_element:
        return True


def get_scraped_data(track_targets, session_data):
    """Scrapes track_targets object url - keyword - column number values. Returns JSON keyword-values"""
    if not track_targets:
        return None
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
            session, soup = create_session(link, session_data)
            if detect_captcha(soup):
                json_data = json.dumps({'captcha': 'detected'})
                return json_data
            for track_key in group:
                try:
                    keyword_td = soup.find('td', string=track_key.keyword)
                    if keyword_td:
                        res = process_result(
                            keyword_td.find_next_siblings('td')[track_key.iterator_value].get_text(strip=True))
                        if str(track_key) in result:
                            result[str(track_key)].append(res)
                        else:
                            result[str(track_key)] = [res]
                except IndexError:
                    print(f"Error: Invalid iterator value for track_key: {track_key}")
        except requests.exceptions.HTTPError as http_err:
            print(f"Error: HTTP error occurred while fetching data for link: {link}, Error message: {str(http_err)}")
        except requests.exceptions.RequestException as req_err:
            print(
                f"Error: Request exception occurred while fetching data for link: {link}, Error message: {str(req_err)}")
        except Exception as err:
            print(
                f"Error: An unexpected error occurred while fetching data for link: {link}, Error message: {str(err)}")
        if i != link_count - 1:
            time.sleep(random.randint(1, 3))
    json_data = json.dumps(result)
    return json_data


def select_dropdow(link, dropbox_keyword_or_id, new_option, session_data):
    """function selects new option in html dropdox"""
    session, soup = create_session(link, session_data)
    if detect_captcha(soup):
        raise DropdownError('Captcha detected while trying to select dropdown')
    """ select_tag find both id and name, whatever is defined"""
    select_tag = soup.find('select', attrs={'name': dropbox_keyword_or_id}) or soup.find('select', attrs={
        'id': dropbox_keyword_or_id})
    if not select_tag:
        raise DropdownError('Invalid dropbox_keyword_or_id of select dropdown')
    else:
        option = select_tag.find('option', {'value': new_option})
        if not option:
            raise DropdownError('Invalid new value for select dropdown')
        else:
            option['selected'] = 'selected'
            return True


def enter_manually(link, input_keyword_or_id, new_value, session_data):
    session, soup = create_session(link, session_data)
    if detect_captcha(soup):
        return False
    """ input_tag find both id and name, whatever is defined"""
    input_tag = soup.find('input', attrs={'name': input_keyword_or_id}) or soup.find('input', attrs={
        'id': input_keyword_or_id})
    if input_tag:
        input_type = input_tag.get('type', 'text')
        if input_type == 'number':
            try:
                new_value = int(new_value)
            except ValueError:
                return False
        input_tag['value'] = str(new_value)
        return True
    return False
    pass


def select_checkbox(link, checkbox_name_or_id, session_data):
    session, soup = create_session(link, session_data)
    if detect_captcha(soup):
        return False
    checkbox = soup.find('input',
                         {'type': 'checkbox', '$or': [{'id': checkbox_name_or_id}, {'name': checkbox_name_or_id}]})
    if checkbox:
        checkbox['checked'] = 'checked'
        return True
    return False


def select_radiobox(link, radiobox_name_or_id, session_data):
    session, soup = create_session(link, session_data)
    if detect_captcha(soup):
        return False
    radiobox = soup.find('input',
                         {'type': 'radio', '$or': [{'id': radiobox_name_or_id}, {'name': radiobox_name_or_id}]})

    if radiobox:
        radiobox['checked'] = 'checked'
        return True
    return False


def press_button(link, button_value, session_data):
    session, soup = create_session(link, session_data)
    if detect_captcha(soup):
        return False
    click_button = soup.find('button', {'type': 'button', 'value': button_value})
    if click_button:
        form = click_button.find_parent('form')
        if form:
            form.submit()
            return True
    return False


def press_submit(link, submitbutton_value, session_data):
    session, soup = create_session(link, session_data)
    if detect_captcha(soup):
        raise SubmitError('Captcha detected while trying to submit')
    submit_button = soup.find('input', {'type': 'submit', 'value': submitbutton_value})
    if not submit_button:
        raise SubmitError('Submit button not found, check the value')
    else:
        form = submit_button.find_parent('form')
        action_url = link.replace('.cgi', '2.cgi')
        method = form.get('method', 'POST')
        form_data = {}
        inputs_and_selects = form.find_all(['input', 'select'])
        for element in inputs_and_selects:
            if not element.has_attr('name'):
                continue
            name = element.get('name')
            if element.name == 'select':
                selected_option = element.find('option', selected=True)
                value = selected_option.get('value') if selected_option else None
            else:
                value = element.get('value', '')
            form_data[name] = value
        if not form:
            raise SubmitError('Error raised when attempting to submit form')
        else:
            deserialized_session_data = json.loads(session_data)
            response = requests.post(action_url, data=form_data, cookies=deserialized_session_data)
            if response.status_code == 200:
                print("Response content:", response.text)
            else:
                print("Form submission failed with status code:", response.status_code)
            return True

# find_previous_sibling - todo
