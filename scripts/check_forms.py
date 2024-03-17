import json, argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--forms', type=str, help='Path to forms.json', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    forms_path = Path(args.forms)
    with forms_path.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)
    
    missing_counts = {'forms': 0, 'past': 0, 'present': 0, 'transliteration': 0}
    for form, data in verb_d.items():
        if 'forms' not in data:
            missing_counts['forms'] += 1
        else:
            forms = data['forms']
            for form in forms:
                if 'past' not in form:
                    missing_counts['past'] += 1
                if 'present' not in form:
                    missing_counts['present'] += 1
                if 'transliteration' not in form['past'] or form['past']['transliteration'] == '' or 'transliteration' not in form['present'] or form['present']['transliteration'] == '':
                    missing_counts['transliteration'] += 1
                    print(form)

    print(missing_counts)

if __name__ == '__main__':
    main()