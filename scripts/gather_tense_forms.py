import argparse, json, logging, requests
from bs4 import BeautifulSoup
from pathlib import Path

def get_tense_forms(form, soup, logger):
    ps = [p for p in soup.find_all('p')
            if p.find('strong', class_='Arab headword', lang='ar')]
    forms = []
    for p in ps:
        headword_lines = p.find_all('span', class_='headword-line')
        for headword_line in headword_lines:
            verb_form = headword_line.find('span', class_='ib-content qualifier-content')
            if not verb_form or verb_form.text != 'I':
                continue
            past_form_find = headword_line.find_all('strong', class_='Arab headword', lang='ar')
            if not past_form_find:
                logger.info(f'No past form found for {form}')
                continue
            past_forms = [past_form.text for past_form in past_form_find]
            logger.info(f'Past forms: {past_forms} for {form}')
            bs = [b for b in headword_line.find_all('b', class_='Arab', lang='ar')
                    if b.find_previous_sibling('i') and b.find_previous_sibling('i', string=lambda text: text != 'or').text == 'non-past'
            ]
            present_forms = []
            for b in bs:
                present_form = b.text
                logger.info(f'Present form: {present_form} for {form}')
                present_forms.append(present_form)
            forms.append({'past': past_forms, 'present': present_forms})
    return forms

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbs', type=Path, help='Path to verbs.json', required=True)
    return parser.parse_args()

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='gather_tense_forms.log')
    logger = logging.getLogger(__name__)
    base_url = 'https://en.wiktionary.org'

    args = get_args()
    with args.verbs.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)

    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    data_dir = root_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    output_path = data_dir / 'forms.json'

    if output_path.exists():
        with output_path.open('r', encoding='utf-8') as f:
            verb_d = json.load(f)

    html_dir = root_dir / 'html'
    html_dir.mkdir(exist_ok=True)
    for i, (form, data) in enumerate(verb_d.items()):
        logger.info(f'Processing {form}')
        if 'forms' in data and data['forms']:
            continue
        form_html_path = html_dir / f'{form}.html'
        if form_html_path.exists():
            with form_html_path.open('r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        else:
            response = requests.get(base_url + data['href'])
            with form_html_path.open('w', encoding='utf-8') as f:
                f.write(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')
        tense_forms = get_tense_forms(form, soup, logger)
        logger.info(f'Tense forms: {tense_forms}')
        verb_d[form]['forms'] = tense_forms
        if i % 10 == 0:
            logger.info(f'{i} forms processed')
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(verb_d, f, ensure_ascii=False, indent=2)

    with output_path.open('w', encoding='utf-8') as f:
        json.dump(verb_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()