import argparse, itertools, json
from pathlib import Path
from util import get_transliteration, sort_transliteration_characters

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--forms', type=Path, help='Path to forms.json', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    with args.forms.open('r', encoding='utf-8') as f:
        verb_d = json.load(f)

    consonant_d = {}
    for form, data in verb_d.items():
        if 'forms' in data:
            forms = data['forms']
            for form in forms:
                past_original, present_original = form['past'], form['present']
                for past_original, present_original in itertools.product(form['past'], form['present']):
                    past_str = get_transliteration(past_original, add_vowels=True, add_consonants=True, join_char='')
                    present_str = get_transliteration(present_original, add_vowels=True, add_consonants=True, join_char='')
                    if len(past_str) != 6 or len(present_str) != 7: # fa'ala, yaf'alu
                        continue
                    past_middle_consonant, past_last_consonant = past_str[2], past_str[4]
                    key_str = f'{past_middle_consonant} -> {past_last_consonant}'
                    if key_str not in consonant_d:
                        consonant_d[key_str] = {}
                    present_middle_vowel = present_str[4]
                    if present_middle_vowel not in consonant_d[key_str]:
                        consonant_d[key_str][present_middle_vowel] = {'count': 0, 'forms': []}
                    consonant_d[key_str][present_middle_vowel]['count'] += 1
                    consonant_d[key_str][present_middle_vowel]['forms'].append((past_str, present_str))

    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    data_dir = root_dir / 'data'
    output_path = data_dir / 'consonant_counts.json'
    consonant_d = {k: v for k, v in sorted(consonant_d.items(), key=lambda item: sort_transliteration_characters(item[0].split(' -> ')))}
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(consonant_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()