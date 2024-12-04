import argparse, itertools, json
from pathlib import Path
from util import get_transliteration

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--forms', type=Path, help='Path to forms.json', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    with args.forms.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)

    vowel_d = {}
    for form, data in verb_d.items():
        if 'forms' in data:
            forms = data['forms']
            for form in forms:
                past_original, present_original = form['past'], form['present']
                for past_original, present_original in itertools.product(form['past'], form['present']):
                    past_vowels_str = get_transliteration(past_original, add_vowels=True, add_consonants=False)
                    if past_vowels_str not in vowel_d:
                        vowel_d[past_vowels_str] = {}
                    present_vowels_str = get_transliteration(present_original, add_vowels=True, add_consonants=False)
                    if present_vowels_str not in vowel_d[past_vowels_str]:
                        vowel_d[past_vowels_str][present_vowels_str] = 0
                    vowel_d[past_vowels_str][present_vowels_str] += 1
                    if past_vowels_str == 'a-i-a' and present_vowels_str == 'a-u-u':
                        print(form, past_vowels_str, present_vowels_str)

    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    data_dir = root_dir / 'data'
    output_path = data_dir / 'vowel_orders.json'
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(vowel_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()