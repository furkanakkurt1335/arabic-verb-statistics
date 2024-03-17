import requests, json
from bs4 import BeautifulSoup
from pathlib import Path

def get_verbs(soup):
    div = soup.find('div', id='mw-pages')
    groups = div.find_all('div', class_='mw-category-group')
    verbs = []
    for group in groups:
        for li in group.find_all('li'):
            link = li.find('a')
            href = link['href']
            form = link['title']
            verbs.append({'form': form, 'href': href})
    return verbs

def main():
    base_url = 'https://en.wiktionary.org'
    category_url = base_url + '/wiki/Category:Arabic_form-I_verbs'
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    verb_d = {}
    verbs = get_verbs(soup)
    for verb in verbs:
        verb_d[verb['form']] = {'href': verb['href']}

    # if next page exists, get the next page with the text 'next page'
    next_page = soup.find('a', string='next page')
    while next_page:
        next_url = base_url + next_page['href']
        response = requests.get(next_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        verbs = get_verbs(soup)
        for verb in verbs:
            verb_d[verb['form']] = {'href': verb['href']}
        next_page = soup.find('a', string='next page')

    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    output_path = Path(data_dir, 'verbs.json')
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(verb_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()