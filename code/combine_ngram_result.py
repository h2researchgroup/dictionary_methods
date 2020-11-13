"""
ARGUMENTS: python3 combine_ngram_result.py <path-to-ngram-results> <total-number-of-parts>
USAGE: combines all parts of n-gram results for all three types of n-gram.
"""

import pandas as pd
import sys

from os.path import join


if len(sys.argv) != 3:
    print(__doc__)
    exit()

PATH = sys.argv[1]
NUM_PARTS = int(sys.argv[2])

unigram = pd.DataFrame(columns=['ngram_1_count', 'culture_1_count', 'demographic_1_count', 'relational_1_count'])
unigram.index.name = 'file_name'

for i in range(1, NUM_PARTS + 1):
    unigram = unigram.append(pd.read_hdf(join(PATH, 'ngram1_part{}.h5').format(i)), ignore_index=True)

bigram = pd.DataFrame(columns=['ngram_2_count', 'culture_2_count', 'demographic_2_count', 'relational_2_count'])
bigram.index.name = 'file_name'

for i in range(1, NUM_PARTS + 1):
    bigram = bigram.append(pd.read_hdf(join(PATH, 'ngram2_part{}.h5').format(i)), ignore_index=True)

trigram = pd.DataFrame(columns=['ngram_3_count', 'culture_3_count', 'demographic_3_count', 'relational_3_count'])
trigram.index.name = 'file_name'

for i in range(1, NUM_PARTS + 1):
    trigram = trigram.append(pd.read_hdf(join(PATH, 'ngram3_part{}.h5').format(i)), ignore_index=True)

combined = unigram.join(bigram).join(trigram)

combined.to_hdf(join(PATH, 'ngram_combined.h5'), key='ngram', mode='w')
