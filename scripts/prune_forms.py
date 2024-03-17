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
    
    for form, data in verb_d.items():
        if 'forms' in data:
            forms = data['forms']
            for form in forms:
                if 'past' in form:
                    past = form['past']
                    if ' or ' in past['original']:
                        del data['forms']
                        break

    with forms_path.open('w', encoding='utf-8') as f:
        json.dump(verb_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()