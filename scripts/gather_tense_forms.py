import argparse, json, logging, re, requests
from bs4 import BeautifulSoup
from pathlib import Path

def get_tense_forms(form, soup, logger):
    ps = [p for p in soup.find_all('p')
            if p.find('strong', class_='Arab headword', lang='ar') and
                (
                    (
                        p.find_previous_sibling('div') and
                        p.find_previous_sibling('div').find('h3') and
                        p.find_previous_sibling('div').find('h3').text == 'Verb'
                    )
                    or
                    (
                        p.find_previous_sibling('div') and
                        p.find_previous_sibling('div').find('h4') and
                        p.find_previous_sibling('div').find('h4').text == 'Verb'
                    )
                )
        ]
    forms = []
    past_or_pattern = re.compile(r'(.*) or (.*)')
    past_two_or_pattern = re.compile(r'(.*) or (.*) or (.*)')
    for p in ps:
        verb_form = p.find('span', class_='ib-content qualifier-content')
        if not verb_form or verb_form.text != 'I':
            continue
        past_form_find = p.find('strong', class_='Arab headword', lang='ar')
        if not past_form_find:
            logger.info(f'No past form found for {form}')
            continue
        past_form = past_form_find.text
        logger.info(f'Past form: {past_form} for {form}')
        past_two_or_search = past_two_or_pattern.search(past_form)
        if not past_two_or_search:
            past_or_search = past_or_pattern.search(past_form)
        past_transliteration_find = p.find('span', class_='Latn', lang='ar-Latn')
        if not past_transliteration_find:
            logger.info(f'No transliteration found for {form}')
            continue
        past_transliteration = past_transliteration_find.text
        logger.info(f'Past transliteration: {past_transliteration} for {form}')
        past_two_or_tr_search = past_two_or_pattern.search(past_transliteration)
        if not past_two_or_tr_search:
            past_or_tr_search = past_or_pattern.search(past_transliteration)
        bs = [b for b in p.find_all('b', class_='Arab', lang='ar') 
                if b.find_previous_sibling('i') and b.find_previous_sibling('i', string=lambda text: text != 'or').text == 'non-past'
        ]
        d = {'present_forms': [], 'transliterations': []}
        for i, b in enumerate(bs):
            present_form = b.text
            logger.info(f'Present form: {present_form} for {form}')
            d['present_forms'].append(present_form)
            transliteration_find = b.find_next_sibling('span', class_='Latn', lang='ar-Latn')
            if transliteration_find:
                tr_text = transliteration_find.text
                logger.info(f'Transliteration: {tr_text} for {form}')
                d['transliterations'].append(tr_text)
        for i in range(len(d['present_forms'])):
            if i < len(d['transliterations']):
                present_d = {'original': d['present_forms'][i], 'transliteration': d['transliterations'][i]}
            else:
                present_d = {'original': d['present_forms'][i]}
            if past_two_or_search and past_two_or_tr_search:
                past_form1, past_form2, past_form3 = past_two_or_search.groups()
                past_transliteration1, past_transliteration2, past_transliteration3 = past_two_or_tr_search.groups()
                form_d1 = {'past': {'original': past_form1, 'transliteration': past_transliteration3}, 'present': present_d}
                form_d2 = {'past': {'original': past_form2, 'transliteration': past_transliteration2}, 'present': present_d}
                form_d3 = {'past': {'original': past_form3, 'transliteration': past_transliteration1}, 'present': present_d}
                if form_d1 not in forms:
                    forms.append(form_d1)
                if form_d2 not in forms:
                    forms.append(form_d2)
                if form_d3 not in forms:
                    forms.append(form_d3)
            elif past_or_search and past_or_tr_search:
                past_form1, past_form2 = past_or_search.groups()
                past_transliteration1, past_transliteration2 = past_or_tr_search.groups()
                form_d1 = {'past': {'original': past_form1, 'transliteration': past_transliteration2}, 'present': present_d}
                form_d2 = {'past': {'original': past_form2, 'transliteration': past_transliteration1}, 'present': present_d}
                if form_d1 not in forms:
                    forms.append(form_d1)
                if form_d2 not in forms:
                    forms.append(form_d2)
            else:
                form_d = {'past': {'original': past_form, 'transliteration': past_transliteration}, 'present': present_d}
                if form_d not in forms:
                    forms.append(form_d)
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
    data_dir = script_dir / '../data'
    data_dir.mkdir(exist_ok=True)
    output_path = data_dir / 'forms.json'

    # if output_path.exists():
    #     with output_path.open('r', encoding='utf-8') as f:
    #         verb_d = json.load(f)

    for i, (form, data) in enumerate(verb_d.items()):
        if form != 'تعس': # debugging
            continue
        # if form != 'أمر': # debugging
        #     continue
        logger.info(f'Processing {form}')
        if 'forms' in data:
            continue
        href = data['href']
        response = requests.get(base_url + href)
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