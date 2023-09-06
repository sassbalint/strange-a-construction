"""
Process dataset for the paper titled
"Strange a construction: the 'A egy N' in Hungarian". 
"""

import argparse
import re
import sys

SEP = '\t'


def replace_first(pattern, substitute, it):
    """SAR for each element of an iterator. Replace first occurence."""
    return map(lambda x: re.sub(pattern, substitute, x, 1), it)


def replace_all(pattern, substitute, it):
    """SAR for each element of an iterator. Replace all occurences."""
    return map(lambda x: re.sub(pattern, substitute, x), it)


def process_field(index, func, it, sep=SEP):
    """Split iterator elements by `sep` then apply `func` to field `index`."""
    for elem in it:
        fields = elem.split(sep)
        fields[index] = func(fields[index])
        yield sep.join(fields)


def main():
    """Process."""
    args = get_args()

    # ! minta -- ezt eleve nem vesszük bele

    # @ nick
    # ¤ egy 'egyetlen'
    # × téves mintaillesztés
    # – nem ezt keressük, véletlen illeszkedés
    # ß mérték (rövid egy hét (alatt), de lehetne rövid két hét... is (vs. + Rövid egy hét volt ez!). jó egy év
    # ÷ állítmány – alany  (akkor sikeres egy ország...)
    # ÷÷ összetettebb szerkezet (pl. szükséges egy kormánydöntés (meghozatalához))
    # * a melléknévként elemzett szó más szófajú (görbe  egy  szakasza)
    # " idézet
    # ’ Szemantikailag vagy grammatikailag zavaros
    # ? nem világos, éppúgy lehet az általunk keresett szerkezet, mint nem
    # $ ezt keressük, egész mondat
    # + ezt keressük, beágyazva
    # ++ valami különlegességgel (pl. halmozott vagy melléknevek)
    # +° nem fókuszként viselkedve
    # +! tulajdonnévvel (széles egy Magyarországon)

    # $ cat data/freq-exam-no-közösségi-prob-val.txt | grep "doc#" | sed "s/doc.*//" | sstat > CODES

    QMARK = 'Q'

    GOOD_CODES = {
        '$': 'OK, full',
        '+': 'OK, nested',
        '++': 'OK, nested, special',
        '+°': 'OK, nested, not as a focus',
        '+!': 'OK, nested, proper name',

        '$+': 'other',
    }
    GOOD_CODE_FIRST_CHARS = {x[0] for x in GOOD_CODES}

    BAD_CODES = {
        '@': 'nickname',
        '¤': "'egy' meaning 'sole'",
        '×': 'wrong match',
        '–': 'accidental match',
        'ß': 'measure',
        '÷': 'predicate – subject',
        '÷÷': 'complex phrase',
        '*': 'word erroneously analysed as adjective',
        QMARK: 'quote', # originally ["] but changed on-the-fly
        '’': 'semantically/grammatically confused',
        '?': 'dubious',

        '|': 'other',
        ':': 'other',
        '^': 'other',

        '÷ß¤': 'other',
        'ß+': 'other',
        '–$': 'other',
    }
    BAD_CODE_FIRST_CHARS = {x[0] for x in BAD_CODES}

    assert not GOOD_CODE_FIRST_CHARS.intersection(BAD_CODE_FIRST_CHARS)

    NEEDED_FIRST_CHARS = GOOD_CODE_FIRST_CHARS
    if args.all: NEEDED_FIRST_CHARS |= BAD_CODE_FIRST_CHARS

    CODES = {**GOOD_CODES, **BAD_CODES}

    it = map(lambda x: x.rstrip('\n'), sys.stdin)

    it = replace_first('^"', QMARK, it) # change quotation mark on-the-fly

    it = filter(lambda x: len(x) > 0 and x[0] in NEEDED_FIRST_CHARS, it)

    it = replace_first(SEP, '', it)
    it = replace_first('doc', f'{SEP}doc', it)
    it = replace_first('  *', SEP, it)
    it = replace_first(' < *', SEP, it)
    it = replace_first(' > *', SEP, it)
    it = replace_all('"', "'", it) # reserving ["] for string delimiter for smooth libreoffice cvs import

    it = process_field(0, lambda x: CODES[x], it, SEP)

    if args.dedup:
        # deduplication by field 3-5
        deduphash = {}
        for elem in it:
            fields = elem.split(SEP)
            val = SEP.join(fields[0:2])
            key = SEP.join(fields[2:5])
            deduphash[key] = val
        for key, val in deduphash.items():
            print(f'{val}{SEP}{key}')
    else:
        for elem in it:
            print(elem)


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--all',
        help='take bad examples as well, not just good ones',
        action='store_true'
    )
    parser.add_argument(
        '--dedup',
        help='deduplicate',
        action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
