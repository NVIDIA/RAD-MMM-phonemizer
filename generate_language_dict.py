# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
from collections import defaultdict
import os
import argparse
import json
from tts_text_processing.text_processing import TextProcessing
from utils import load_dict, load_list


def phonemize_text(language, words_list, text_processor_config, output_dir):
    """returns a dict with word: ipa phoneme map"""
    # text_processor_config['language'] = language
    text_processor = TextProcessing(**text_processor_config)
    word_phoneme_mapping = {}
    for sentence in words_list:
        # pass through the vocoder and split at blanks
        seq = text_processor.sequence_to_text(text_processor.encode_text(sentence, language=language))
        if len(seq) == 0:
            print(seq)
            print(word)
            continue

        if seq[0] == '{':
            seq = seq[1:]
        if seq[-1] == '}':
            seq = seq[:-1]

        words = [word for word in sentence.split(' ')]
        phonemes = [ph for ph in seq.split('} {')]

        
        if len(words) != len(phonemes):
            # generally should be same except for cases like hyphenated
            print(words)
            print(phonemes)
            # merge
            phonemes = [' '.join(phonemes)]

        for word, phoneme in zip(words, phonemes):
            if word in word_phoneme_mapping and \
                word_phoneme_mapping[word] != phoneme:
                print('multiple versions of phonemes for same word')
                print(word)
                print(phoneme)
                print(word_phoneme_mapping[word])
            word_phoneme_mapping[word] = phoneme

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/{language}_word_ipa_map.txt', 'w') as fp:        
        for word in sorted(word_phoneme_mapping):
            phoneme = word_phoneme_mapping[word]
            fp.write(f'{word}\t{phoneme}\n')

    fp.close()

if __name__ == '__main__':
    # essentially performs the map operation on the language words
    # ie converts bunch of words to ipa phonemes for a language
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dictionary_path', type=str, default='', required=False)
    parser.add_argument('-w', '--wordlist_path', type=str)
    parser.add_argument('-l', '--language', type=str)
    parser.add_argument('-o', '--output_dir', type=str)
    parser.add_argument('-tp_config', '--text_processing_config_path', type=str)

    args = parser.parse_args()

    # dict path optional
    if args.dictionary_path is not None and \
        args.dictionary_path != '':
        word_dict = load_dict(args.dictionary_path)
        word_list = [word for word, phoneme in word_dict.items()]
    else:
        word_list = []

    sentence_list = load_list(args.wordlist_path)
    # words_list = list(set(list(set(word_list)) + list(set(sentence_list))))
    words_list = word_list
    for sentence in sentence_list:
        for word in sentence.split(' '):
            words_list.append(word)
    
    language = args.language

    print(f'processing language {language} with {len(words_list)} words...')

    with open(args.text_processing_config_path) as f:
        tp_config = f.read()

    text_processor_config = json.loads(tp_config)

    phonemized_words = phonemize_text(language, words_list, text_processor_config, args.output_dir)