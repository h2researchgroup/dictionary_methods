## N-Gram Pipeline Description
We created a data-preparation pipeline consisting of a series of Python scripts and shell commands that takes in n-gram files and metadata provided by JSTOR along with expert-generated concept dictionaries. For each article, the JSTOR data includes files listing unigrams, bigrams, trigrams, and their counts along with a metadata file. Additionally, a journal metadata table includes fields like primary subject for each journal included in the database. The initial pipeline steps serve to parse the n-gram and metadata files in batches, then merge the results. The process of parsing and combining the n-gram files keeps a running total of counts for each concept dictionary, for each n-gram size (uni-, bi-, tri-). From the aggregated metadata table, only articles within our primary focal subject areas, 'Sociology' and 'Management & Organizational Behavior,' were retained. We joined the filtered metadata table with the n-gram counts table on a unique article identifier to generate a reduced, focused set of articles and n-gram counts. From this dataset, we calculated how much each article in each dataset in each journal engaged with each of the three perspectives. We then aggregated data to the level of the subject area and year, and generated plots of engagement over time.

## File locations:
Lists of unigrams, bigrams, trigrams, and their counts: `jstor_data/ngram[123]/journal-article-*-ngram[123].txt` <br>
Metadata: `jstor_data/metadata/journal-article-*.xml` <br>
Journal metadata: `MetaData/journal titles & subjects 10-15 edited.csv` <br>
Term counts per core dictionary and subject: `counts_and_subject.csv`

## Scripts:
Parsing the N-gram files in batches: `parse_ngram_files.py` <br>
Parsing metadata files in batches: `ParseMetaFilesUpdated.py` <br>
Merge N-gram and metadata results: `combine_ngram_result.py`, `merge_metadata_result.py` <br>
Filter to only articles in primary subject areas: `Merging.py` (this has been integrated into another script) <br>
Join metadata with N-gram counts into combined articles table: `Combine_Meta_Ngram_Data_into_Visual.ipynb` <br>
Also check out: <br>
`Pipe/Dictionary_Term_Count.ipynb` <br>
`merge_counts_dfs.ipynb`

(more file/script descriptions/locations coming)
