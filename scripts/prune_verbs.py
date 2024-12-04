import json, argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbs', type=Path, help='Path to verbs.json', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    with args.verbs.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)
    
    verbs_to_delete = []
    for form in verb_d:
        if ' ' in form:
            verbs_to_delete.append(form)

    for form in verbs_to_delete:
        del verb_d[form]

    with args.verbs.open('w', encoding='utf-8') as f:
        json.dump(verb_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()