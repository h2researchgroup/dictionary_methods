#!/usr/bin/env python
# coding: utf-8

'''
@authors: Zekai Fan, UC Berkeley; Deepak Ragu, UC Berkeley; Jaren Haber, PhD, Dartmouth College
@PI: Prof. Heather Haveman, UC Berkeley
#date_modified: December 2022
@contact: jhaber@berkeley.edu
@inputs: list of authors
@outputs: count of authors (citation_and_expanded_dict_count_{thisdate}.csv), where 'thisdate' is in mmddyy format 
@description: Counts references to canonical authors in articles by ngrams. To count a new list of terms or author names in the ngram files, change the list of words in the 'Update Words' section and/or change the word type to count (between 'citations' and 'terms', i.e. dictionaries), then run the script via `sudo python3 citation_count.py`. Then update the input file in merge_counts_dfs.ipynb and run all cells in that notebook.
'''


###############################################
#                  Initialize                 #
###############################################

# import packages
import os
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

cwd = os.getcwd()
root = str.replace(cwd, 'dictionary_methods/code', '')
JSTOR_HOME = root + "jstor_data"
INDICES = "../article_data/filtered_length_index.csv"

with open(INDICES, 'r') as f:
    files = f.read().split('\n')[:-1]
    files = [fp.split(',')[1] for fp in files]

    
###############################################
#                Update words                 #
###############################################

## Capture author citations
'''
words_type = 'citations'

demographic_authors = ['hannan freeman', 'barnett carroll', 'barron west', 'brüderl schüssler', 'carrol hannan', 
                       'freeman carrol', 'fichman levinthal', 'carrol']
relational_authors = ['pfeffer salancik', 'burt christman', 'pfeffer nowak', 'pfeffer']
cultural_authors = ['meyer rowan', 'dimaggio powell', 'powell dimaggio', 'oliver', 'powell', 'scott', 'weick']

ALL_WORDS = set(demographic_authors + relational_authors + cultural_authors)

word_types_list = [cultural_authors, demographic_authors, relational_authors]
'''

## Capture foundational terms

words_type = 'terms'

# Load original dictionaries
cult_orig = pd.read_csv('../dictionaries/original/cultural_original.csv', delimiter = '\n', 
                        header=None)[0].apply(lambda x: x.replace(',', ' '))
cultural_terms = cult_orig.tolist()

dem_orig = pd.read_csv('../dictionaries/original/demographic_original.csv', delimiter = '\n', 
                       header=None)[0].apply(lambda x: x.replace(',', ' '))
demographic_terms = dem_orig.tolist()

relt_orig = pd.read_csv('../dictionaries/original/relational_original.csv', delimiter = '\n', 
                        header=None)[0].apply(lambda x: x.replace(',', ' '))
relational_terms = relt_orig.tolist()

ALL_WORDS = set(demographic_terms + relational_terms + cultural_terms) # full list of dictionaries

word_types_list = [cultural_terms, demographic_terms, relational_terms]


###############################################
#          Define counting functions          #
###############################################

def generate_ngram_counts(ngram_value, counts_df, ALL_WORDS, JSTOR_HOME):
    '''Generates ngram counts by parsing through JSTOR article files, and collecting and storing the word counts 
    for the words used in the JSTOR article. 
    
    Args: 
        ngram_value (int): how many words to count: 1 = unigram, 2 = bigram, 3 = trigram
        counts_df (pd.DataFrame): the dataframe to update
        ALL_WORDS (set): list of words to count
        JSTOR_HOME (str): path to top-level folder, under which are folders with ngram data
    
    Returns:
        counts_df (pd.DataFrame): updated with columns for counts
    '''
    
    if (ngram_value > 3) or (ngram_value < 1):
        print(f"ERROR: Unable to count entries of {ngram_value} length. Please limit the word number to 1-3.")
        sys.exit()
    
    folder = os.path.join(JSTOR_HOME, 'ngram{}'.format(ngram_value))

    for file in tqdm(files):
        with open(os.path.join(folder, '{}-ngram{}.txt'.format(file, ngram_value)), 'r') as f:

            file_dict = {}

            for line in f.read().splitlines():
                k, v = line.split('\t')
                if k in ALL_WORDS:
                    file_dict[k] = int(v)
                    
            if (ngram_value == 1):
                for word in ALL_WORDS:
                    counts_df.at[file, word + "_count"] = file_dict.get(word, 0)
                
            else: # ngram_value == 2 or 3
                row = {"article_id": file}
                for word in ALL_WORDS:
                    row[word + "_count"] = file_dict.get(word, 0)

                counts_df = counts_df.append(row, ignore_index=True)
            
            counts_df = counts_df.set_index('article_id')

        
################################################
#                 Count words                  #
################################################

counts_df = pd.DataFrame(columns=["article_id"]+[(re.sub(" ", "_", word) + "_count") for word in list(ALL_WORDS)])

perspective_types = ["cultural", "demographic", "relational"]


if not words_type:
    print("ERROR: No type specified. Check the script to specify 'citations' or 'words' as counting target.")
    sys.exit()

print(f'Counting {words_type}...')

generate_ngram_counts(3, counts_df, ALL_WORDS=ALL_WORDS, JSTOR_HOME=JSTOR_HOME) # Count trigrams
generate_ngram_counts(2, counts_df, ALL_WORDS=ALL_WORDS, JSTOR_HOME=JSTOR_HOME) # Count bigrams
generate_ngram_counts(1, counts_df, ALL_WORDS=ALL_WORDS, JSTOR_HOME=JSTOR_HOME) # Count unigrams

                
#################################################
#                Save output file               #
#################################################

thisday = date.today().strftime("%m%d%y") # get current date
counts_df.to_csv(f'{words_type}_count_{thisday}.csv', index=True)

print(f"Saved counts to file.")

sys.exit() # Close script to be safe
