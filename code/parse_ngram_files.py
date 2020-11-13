"""
ARGUMENTS: python3 parse_ngram_files.py <path-to-dictionaries> <path-to-jstor-data> <which-ngram> <which-part> <how-many-parts> <output-path>
    <which-ngram>: 1, 2, or 3.
    <how-many-parts>: for parallel processing, this should be the number of workers available to run the program; 1 if not running in parallel.
    <which-part>: for parallel processing, this should be a unique number for each worker, from 1 to <how-many-parts>; 1 if not running in parallel.
USAGE: This program takes already-split dictionaries and reads in a batch of JSTOR article n-gram files to count the number of appearances of each n-gram in the dictionaries.
INPUT: 
    1. Dictionaries for Culture, Demographic, and Relational for <which-ngram>, split by the 'split_dictionary' program. 
    2. JSTOR n-gram files for <which-ngram>.
OUTPUT: A table in HDF5 format, indexed on 'file_name', consisting of the following columns:
    'ngram_<which-ngram>_count', 'culture_<which-ngram>_count', 'demographic_<which-ngram>_count', 'relational_<which-ngram>_count'.
ERROR LOG: contains the path to all files that the program skipped because of an error, if such files exist.
"""

import math
import os
import pandas as pd
import re
import sys

from tqdm import tqdm


if len(sys.argv) != 7:
    print(__doc__)
    exit()

DICT_HOME, JSTOR_HOME, NGRAM, NUM, CPU_COUNT, OUTPUT_PATH = sys.argv[1:]
NGRAM, NUM, CPU_COUNT = int(NGRAM), int(NUM), int(CPU_COUNT)

folder = os.path.join(JSTOR_HOME, 'ngram{}'.format(NGRAM))

path, dirs, files = next(os.walk(folder))
files = [os.path.join(path, file) for file in files] # Add folder name "path" as prefix to file 

NUM_EACH = math.ceil(len(files) / CPU_COUNT)
LEFT = (NUM - 1) * NUM_EACH
RIGHT = LEFT + NUM_EACH

files = files[LEFT:RIGHT]

LOG_FILE = os.path.join(OUTPUT_PATH, 'ngram{}_part{}.log'.format(NGRAM, NUM))

with open(os.path.join(DICT_HOME, 'Culture_{}.csv'.format(NGRAM)), 'r') as f:
    culture = set(f.read().splitlines())

with open(os.path.join(DICT_HOME, 'Demographic_{}.csv'.format(NGRAM)), 'r') as f:
    demographic = set(f.read().splitlines())

with open(os.path.join(DICT_HOME, 'Relational_{}.csv'.format(NGRAM)), 'r') as f:
    relational = set(f.read().splitlines())

df = pd.DataFrame(columns=[
        'file_name',
        'ngram_{}_count'.format(NGRAM),
        'culture_{}_count'.format(NGRAM),
        'demographic_{}_count'.format(NGRAM),
        'relational_{}_count'.format(NGRAM)]).set_index('file_name')

log_file = open(LOG_FILE, 'w')
logged = False

for file in tqdm(files):
    try:
        with open(file, 'r') as f:
            file_name = re.findall('journal-article-.+\.txt', file)[0][:-11]
            ngram_count = 0
            culture_count = 0
            demographic_count = 0
            relational_count = 0

            for line in f.read().splitlines():
                k, v = line.split('\t')
                ngram_count += int(v)
                if k in culture:
                    culture_count += int(v)
                if k in demographic:
                    demographic_count += int(v)
                if k in relational:
                    relational_count += int(v)

                df.loc[file_name, :] = [
                    ngram_count,
                    culture_count,
                    demographic_count,
                    relational_count]
    except:
        _ = log_file.write(file + '\n')
        logged = True

df.to_hdf(os.path.join(OUTPUT_PATH, 'ngram{}_part{}.h5'.format(NGRAM, NUM)), key='ngram', mode='w')

log_file.close()

if logged:
    print('One or more files are skipped because of an error occurred when processing them. Check {} for these files.'.format(LOG_FILE))
else:
    os.remove(LOG_FILE) # remove log if it contains no message
