""" adapted from https://github.com/keithito/tacotron """

import re
_alt_re = re.compile(r'\([0-9]+\)')


class Grapheme2PhonemeDictionary:
    """Thin wrapper around g2p data."""
    def __init__(self, file_or_path, keep_ambiguous=True, encoding='latin-1',
                split_token='\t', language=None):
        with open(file_or_path, encoding=encoding) as f:
            if language is None:
                # default to cmudict
                entries = _parse_g2p(f, split_token)
            else:
                entries = _parse_multilanguage_g2p(f, split_token)
        if not keep_ambiguous:
            entries = {word: pron for word, pron in entries.items()
                       if len(pron) == 1}
        self._entries = entries

    def __len__(self):
        return len(self._entries)

    def lookup(self, word):
        """Returns list of pronunciations of the given word."""
        return self._entries.get(word.upper())


def _parse_g2p(file, split_token='\t'):
    g2p = {}
    for line in file:
        if len(line) and (line[0] >= 'A' and line[0] <= 'Z' or line[0] == "'"):
            parts = line.split(split_token)
            word = re.sub(_alt_re, '', parts[0])
            pronunciation = parts[1].strip()
            if word in g2p:
                g2p[word].append(pronunciation)
            else:
                g2p[word] = [pronunciation]
    return g2p

def _parse_multilanguage_g2p(file, split_token='\t'):
    g2p = {}
    for line in file:
        parts = line.split(split_token)
        word = parts[0]
        # make sure all keys are upper case for proper match
        word = word.upper()
        pronunciations = parts[1].strip()
        pronunciations = pronunciations.split(", ")  # default in ipa-dict

        if word not in g2p:
            g2p[word] = []
            
        for pronunciation in pronunciations:
            pronunciation = pronunciation[1:-1]  # remove default / p /
            pronunciation = list(pronunciation) # seperate with spaces
            pronunciation = ' '.join(pronunciation)
            g2p[word].append(pronunciation)

        if word not in g2p or g2p[word] == []:
            print(f'{word} not in dict')

    return g2p