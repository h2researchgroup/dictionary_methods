"""
ARGUMENTS: python3 ParseMetaFilesUpdated.py <path-to-jstor-data> <which-part> <how-many-parts> <output-path>
    <how-many-parts>: for parallel processing, this should be the number of workers available to run the program; 1 if not running in parallel.
    <which-part>: for parallel processing, this should be a unique number for each worker, from 1 to <how-many-parts>; 1 if not running in parallel.
USAGE: This program takes already-split dictionaries and reads in a batch of JSTOR article n-gram files to count the number of appearances of each n-gram in the dictionaries.
INPUT: JSTOR metadata files.
OUTPUT: A table in HDF5 format, indexed on 'file_name', consisting of 18 columns.
"""

import math
import os
import re
import sys
from tqdm import tqdm
from xml.etree import ElementTree as ET

import pandas as pd


# check if improper number of arguments; if so, return instructions and quit
if len(sys.argv) != 5:
    print(__doc__)
    exit()

# read in arguments from command line
JSTOR_HOME, NUM, NUM_CPUS, OUTPATH = sys.argv[1:]
NUM, NUM_CPUS = int(NUM), int(NUM_CPUS)

METADATA_HOME = os.path.join(JSTOR_HOME, 'metadata/')
path, dirs, files = next(os.walk(METADATA_HOME))
files = [(path + file) for file in files] # Add folder name "path" as prefix to file

NUM_EACH = math.ceil(len(files) / NUM_CPUS)
LEFT = (NUM - 1) * NUM_EACH
RIGHT = LEFT + NUM_EACH

files = files[LEFT:RIGHT]

def add(elem, attrs):
    # TO DO: Filter by article-type?

    elements = attrs['elements']
    surnames = attrs['surname']
    given_names = attrs['given-names']
    tag = elem.tag
    if tag in attrs['df_cols']:
        if tag == 'journal-id':
            tag = 'journal_id'
        elif tag == 'article':
            article_attrs = elem.attrib
            article_type = article_attrs['article-type']
            tag = 'type'
            elem.text = article_type
        elif tag =='journal-title':
            tag = 'journal_title'
        elif tag == 'article-id':
            tag = 'article_id'
        elif tag == 'article-name':
            tag = 'article_name'
        elif tag == 'surname':
            if type(elem.text) == 'str':
                surnames.append(elem.text.split(',')[0])
            else:
                surnames.append('None')
            elem.text = surnames
        elif tag == 'given-names':
            tag = 'given_names'
            given_names.append(elem.text)
            elem.text = given_names
        elif tag == 'issue-id':
            tag = 'issue_id'
        elif tag == 'ns1:ref':
            tag = 'jstor_url'
        elif tag == 'p':
            tag = 'abstract'

#        if tag not in elements:
#            elements[tag] = pd.Series([elem.text])
#        else:
#            elements[tag].append(pd.Series([elem.text]), ignore_index=True)
        len_list = len(elements[tag])
        elements[tag][len_list - 1] = elem.text

    for child in elem.findall('*'):
        add(child, attrs)

def xml2df(xml_files):
    """Transforms XML files into a Pandas DataFrame.

    Args: 
        files: list of complete file paths

    Returns:
        df: DataFrame with article info"""

    all_records = {'type':[], 'journal_id':[], 'journal_title':[], 'issn':[], 'article_id':[], 'article_name':[], 'given_names':[], 'surname':[], 'day':[], 'month':[], 'year':[], 'volume':[], 'issue':[], 'issue_id':[], 'fpage':[], 'lpage':[], 'jstor_url':[], 'abstract':[]}
    attrs = {}
    attrs['elements'] = all_records
    attrs['surname'] = []
    attrs['given-names'] = []
    attrs['df_cols'] = ['article', 'journal-id', 'journal-title', 'issn', 'article-id', 'article-name', 'given-names', 'surname', 'day', 'month', 'year', 'volume', 'issue', 'issue-id', 'fpage', 'lpage', 'ns1:ref', 'p']

    for file in tqdm(xml_files):
        with open(file, 'rb') as f:
            t = ET.parse(f) # element tree
            root = t.getroot()
            for record in all_records:
                all_records[record].append('None')
            add(root, attrs)

    #print(all_records)
    print ('Start creating data frame')
    df = pd.DataFrame(all_records)
    return df

# This is definitely NOT a good practice. However, I'm trying not to break what's running properly.
def amend_df(df, files):
    file_names = []
    jstor_urls = []
    abstracts = []
    article_names = []

    for file in tqdm(files):
        file_names.append(re.findall('journal-article-.+\.xml', file)[0][:-4])
        with open(file, 'rb') as f:
            t = ET.parse(f) # element tree
            root = t.getroot()

            try:
                jstor_urls.append(root.find('front').find('article-meta').find('self-uri').items()[0][1])
            except:
                jstor_urls.append('None')

            try:
                abstracts.append(root.find('front').find('article-meta').find('abstract').find('p').text)
            except:
                abstracts.append('None')

            try:
                article_names.append(root.find('front').find('article-meta').find('title-group').find('article-title').text)
            except:
                article_names.append('None')

    df.loc[:, 'file_name'] = file_names
    df.loc[:, 'jstor_url'] = jstor_urls
    df.loc[:, 'abstract'] = abstracts
    df.loc[:, 'article_name'] = article_names

print('Start processing')
df = xml2df(files)
print('Start amending')
amend_df(df, files)

# df.to_pickle('pickles/part{}.pickle'.format(n))
df.set_index('file_name').to_hdf(os.path.join(OUTPATH, 'part{}.h5'.format(NUM)), key='metadata', mode='w')
