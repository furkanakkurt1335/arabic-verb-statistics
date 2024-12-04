madda = chr(1570)
alif = chr(1575)
waw = chr(1608)
maqsura = chr(1609)
ya = chr(1610)
fatha = chr(1614)
damma = chr(1615)
kasra = chr(1616)
jazm = chr(1617)
vowels = {
    madda: 'ā',
    fatha: 'a',
    damma: 'u',
    kasra: 'i',
    jazm: '\''
}
consonants = {
    'أ': 'ʔ',
    'ء': 'ʔ',
    'ب': 'b',
    'ت': 't',
    'ث': 'ṯ',
    'ج': 'j',
    'ح': 'ḥ',
    'خ': 'ḵ',
    'د': 'd',
    'ذ': 'ḏ',
    'ر': 'r',
    'ز': 'z',
    'س': 's',
    'ش': 'š',
    'ص': 'ṣ',
    'ض': 'ḍ',
    'ط': 'ṭ',
    'ظ': 'ẓ',
    'ع': 'ʕ',
    'غ': 'ġ',
    'ف': 'f',
    'ق': 'q',
    'ك': 'k',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'و': 'w',
    'ي': 'y'
}

def get_transliteration(original_str, add_vowels=True, add_consonants=False, join_char='-'):
    transliteration = []
    for i, ch in enumerate(original_str):
        if ch == fatha and i < len(original_str) - 1 and original_str[i + 1] in [maqsura, alif]:
            transliteration.append('ā')
        elif ch == kasra and i < len(original_str) - 1 and original_str[i + 1] == ya:
            transliteration.append('ī')
        elif ch == damma and i < len(original_str) - 1 and original_str[i + 1] == waw:
            transliteration.append('ū')
        elif add_vowels and ch in vowels:
            transliteration.append(vowels[ch])
        elif add_consonants and ch in consonants:
            if ch in ['و', 'ي'] and ((i < len(original_str) - 1 and original_str[i + 1] not in [fatha, damma, kasra]) or (i == len(original_str) - 1)):
                continue
            transliteration.append(consonants[ch])
    return join_char.join(transliteration)

transliteration_character_order = [
    'ʔ',
    'b',
    't',
    'ṯ',
    'j',
    'ḥ',
    'ḵ',
    'd',
    'ḏ',
    'r',
    'z',
    's',
    'š',
    'ṣ',
    'ḍ',
    'ṭ',
    'ẓ',
    'ʕ',
    'ġ',
    'f',
    'q',
    'k',
    'l',
    'm',
    'n',
    'h',
    'w',
    'y'
]

def sort_transliteration_characters(transliteration):
    return sorted(transliteration, key=lambda x: transliteration_character_order.index(x))