for i in {1..44}
do
    nohup python3 ParseMetaFilesUpdated.py /vol_b/data/jstor_data $i 44 ./metadata_results/ &
done

wait

python3 merge_metadata_result.py ./metadata_results/h5/ 44 ../MetaData/journal\ titles\ \&\ subjects\ 10-15\ edited.csv ./output/metadata_combined.h5
