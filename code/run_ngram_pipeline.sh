nohup python3 split_dictionary.py ../Dictionaries ./dicts Culture &
nohup python3 split_dictionary.py ../Dictionaries ./dicts Demographic &
nohup python3 split_dictionary.py ../Dictionaries ./dicts Relational &

wait

for i in {1..44}
do
    nohup python3 parse_ngram_files.py ./dicts /vol_b/data/jstor_data 1 $i 44 ./ngram_results &
done

wait

echo "Finished parsing unigrams"

for i in {1..44}
do
    nohup python3 parse_ngram_files.py ./dicts /vol_b/data/jstor_data 2 $i 44 ./ngram_results &
done

wait

echo "Finished parsing bigrams"

for i in {1..44}
do
    nohup python3 parse_ngram_files.py ./dicts /vol_b/data/jstor_data 3 $i 44 ./ngram_results &
done

wait

echo "Finished parsing trigrams"

python3 combine_ngram_result.py ./output/ 44
