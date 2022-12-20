# Counting Dictionaries and Citations in JSTOR Text Data
Our workflow counts terms within dictionaries or list of authors within [the three contemporary organizational perspectives](https://www.jstor.org/stable/j.ctv2nv8q69): demographic, relational, and cultural.

## Quickstart
To count a new list of terms or author names in the ngram files, first change list of authors in code cell 6 of [Citation_Counts.ipynb](code/Citation_Count.ipynb) labeled *Update Words*, then follow the flow in that script and run all cells. Then update the input file and run `merge_counts_dfs.ipynb`. 

You can load the merged dataframe into your own analysis script using the below template code (for a complete example, see [calculate_pearsons.ipynb](code/calculate_pearsons.ipynb) ):
```python
df = pd.read_csv('./counts_and_subject.csv')
df["culture_author_count"] = df["cultural_author_count"]
df["edited_filename"] = df["article_id"].apply(lambda x: x[16:])
df.columns
```

## N-Gram Pipeline Description
We created a data-preparation pipeline consisting of a series of Python scripts and shell commands that takes in n-gram files and metadata provided by JSTOR along with expert-generated concept dictionaries. For each article, the JSTOR data includes files listing unigrams, bigrams, trigrams, and their counts along with a metadata file. Additionally, a journal metadata table includes fields like primary subject for each journal included in the database. The initial pipeline steps serve to parse the n-gram and metadata files in batches, then merge the results. The process of parsing and combining the n-gram files keeps a running total of counts for each concept dictionary, for each n-gram size (uni-, bi-, tri-). From the aggregated metadata table, only articles within our primary focal subject areas, 'Sociology' and 'Management & Organizational Behavior,' were retained. We joined the filtered metadata table with the n-gram counts table on a unique article identifier to generate a reduced, focused set of articles and n-gram counts. From this dataset, we calculated how much each article in each dataset in each journal engaged with each of the three perspectives. We then aggregated data to the level of the subject area and year, and generated plots of engagement over time.

## Files in repos
- Journal metadata: [`article_data/journal_titles_subjects_101519.csv`](article_data/journal_titles_subjects_101519.csv) <br>
- Names of all authors in filtered soc/mgt JSTOR dataset: [`article_data/surnames.txt`](article_data/surnames.txt) <br/>
- Term counts per core dictionary and subject: [`metadata/counts_and_subject.csv`](https://github.com/h2researchgroup/models_storage/blob/master/metadata/counts_and_subject.csv)
- For info on scripts in this workflow, see the README in the [`code/`](code/) folder

## Files on team VM
- Lists of unigrams, bigrams, trigrams, and their counts: `jstor_data/ngram[123]/journal-article-*-ngram[123].txt` <br>
- Metadata: `jstor_data/metadata/journal-article-*.xml` <br>
