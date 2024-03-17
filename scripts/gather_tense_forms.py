import requests, json, argparse, re
from bs4 import BeautifulSoup
from pathlib import Path

def get_tense_forms(soup):
    ps = [p for p in soup.find_all('p') 
          if p.find('strong', class_='Arab headword', lang='ar') and 
            ((p.find_previous_sibling('h4') and 
                p.find_previous_sibling('h4').find('span', class_='mw-headline') and 
                    p.find_previous_sibling('h4').find('span', class_='mw-headline').text == 'Verb')
            or
            (p.find_previous_sibling('h3') and
                p.find_previous_sibling('h3').find('span', class_='mw-headline') and
                    p.find_previous_sibling('h3').find('span', class_='mw-headline').text == 'Verb')) and
                        p.find('abbr', title='Verb form I')
        ]
    forms = []
    tr_pattern1 = re.compile(r'\((.*)\)')
    tr_pattern2 = re.compile(r'\((.*) (.*)\)')
    for p in ps:
        if p.find('br'):
            parts = p.decode_contents().split('<br/>')
            parts = [BeautifulSoup(part, 'html.parser') for part in parts]
        else:
            parts = [p]
        for part in parts:
            p = part
            strong = p.find('strong', class_='Arab headword', lang='ar')
            if not strong:
                continue
            past_form = p.find('strong', class_='Arab headword', lang='ar').text
            past_transliteration = p.find('span', class_='Latn', lang='ar-Latn').text
            bs = p.find_all('b', class_='Arab', lang='ar')
            d = {'present_forms': [], 'transliterations': []}
            for i, b in enumerate(bs):
                present_form = b.text
                d['present_forms'].append(present_form)
                if i == len(bs) - 1:
                    b_next_sibling = b.next_sibling
                    if b_next_sibling:
                        text_after_b = b_next_sibling.strip()
                        tr_search1 = tr_pattern1.search(text_after_b)
                        if tr_search1:
                            tr_text = tr_search1.group(1)
                            d['transliterations'] = [tr_text]
                        else:
                            small_sibling = b_next_sibling.next_sibling
                            if small_sibling and small_sibling.name == 'small' and small_sibling.text == 'or':
                                second = small_sibling.next_sibling.strip()
                                if second:
                                    merged = text_after_b + ' ' + second
                            tr_search2 = tr_pattern2.search(merged)
                            if tr_search2:
                                tr_text1, tr_text2 = tr_search2.groups()
                                d['transliterations'] = [tr_text1, tr_text2]
            for i in range(len(d['present_forms'])):
                if i < len(d['transliterations']):
                    present_d = {'original': d['present_forms'][i], 'transliteration': d['transliterations'][i]}
                else:
                    present_d = {'original': d['present_forms'][i]}
                form_d = {'past': {'original': past_form, 'transliteration': past_transliteration}, 'present': present_d}
                if form_d not in forms:
                    forms.append(form_d)
    return forms

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbs', type=str, help='Path to verbs.json', required=True)
    return parser.parse_args()

def main():
    base_url = 'https://en.wiktionary.org'

    args = get_args()
    verbs_path = Path(args.verbs)
    with verbs_path.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)
    
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    output_path = Path(data_dir, 'forms.json')

    if output_path.exists():
        with output_path.open('r', encoding='utf-8') as f:
            verb_d = json.load(f)
    
    for i, (form, data) in enumerate(verb_d.items()):
        if 'forms' in data:
            continue
        # form_to_search = 'بطن'
        # if form != form_to_search:
        #     continue
        href = data['href']
        response = requests.get(base_url + href)
        soup = BeautifulSoup(response.text, 'html.parser')
        # if form == form_to_search:
        #     with open('test.html', 'w', encoding='utf-8') as f:
        #         f.write(soup.prettify())
        #     exit()
        verb_d[form]['forms'] = get_tense_forms(soup)
        if i % 10 == 0:
            print(f'{i} forms processed')
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(verb_d, f, ensure_ascii=False, indent=2)

    with output_path.open('w', encoding='utf-8') as f:
        json.dump(verb_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()