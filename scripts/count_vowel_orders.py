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
    
    vowels = {
        chr(1570): 'ā',
        chr(1614): 'a',
        chr(1615): 'u',
        chr(1616): 'i'
    }
    fatha = chr(1614)
    maqsura = chr(1609)
    alif = chr(1575)
    
    vowel_d = {}
    for form, data in verb_d.items():
        if 'forms' in data:
            forms = data['forms']
            for form in forms:
                past_original, present_original = form['past']['original'], form['present']['original']
                past_vowels = []
                for i, v in enumerate(past_original):
                    if v == fatha and i < len(past_original) - 1 and (past_original[i + 1] in [maqsura, alif]):
                        past_vowels.append('ā')
                    elif v in vowels:
                        past_vowels.append(vowels[v])
                past_vowels_str = '-'.join(past_vowels)
                if past_vowels_str == 'a-i-a-ā-a-a-i':
                    print(form)
                if past_vowels_str not in vowel_d:
                    vowel_d[past_vowels_str] = {}
                present_vowels = []
                for i, v in enumerate(present_original):
                    if v == fatha and i < len(present_original) - 1 and (present_original[i + 1] in [maqsura, alif]):
                        present_vowels.append('ā')
                    elif v in vowels:
                        present_vowels.append(vowels[v])
                present_vowels_str = '-'.join(present_vowels)
                if present_vowels_str not in vowel_d[past_vowels_str]:
                    vowel_d[past_vowels_str][present_vowels_str] = 0
                vowel_d[past_vowels_str][present_vowels_str] += 1
    
    output_path = Path('data', 'vowel_orders.json')
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(vowel_d, f, ensure_ascii=False, indent=2)
    
if __name__ == '__main__':
    main()