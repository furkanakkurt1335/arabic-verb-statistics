import json, argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbs', type=str, help='Path to verbs.json', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    verbs_path = Path(args.verbs)
    with verbs_path.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)
    
    verbs_to_delete = []
    for form, data in verb_d.items():
        if ' ' in form:
            verbs_to_delete.append(form)

    for form in verbs_to_delete:
        del verb_d[form]

    with verbs_path.open('w', encoding='utf-8') as f:
        json.dump(verb_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()