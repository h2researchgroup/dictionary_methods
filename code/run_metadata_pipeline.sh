for i in {1..44}
do
    nohup python3 ParseMetaFilesUpdated.py /vol_b/data/jstor_data $i 44 /vol_b/data/models_storage/metadata/temp/ &
done

wait

python3 merge_metadata_result.py /vol_b/data/models_storage/metadata/temp/ 44 /vol_b/data/models_storage/metadata/journal_titles_subjects_h2.csv /vol_b/data/models_storage/metadata/metadata_combined_030921.h5