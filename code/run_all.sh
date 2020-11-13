DIR="dicts/"
if [ -d "$DIR" ]; then
  echo "${DIR} already exists"
else
  echo "Making ${DIR}"
  mkdir ${DIR}
fi

DIR="output/"
if [ -d "$DIR" ]; then
  echo "${DIR} already exists"
else
  echo "Making ${DIR}"
  mkdir ${DIR}
fi

DIR="metadata_results/"
if [ -d "$DIR" ]; then
  echo "${DIR} already exists"
else
  echo "Making ${DIR}"
  mkdir ${DIR}
fi

DIR="ngram_results/"
if [ -d "$DIR" ]; then
  echo "${DIR} already exists"
else
  echo "Making ${DIR}"
  mkdir ${DIR}
fi

for i in {1..44}
do
    nohup python3 ParseMetaFilesUpdated.py /vol_b/data/jstor_data $i 44 ./metadata_results/ &
done

wait

echo "Finished parsing metadata files"

python3 merge_metadata_result.py ./metadata_results/ 44 ../MetaData/journal\ titles\ \&\ subjects\ 10-15\ edited.csv ./metadata_combined.h5

echo "Finished merging metadata files"

nohup python3 split_dictionary.py ../Dictionaries ./dicts Culture &
nohup python3 split_dictionary.py ../Dictionaries ./dicts Demographic &
nohup python3 split_dictionary.py ../Dictionaries ./dicts Relational &

wait

echo "Finished splitting dictionaries"

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

python3 combine_ngram_result.py ./ 44

echo "Finished merging ngram results"
