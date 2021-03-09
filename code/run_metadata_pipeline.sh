for i in {1..44}
do
    nohup python3 ParseMetaFilesUpdated.py /vol_b/data/jstor_data $i 44 /vol_b/data/models_storage/metadata/ &
done

wait

python3 merge_metadata_result.py /vol_b/data/models_storage/metadata/ 44 ../metadata/journal\ titles\ \&\ subjects\ 10-15\ edited.csv /vol_b/data/models_storage/metadata/metadata_combined.h5