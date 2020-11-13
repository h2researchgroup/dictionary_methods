import numpy as np
import pandas as pd
import sys

from os.path import join


METADATA_HOME, NUM_PARTS, JOURNAL_META_FILE, OUTFILE = sys.argv[1:]

data = pd.DataFrame()

for i in range(1, int(NUM_PARTS) + 1):
    df = pd.read_hdf(join(METADATA_HOME, 'part{}.h5'.format(i)))
    data = data.append(df)

data.loc[data.journal_title == 'Industrial and Labor Relations Review', 'journal_title'] = 'ILR Review'
data.loc[data.journal_title == 'Journal for East European Management Studies', 'journal_title'] = 'Journal of East European Management Studies'

journals = pd.read_csv(JOURNAL_META_FILE)

s1 = r'Max Weber Studies	1470-8078	https://www.jstor.org/journal/maxweberstudies	Sociology	2000-10-01 - 2018-01-01											10/1/00 0:00	2019			'
s2 = r'Review of Religious Research	0034-673X	https://www.jstor.org/journal/revirelirese	Religion	1959-06-01 - 2015-12-01											6/1/59 0:00	2015			'
s3 = r'The Polish Sociological Bulletin	0032-2997	https://www.jstor.org/journal/polisocibull	Sociology	1961-05-01 - 1992-12-01	Social Sciences 	 Sociology									5/1/61 0:00	1992	polisocirevi		'

to_append = pd.DataFrame([s1.split('\t'), s2.split('\t'), s3.split('\t')], columns=journals.columns)
to_append = to_append.replace('', np.nan)

journals = journals.append(to_append, ignore_index=True)

merged = data.reset_index().merge(
    journals.loc[:, ['publication_title', 'primary_subject']],
    how='left',
    left_on='journal_title',
    right_on='publication_title').set_index('file_name')

merged = merged.drop('publication_title', axis=1) # no longer need this column
merged = merged[~merged.primary_subject.isnull()] # drop if has no journal, or journal has no primary subject
merged.loc[~merged.primary_subject.isin(['Sociology', 'Management & Organizational Behavior']), 'primary_subject'] = 'Other' # rename primary subject as "other" if not in sociology/OB

merged.to_hdf(OUTFILE, key='metadata', mode='w')
