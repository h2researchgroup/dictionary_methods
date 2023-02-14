#!/usr/bin/env python
# coding: utf-8

'''
@authors: Jaren Haber, PhD, Dartmouth College; Zekai Fan, UC Berkeley; Deepak Ragu, UC Berkeley
@PI: Prof. Heather Haveman, UC Berkeley
@date_modified: February 2023
@contact: jhaber@berkeley.edu
@inputs: list of authors OR list of terms per perspective, list of article filepaths 
@outputs: count of authors ((citations_by_persp|dicts)_count_{thisdate}.csv), where 'thisdate' is in mmddyy format 
@usage: run `python3 dict_count_all.py` from within `dictionary_methods/code`
@description: Counts mentions of perspectives--summed over individual words or authors--in articles by using ngram files ACROSS A SINGLE DECADE. To count a new list of terms or author names in the ngram files, change the list of words in the 'Update Words' section and/or change the word type to count (between 'citations' and 'terms', i.e. dictionaries), then run the script. 
'''


###############################################
#                  Initialize                 #
###############################################

# import packages
from os import getcwd, listdir
from os.path import isfile, join
import csv
import pandas as pd
import numpy as np
import re
import sys
from datetime import date
from tqdm import tqdm # Shows progress over iterations, including in pandas via `df.progress_apply`
from multiprocessing import Pool, cpu_count; cores = cpu_count() # count cores
from functools import partial


###############################################
#              Define file paths              #
###############################################

cwd = getcwd()
root = str.replace(cwd, 'dictionary_methods/code', '')
DICTS_HOME = join(root, 'dictionary_methods/dictionaries')
DATA_HOME = join(root, 'dictionary_methods/article_data')
JSTOR_HOME = join(root, 'jstor_data')
METADATA = join(root, 'models_storage/metadata/metadata_cleaned_02142023.pkl')
INDICES_HOME = join(root, 'models_storage/article_lists_jstor')

# get decade-specific list of JSTOR filepaths (INDICES)
INDICES_LIST = [file for file in listdir(INDICES_HOME) if isfile(join(INDICES_HOME, file))] # files only
DECADE = str(sys.argv[1]) # note hyphen in middle
assert DECADE.__contains__('-'), 'Wrong format for DECADE: must contain a hypen, e.g. 1971-1981 (quotation marks optional)'
assert DECADE in ['1971-1981', '1982-1992', '1993-2003', '2004-2014'], f'Cannot parse decade of {DECADE}; only acceptable ranges are: 1971-1981, 1982-1992, 1993-2003, 2004-2014'
INDICES = [file for file in INDICES_LIST if ('_' + DECADE + '_') in file]
assert len(INDICES) == 1, f'Found {str(len(INDICES))} filepath lists in {INDICES_HOME} to count in {str(DECADE)}, expected just 1'
INDICES = join(INDICES_HOME, INDICES[0]) # get full filepath

with open(INDICES, 'r') as f:
    files = f.read().split('\n')[1:-1]
    files = [fp.split(',')[1] for fp in files]

    
###############################################
#                Update words                 #
###############################################

## Capture author citations
'''
words_type = 'citations_by_persp'

demographic_authors = ['hannan freeman', 'barnett carroll', 'barron west', 'brüderl schüssler', 'carrol hannan', 
                       'freeman carrol', 'fichman levinthal', 'carrol']
relational_authors = ['pfeffer salancik', 'burt christman', 'pfeffer nowak', 'pfeffer']
cultural_authors = ['meyer rowan', 'dimaggio powell', 'powell dimaggio', 'oliver', 'powell', 'scott', 'weick']

ALL_WORDS = set(demographic_authors + relational_authors + cultural_authors) # full list of authors
ALL_WORDS_COUNTS = [(re.sub(" ", "_", word) + "_count") for word in list(ALL_WORDS)] # cleaned version
'''

## Capture foundational terms

words_type = 'dicts' # set to count dictionaries, one per perspective

# Load decade-specific dictionaries
DECADE_UNDER = DECADE.replace('-', '_')
dem = pd.read_csv(join(DICTS_HOME, f'expanded_decades/demographic_{DECADE_UNDER}.txt'), delimiter = '\n', 
                       header=None)[0].apply(lambda word: word.replace(',', ' ')).tolist()
relt = pd.read_csv(join(DICTS_HOME, f'expanded_decades/relational_{DECADE_UNDER}.txt'), delimiter = '\n', 
                        header=None)[0].apply(lambda word: word.replace(',', ' ')).tolist()
cult = pd.read_csv(join(DICTS_HOME, f'expanded_decades/cultural_{DECADE_UNDER}.txt'), delimiter = '\n', 
                        header=None)[0].apply(lambda word: word.replace(',', ' ')).tolist()

ALL_WORDS = dem + relt + cult # full list of words in dictionaries; note underscores to separate ngrams
ALL_DICTS = [dem, relt, cult] # list of dictionaries
DICT_NAMES = ['demographic', 'relational', 'cultural'] # names of dictionaries

assert len(ALL_DICTS) == len(DICT_NAMES), f'Must have same number of dictionaries (currently {str(len(ALL_DICTS))}) and dictionary names (currently {str(len(DICT_NAMES))}).'

# make word:perspective dictionary for output
#ALL_WORDS_PERSPECTIVES = ['demographic' for term in dem] + \
#                         ['relational' for term in relt] + \
#                         ['cultural' for term in cult] # list of perspectives per term in ALL_WORDS
#assert len(ALL_WORDS) == len(ALL_WORDS_PERSPECTIVES), f'Full list of terms ({str(len(ALL_WORDS))} terms) does match list of perspectives in #order ({str(len(ALL_WORDS_PERSPECTIVES))} entries)'
#WORDS_PERSPECTIVES_DICT = {word: persp for word, persp in list(zip(ALL_WORDS, ALL_WORDS_PERSPECTIVES))}


###############################################
#          Define counting functions          #
###############################################

def generate_ngram_counts(ngram_value:int, files:list, 
                          ALL_WORDS:list, ALL_DICTS:list, DICT_NAMES:list, 
                          JSTOR_HOME:str):
    '''Generates ngram counts by parsing through JSTOR article files, and collecting and storing the word counts 
    for the words used in the JSTOR article. 
    
    Args: 
        ngram_value (int): how many words to count: 1 = unigram, 2 = bigram, 3 = trigram
        files (list): list of all article filepaths
        ALL_WORDS (list): list of all words to count (regardless of whether unigram, bigram, etc.)
        ALL_DICTS (list): list of lists, each list is a dictionary (list of str) for a perspective
        DICT_NAMES (list): list of strings, each of which references a perspective (same order as previous two params)
        JSTOR_HOME (str): path to top-level folder, under which are folders with ngram data
    
    Returns:
        counts_df (pd.DataFrame): DataFrame with columns for words, values for counts
    '''
    
    # Check that ngram_value between 1 and 3
    assert (ngram_value>=1 and ngram_value<=3), f"Unable to count entries of {ngram_value} length. Please limit the word number to 1-3."
        
    # Filter ALL_WORDS to length of ngram_value (to improve counting speed)
    terms = [term for term in ALL_WORDS if len(term.split('_'))==ngram_value] # underscores separate words
    
    # Initialize DataFrame to store counting results
    counts_df = pd.DataFrame(columns=['article_id']+[(dict_name+'_count') for dict_name in DICT_NAMES])
    
    folder = join(JSTOR_HOME, f'ngram{ngram_value}')

    for file in tqdm(files):
        with open(join(folder, f'{file}-ngram{ngram_value}.txt'), 'r') as f:

            file_dict = {} # initialize dict for relevant vocab from article
            
            # Add to file_dict the count for each word from ALL_WORDS that are of length ngram_value
            for line in f.read().splitlines():
                word, count = line.split('\t')
                word = word.replace(' ', '_') # to match dictionary format, use underscores to separate words
                if word in terms:
                    file_dict[word] = int(count)
            
            # Sum word frequencies for each perspective/dict
            term_sums = [sum([file_dict.get(term, 0) for term in DICT]) for DICT in ALL_DICTS] 
            
            # Create dict for row, with article id:file and dict:count
            row = {"article_id": file}
            for i in range(len(ALL_DICTS)): # for each perspective/dictionary...
                row[DICT_NAMES[i] + '_count'] = term_sums[i] # assign total term count as value
                    
            counts_df = counts_df.append(row, ignore_index=True) # add row for article to DF
    
    return counts_df

        
################################################
#                 Count words                  #
################################################

assert words_type in ['dicts', 'citations_by_persp'], "Wrong 'words_type' specified as counting target. Options are 'citations_by_persp' or 'dicts'."
print(f'Counting {words_type}...')

trigram_counts_df = generate_ngram_counts(3, files=files, ALL_WORDS=ALL_WORDS, 
                                          ALL_DICTS=ALL_DICTS, DICT_NAMES=DICT_NAMES, 
                                          JSTOR_HOME=JSTOR_HOME) # Count trigrams

bigram_counts_df = generate_ngram_counts(2, files=files, ALL_WORDS=ALL_WORDS, 
                                         ALL_DICTS=ALL_DICTS, DICT_NAMES=DICT_NAMES, 
                                         JSTOR_HOME=JSTOR_HOME) # Count bigrams
counts_df = pd.concat([trigram_counts_df, bigram_counts_df], axis=0) # merge bigram + trigram counts

unigram_counts_df = generate_ngram_counts(1, files=files, ALL_WORDS=ALL_WORDS, 
                                          ALL_DICTS=ALL_DICTS, DICT_NAMES=DICT_NAMES, 
                                          JSTOR_HOME=JSTOR_HOME) # Count unigrams
counts_df = pd.concat([counts_df, unigram_counts_df], axis=0) # merge unigram counts with the rest

counts_df = counts_df.loc[:,~counts_df.columns.duplicated()] # remove duplicate columns, e.g. 'article_id'
counts_df = counts_df.groupby('article_id').sum().reset_index(drop=False) # add up all ngrams for each article


################################################
#        Merge counts with article data        #
################################################

meta_df = pd.read_pickle(METADATA).drop(columns='abstract') # load metadata, cut abstract due to merging issues
counts_df['doi'] = counts_df['article_id'].apply(lambda fname: fname.split('-')[-1]) # get DOI from file name, e.g. 'journal-article-10.2307_2065002' -> '10.2307_2065002'
counts_df = pd.merge(counts_df, meta_df, how='left', on='doi')


#################################################
#                Save output file               #
#################################################

thisday = date.today().strftime("%m%d%y") # get current date
counts_df.to_csv(join(DATA_HOME, f'{words_type}_count_{DECADE}_{thisday}.csv'), index=False)

print(f"Saved counts to file.")

sys.exit() # Close script to be safe
