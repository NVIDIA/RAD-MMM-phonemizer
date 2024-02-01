# phonemizer-internal
This repository provides helper functionality to phonemize textual data from multiple language. We utilize (only USE and NOT MODIFY) the tool phonemizer (https://github.com/bootphon/phonemizer/) with GPL License to phonemize the textual data.

There are primarily 2 different utilities in this repo:
1. constructing phoneme lookup dictionary for multiple languages using phonemizer. The output is dictionary per language (https://drive.google.com/drive/folders/1woNCODwXh9aHu7Fd6b4Jo42aL7f5RFZg?usp=sharing) using generate_language_dict.py
Example usage below

```
python3 generate_language_dict.py -w wikidict-wordlist/data/en-wordlist_wiki-01.txt -l en_US -o assets/ -tp_config text_processor_config.json 
```

2. phonemizing a filelist of dataset comprising of multiple languages (eg: https://drive.google.com/drive/folders/1tALLXAR-quig3yAvKcCW12oAKWgV9w_2?usp=sharing) using phonemize_text.py
Example usage:

```
python3 phonemize_text.py -c configs/RADMMM_opensource_16khz_data_config.yaml -o output/
```

## OSS Used:
1. Phonemizer (https://github.com/bootphon/phonemizer) with GPL License.
2. Wiki word data lists (https://github.com/open-dict-data/wikidict-wordlist) with https://creativecommons.org/publicdomain/zero/1.0/ License.

## Authors and acknowledgment
Rohan Badlani (rbadlani@nvidia.com)

## License
GPL License