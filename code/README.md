# File Descriptions

![Data Flow**](https://github.com/h2researchgroup/Computational-Analysis-For-Social-Science/blob/master/Dictionary%20Mapping/imgs/data%20flow%20chart%20-%20zekai%20fan%20dec%202019.png)

## 1. Scripts

1. `run_all.sh`: Shell script for automatically running the pipeline.
2. `ParseMetaFilesUpdated.py`: Python script for extracting useful information from metadata XML files and storing it in tabular form. It takes a batch of input data and produces a table for the batch.
3. `merge_metadata_result.py`: Python script for merging the metadata results from batches and combining them into a single table.
4. `split_dictionary.py`: Python script for splitting combined n-gram dictionaries into sub-dictionaries for each type of n-gram (unigram, bigram, and trigram).
5. `parse_ngram_files.py`: Python script for counting dictionary words for one type of n-gram, in batches.
6. `combine_ngram_result.py`: Python script for merging the n-gram results from batches and combining them into a single table.
7. `Combine_Meta_Ngram_Data_into_Visual.ipynb`: Jupyter notebook for merging metadata result with n-gram result, and then filtering and aggregating according to desired criteria. It produces a graph of frequencies of words in each dictionary over time.

## 2. Input Data

1. Metadata
   `jstor_data/metadata/journal-article-*.xml`: Metadata files, each corresponding to one article.
2. N-gram
   1. `jstor_data/ngram1/journal-article-*-ngram1.txt`: Lists of all unigrams and their counts in one article.
   2. `jstor_data/ngram2/journal-article-*-ngram2.txt`: Lists of all unigrams and their counts in one article.
   3. `jstor_data/ngram2/journal-article-*-ngram2.txt`: Lists of all unigrams and their counts in one article.
3. Dictionaries
   1. `Dictionaries/Culture.csv`: List of all dictionary words for "Culture".
   2. `Dictionaries/Demographic.csv`: List of all dictionary words for "Demographic".
   3. `Dictionaries/Relational.csv`: List of all dictionary words for "Relational".
4. Journal metadata
   `MetaData/journal titles & subjects 10-15 edited.csv`: Table of relevant journals, their primary subjects, and more.

## 3. Output

1. Metadata results
   `metadata_results/part*.h5`: HDF file for table as parsed by 1.2.
2. Combined metadata result
   `metadata_combined.h5`
3. Split dictionaries
   1. `dicts/Culture_*.csv`: List of dictionary words of each type of n-gram for "Culture".
   2. `dicts/Demographic_*.csv`: List of dictionary words of each type of n-gram for "Demographic".
   3. `dicts/Relational_*.csv`: List of dictionary words of each type of n-gram for "Relational".
4. N-gram results
   1. `ngram1_part*.h5`: HDF file for unigram results as parsed by 1.5.
   2. `ngram2_part*.h5`: HDF file for bigram results as parsed by 1.5.
   3. `ngram3_part*.h5`: HDF file for trigram results as parsed by 1.5.
5. Combined n-gram result
   `ngram_combined.h5`



** Data flow image online at https://i.imgur.com/gBfgTNF.png
