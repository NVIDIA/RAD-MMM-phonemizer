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
import os
import sys
import argparse
import yaml
sys.path.append(os.path.join(sys.path[0],'../'))
from tts_text_processing.text_processing import TextProcessing
from phonemizer.backend import EspeakBackend
from phonemizer.punctuation import Punctuation
from phonemizer.separator import Separator
from scripting_utils import load_yaml

def get_phonemizer_phonemes(phonemizer_backend_instance, text):

    separator = Separator(phone='|\p|', word='} {')
    
    lexicon = phonemizer_backend_instance.phonemize([text], 
                                                    separator=separator, 
                                                    strip=True,
                                                    njobs=1)[0]
    lexicon = lexicon.replace('|\p|', ' ')
    lexicon = '{' + lexicon + '}'
    return lexicon

def phonemize_text(text_processor, text, language):
    phonemizer_backed = text_processor.phonemizer_backend_dict[language]
    return get_phonemizer_phonemes(phonemizer_backed, text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str,
                        help='YAML file for datasets')
    parser.add_argument('-o', '--output_path', type=str)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    if 'data' in cfg:
        cfg = cfg['data']
    
    text_processor = TextProcessing(
            cfg['symbol_set'], cfg['cleaner_names'], cfg['heteronyms_path'],
            cfg['phoneme_dict_path'],
            p_phoneme=cfg['p_phoneme'], handle_phoneme=cfg['handle_phoneme'],
            handle_phoneme_ambiguous=cfg['handle_phoneme_ambiguous'],
            prepend_space_to_text=cfg['prepend_space_to_text'],
            append_space_to_text=cfg['append_space_to_text'],
            add_bos_eos_to_text=cfg['add_bos_eos_to_text'],
            g2p_type=cfg['g2p_type'])
    
    accepted_keys = ['training_files', 'validation_files']
    for key in accepted_keys:
        if key in cfg.keys():
            # parse all datasets
            for speaker in cfg[key]:
                dataset = []
                
                print(f'processing {speaker}')
                print(cfg[key][speaker])
                filelist_path = os.path.join(cfg[key][speaker]['filelist_basedir'],
                                            cfg[key][speaker]['filelist'])
                language = cfg[key][speaker]['language']
                
                with open(filelist_path, encoding='utf-8') as f:
                    data = [line.strip().split('|') for line in f]
                
                print(f'processing file: {filelist_path}')
                
                for d in data:
                    phonemized_text = phonemize_text(text_processor, d[1], language)
                    dataset.append(
                        {
                            'audiopath': d[0],
                            'text': phonemized_text,
                            'speaker': d[2],
                            'emotion': d[3],
                            'duration': float(d[4]),
                            'language': language
                        }
                    )
                
                # dump to file
                filename = cfg[key][speaker]['filelist'].split('.')[0]
                fileext = cfg[key][speaker]['filelist'].split('.')[1]
                
                output_filelist_path = os.path.join(cfg[key][speaker]['filelist_basedir'],
                                                    filename + '_phonemized.' + fileext)
                
                with open(output_filelist_path, 'w') as fp:
                    for d in dataset:
                        fp.write('|'.join([d['audiopath'],
                                            d['text'],
                                            d['speaker'],
                                            d['emotion'],
                                            str(d['duration'])
                                            ]) + '\n')
                    
