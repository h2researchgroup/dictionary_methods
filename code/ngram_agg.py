import os
import sys
from collections import Counter

from tqdm import tqdm


JSTOR_HOME, NGRAM, INDICES, OUTPUT_PATH = sys.argv[1:]
NGRAM = int(NGRAM)

folder = os.path.join(JSTOR_HOME, 'ngram{}'.format(NGRAM))

with open(INDICES, 'r') as f:
    files = f.read().split('\n')[:-1]

c = Counter()

print('Begin processing.')

for file in tqdm(files):
    try:
        with open(os.path.join(folder, '{}-ngram{}.txt'.format(file, NGRAM)), 'r') as f:
            d = {}
            for line in f.read().splitlines():
                k, v = line.split('\t')
                d[k] = int(v)
            c.update(d)
    except:
        print('Encountered an error when processing', file)

to_write = ''
for x in c.items():
    to_write += '{} {}\n'.format(x[0], x[1])

with open(os.path.join(OUTPUT_PATH, 'ngram{}_agg.txt'.format(NGRAM)), 'w') as f:
    f.write(to_write)
