import sys

from os.path import join

PATH = sys.argv[1]
OUTPATH = sys.argv[2]
DICT = sys.argv[3]

ngrams = ['', '', '']

with open(join(PATH, '{}.csv'.format(DICT)), 'r') as f:
    for line in f.read().splitlines():
        ngrams[line.count(',')] += line + '\n'

for i in range(3):
    with open(join(OUTPATH, '{}_{}.csv'.format(DICT, i + 1)), 'w') as f:
        f.write(ngrams[i])
