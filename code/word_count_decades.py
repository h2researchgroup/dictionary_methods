#!/usr/bin/env python
# coding: utf-8

'''
@authors: Jaren Haber, PhD, Dartmouth College; Zekai Fan, UC Berkeley; Deepak Ragu, UC Berkeley
@PI: Prof. Heather Haveman, UC Berkeley
@date_modified: February 2023
@contact: jhaber@berkeley.edu
@inputs: list of authors OR list of terms, list of decade-specific article filepaths 
@outputs: count of authors (citation_and_expanded_dict_count_{thisdate}.csv), where 'thisdate' is in mmddyy format 
@usage: python3 word_count_decades.py 1971-1981 # or: 1982-1992, 1993-2003, 2004-2014 (quotation marks optional)
@description: Counts mentions of individual words or authors--NOT separated by perspective as in previous versions--in articles by using ngram files ACROSS A SINGLE DECADE. To count a new list of terms or author names in the ngram files for a specific decade, change the list of words in the 'Update Words' section, change the `DECADE` parameter below (under 'Define file paths' section), and/or change the word type to count (between 'citations' and 'terms', i.e. dictionaries), then run the script. 
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
INDICES_HOME = join(root, 'models_storage/article_lists_jstor')
JSTOR_HOME = join(root, 'jstor_data')

# get decade-specific list of JSTOR filepaths (INDICES)
INDICES_LIST = [file for file in listdir(INDICES_HOME) if isfile(join(INDICES_HOME, file))] # files only
DECADE = str(sys.argv[1]) # note hyphen in middle
assert DECADE.__contains__('-'), 'Wrong format for DECADE: must contain a hypen, e.g. 1971-1981 (quotation marks optional)'
INDICES = [file for file in INDICES_LIST if ('_' + DECADE + '_') in file]
assert len(INDICES) == 1, f'Found {str(len(INDICES))} filepath lists in {INDICES_HOME} to count in {str(DECADE)}, expected just 1'
INDICES = join(INDICES_HOME, INDICES[0]) # get full filepath

# get full list of filepaths
with open(INDICES, 'r') as f:
    files = f.read().split('\n')[1:]
    files = [fp.split(',')[1] for fp in files[:20]] # ignore index; get filepath only

    
###############################################
#                Update words                 #
###############################################

## Capture author citations
'''
words_type = 'citations' # set to count citations

dem = ['hannan freeman', 'barnett carroll', 'barron west', 'brüderl schüssler', 'carrol hannan', 
                       'freeman carrol', 'fichman levinthal', 'carrol']
relt = ['pfeffer salancik', 'burt christman', 'pfeffer nowak', 'pfeffer']
cult = ['meyer rowan', 'dimaggio powell', 'powell dimaggio', 'oliver', 'powell', 'scott', 'weick']

ALL_WORDS = dem + relt + cult # full list of authors
'''

## Capture foundational terms

words_type = 'terms' # set to count terms

# Load decade-specific dictionaries
DECADE_UNDER = DECADE.replace('-', '_')
dem = pd.read_csv(join(DICTS_HOME, f'expanded_decades/demographic_{DECADE_UNDER}.txt'), delimiter = '\n', 
                       header=None)[0].apply(lambda word: word.replace(',', ' ')).tolist()
relt = pd.read_csv(join(DICTS_HOME, f'expanded_decades/relational_{DECADE_UNDER}.txt'), delimiter = '\n', 
                        header=None)[0].apply(lambda word: word.replace(',', ' ')).tolist()
cult = pd.read_csv(join(DICTS_HOME, f'expanded_decades/cultural_{DECADE_UNDER}.txt'), delimiter = '\n', 
                        header=None)[0].apply(lambda word: word.replace(',', ' ')).tolist()

ALL_WORDS = dem + relt + cult # full list of dictionaries

# make word:perspective dictionary for output
ALL_WORDS_PERSPECTIVES = ['demographic' for term in dem] + \
                         ['relational' for term in relt] + \
                         ['cultural' for term in cult] # list of perspectives per term in ALL_WORDS
assert len(ALL_WORDS) == len(ALL_WORDS_PERSPECTIVES), f'Full list of terms ({str(len(ALL_WORDS))} terms) does match list of perspectives in order ({str(len(ALL_WORDS_PERSPECTIVES))} entries)'
WORDS_PERSPECTIVES_DICT = {word: persp for word, persp in list(zip(ALL_WORDS, ALL_WORDS_PERSPECTIVES))}


###############################################
#          Define counting functions          #
###############################################

def generate_ngram_counts(ngram_value:int, counts_df:pd.DataFrame(), files:list, ALL_WORDS:list, JSTOR_HOME:str):
    '''Generates ngram counts by parsing through JSTOR article files, and collecting and storing the word counts 
    for the words used in the JSTOR article. 
    
    Args: 
        ngram_value (int): how many words to count: 1 = unigram, 2 = bigram, 3 = trigram
        counts_df (pd.DataFrame): the dataframe to update
        files (list): list of all article filepaths
        ALL_WORDS (list): list of words to count
        JSTOR_HOME (str): path to top-level folder, under which are folders with ngram data
    
    Returns:
        counts_df (pd.DataFrame): updated with columns for counts
    '''
    
    # Check that ngram_value between 1 and 3
    assert (ngram_value>=1 and ngram_value<=3), f"Unable to count entries of {ngram_value} length. Please limit the word number to 1-3."
        
    # Filter ALL_WORDS to length of ngram_value (to improve counting speed)
    ALL_WORDS = [term for term in ALL_WORDS if len(term.split())==ngram_value]
    
    folder = join(JSTOR_HOME, f'ngram{ngram_value}')

    for file in tqdm(files):
        with open(join(folder, f'{file}-ngram{ngram_value}.txt'), 'r') as f:

            file_dict = {} # initialize dict for relevant vocab from article

            for line in f.read().splitlines():
                word, count = line.split('\t')
                if word in ALL_WORDS:
                    file_dict[word] = int(count)
                    
            # Create empty dict for row, with article id
            row = {key: None for key in ALL_WORDS}
            row['article_id'] = file #row = {"article_id": file}
            
            # For each word, assign counts to row
            for word_idx in range(len(ALL_WORDS)):
                row[ALL_WORDS[word_idx]] = file_dict.get(ALL_WORDS[word_idx], 0)
            
            counts_df = counts_df.append(row, ignore_index=True) # add row for article to DF
    
    return counts_df

        
################################################
#                 Count words                  #
################################################

counts_df = pd.DataFrame(columns=["article_id"]+ALL_WORDS)

assert words_type, "No type specified. Check the script to specify 'citations' or 'words' as counting target."

print(f'Counting {words_type}...')

counts_df = generate_ngram_counts(3, counts_df, files=files, ALL_WORDS=ALL_WORDS, JSTOR_HOME=JSTOR_HOME) # Count trigrams

counts_df = generate_ngram_counts(2, counts_df, files=files, ALL_WORDS=ALL_WORDS, JSTOR_HOME=JSTOR_HOME) # Count bigrams
counts_df = counts_df.reset_index(drop = False).groupby('article_id').sum() # collapse to save space

counts_df = generate_ngram_counts(1, counts_df, files=files, ALL_WORDS=ALL_WORDS, JSTOR_HOME=JSTOR_HOME) # Count unigrams
counts_df = counts_df.reset_index(drop = False).groupby('article_id').sum().drop(columns=['level_0']) # collapse so one article = one row


################################################
#       Transpose terms from cols to rows      #
################################################

counts_df = counts_df.sum(axis=0).drop(index='index').reset_index(drop=False) # sum across articles
#counts_df = counts_df.transpose().reset_index(drop=False) # make terms into rows
counts_df.columns = ['term', 'count']
counts_df['count'] = counts_df['count'].astype(int) # cast as int

# Create new columns for proportion of highest count and perspective for a given term
counts_df['prop_max'] = (counts_df['count']*100)/counts_df['count'].max().astype(float) # calculate percentage of highest count, make float
counts_df['perspective'] = counts_df.term.apply(lambda term: WORDS_PERSPECTIVES_DICT[term]) # use term:persp dictionary to get persp for each row

counts_df.sort_values(['perspective', 'count'], inplace=True)

                
#################################################
#                Save output file               #
#################################################

thisday = date.today().strftime("%m%d%y") # get current date
counts_df.to_csv(join(DATA_HOME, f'{words_type}_count_{DECADE}_{thisday}.csv'), index=False)

print(f"Saved counts to file.")

sys.exit() # Close script to be safe
