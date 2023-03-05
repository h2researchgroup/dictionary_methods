'''

@title: Similarity calculations for expanded dictionaries 
@author: Nancy Xu, UC Berkeley
@coauthors:  Jaren Haber, PhD, Dartmouth College; Prof. Heather Haveman, UC Berkeley
@contact: yinuoxu54@berkeley.edu
@project: Computational Literature Review of Organizational Scholarship
@repo: https://github.com/h2researchgroup/classification/
@date: March 5, 2023
@description: Output csv with the 500 closest words or refined words per dict/time period, with each word's cosine distance from that dict, that word's overall frequency, and a tuple including (a) each of the 3 closest terms in seed dictionary and (b) the cosine distance from that term to the focal term.
@example command: python3 get_cos_sim_dicts_df.py -w "../.." -o "./out"

'''

import gensim
from gensim.models import KeyedVectors
import pandas as pd
import sklearn
import sklearn.metrics
import numpy as np
import os
import argparse


parser = argparse.ArgumentParser()


parser.add_argument("-o", "--output_dir", help = "Show Output" )
parser.add_argument("-w", "--work_dir", help = "Show Output" )


args = parser.parse_args()

work_dir = str(args.work_dir)
output_dir = str(args.output_dir)

m1 = KeyedVectors.load(work_dir+'/models_storage/w2v_models/word2vec_1971-1981_phrased_filtered_enchant_orgdict_300d_10w_020423.bin')
m2 = KeyedVectors.load(work_dir+'/models_storage/w2v_models/word2vec_1982-1992_phrased_filtered_enchant_orgdict_300d_10w_020423.bin')
m3 = KeyedVectors.load(work_dir+'/models_storage/w2v_models/word2vec_1993-2003_phrased_filtered_enchant_orgdict_300d_10w_020423.bin')
m4 = KeyedVectors.load(work_dir+'/models_storage/w2v_models/word2vec_2004-2014_phrased_filtered_enchant_orgdict_300d_10w_020423.bin')
ma =  KeyedVectors.load(work_dir+'/models_storage/w2v_models/word2vec_ALLYEARS_phrased_filtered_enchant_orgdict_300d_10w_020423.bin')


cult_core = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/core/cultural_core.csv', header=None)[0].apply(lambda x: x.replace(' ', '_')))
dem_core = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/core/demographic_core.csv', header=None)[0].apply(lambda x: x.replace(' ', '_')))
relt_core = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/core/relational_core.csv', header=None)[0].apply(lambda x: x.replace(' ', '_')))


cult_expanded_1 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/cultural_1971_1981.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
dem_expanded_1 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/demographic_1971_1981.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
relt_expanded_1 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/relational_1971_1981.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))


cult_expanded_2 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/cultural_1982_1992.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
dem_expanded_2 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/demographic_1982_1992.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
relt_expanded_2 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/relational_1982_1992.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))

cult_expanded_3 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/cultural_1993_2003.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
dem_expanded_3 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/demographic_1993_2003.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
relt_expanded_3 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/relational_1993_2003.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))

cult_expanded_4 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/cultural_2004_2014.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
dem_expanded_4 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/demographic_2004_2014.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))
relt_expanded_4 = list(pd.read_csv(work_dir+'/dictionary_methods/dictionaries/expanded_decades/relational_2004_2014.txt', header=None)[0].apply(lambda x: x.replace(' ', '_')))

def remove_terms(seed_lst, m):
    for i in range(5):
        for word in seed_lst:
            try: 
                if m.wv.key_to_index[word] > 0:
                    pass
            except:
                    seed_lst.remove(word)
                    print("Removed " + str(word) + " from  dictionary.")
        for word in seed_lst:
            try: 
                if m.wv.key_to_index[word] > 0:
                    pass
            except:
                    seed_lst.remove(word)
                    print("Removed " + str(word) + " from  dictionary.")


    print("Length of culture dictionary filtered into vector space:", len(seed_lst))
    return seed_lst


def get_cos_sim_w_core(expanded_words,core_words, model):
  avg_cos_sims=[]
  top3_tuple_lst = []
  for w1 in expanded_words:
    try:
        sims_with_core_terms = sklearn.metrics.pairwise.cosine_similarity([model.wv[w1]],model.wv[core_words])[0]
        avg_cos_sims.append(np.mean(sims_with_core_terms))
        top3_df = pd.DataFrame(sims_with_core_terms,core_words ).reset_index().sort_values(0, ascending = False).head(3)
        top3_tuples = list(top3_df.itertuples(index=False, name=None))
        top3_tuple_lst.append(top3_tuples)
    except:
        avg_cos_sims.append('skip')
        top3_tuple_lst.append('skip')
        print(w1)
  return avg_cos_sims, top3_tuple_lst


def get_output_df(top_500_all, core, m ):
  cos_avg_sims_top_500_all, top3_tuple_lst_top_500_all = get_cos_sim_w_core(top_500_all,core,m )
  cos_avg_sims_core_all, top3_tuple_lst_core_all= get_cos_sim_w_core(core,core,m )
  core_df = pd.DataFrame([core, cos_avg_sims_core_all,  top3_tuple_lst_core_all]).T
  top_500_df = pd.DataFrame([top_500_all, cos_avg_sims_top_500_all,  top3_tuple_lst_top_500_all]).T
  df_concat = pd.concat([core_df, top_500_df])
  df_concat.columns = ['term', 'cosine_sim_with_core', ' closest_terms_from_core']
  return df_concat

def get_results_decade(model, cult_core, dem_core, relt_core, top_500_cult_1, top_500_dem_1, top_500_relt_1, get_500=False):
    dem_core=remove_terms(dem_core, model)
    cult_core=remove_terms(cult_core, model)
    relt_core=remove_terms(relt_core, model)
    
    if get_500:
        top_500_cult_1 = [i[0] for i in model.wv.most_similar(cult_core, topn = 500)]
        top_500_dem_1 = [i[0] for i in model.wv.most_similar(dem_core, topn = 500)]
        top_500_relt_1 = [i[0] for i in model.wv.most_similar(relt_core, topn = 500)]
    
    cult_concat1=get_output_df(top_500_cult_1, cult_core,model)
    dem_concat1=get_output_df(top_500_dem_1, dem_core,model)
    relt_concat1=get_output_df(top_500_relt_1, relt_core,model)
    return cult_concat1, dem_concat1, relt_concat1





####################################
###### get similarities of expanded dicts (500)
####################################

cult_exp1,dem_exp1 , relt_exp1=get_results_decade(m1, cult_core, dem_core, relt_core, [], [], [], get_500=True)

cult_exp2,dem_exp2 , relt_exp2=get_results_decade(m2, cult_core, dem_core, relt_core, [], [], [], get_500=True)

cult_exp3,dem_exp3 , relt_exp3=get_results_decade(m3, cult_core, dem_core, relt_core, [], [], [], get_500=True)

cult_exp4,dem_exp4 , relt_exp4=get_results_decade(m4, cult_core, dem_core, relt_core, [], [],[], get_500=True)

cult_exp1.to_csv(output_dir+"/cos_sim_df_expanded_500_cult_1971-1981.csv")
dem_exp1.to_csv(output_dir+"/cos_sim_df_expanded_500_dem_1971-1981.csv")
relt_exp1.to_csv(output_dir+"/cos_sim_df_expanded_500_relt_1971-1981.csv")

cult_exp2.to_csv(output_dir+"/cos_sim_df_expanded_500_cult_1982_1992.csv")
dem_exp2.to_csv(output_dir+"/cos_sim_df_expanded_500_dem_1982_1992.csv")
relt_exp2.to_csv(output_dir+"/cos_sim_df_expanded_500_relt_1982_1992.csv")

cult_exp3.to_csv(output_dir+"/cos_sim_df_expanded_500_cult_1993_2003.csv")
dem_exp3.to_csv(output_dir+"/cos_sim_df_expanded_500_dem_1993_2003.csv")
relt_exp3.to_csv(output_dir+"/cos_sim_df_expanded_500_relt_1993_2003.csv")

cult_exp4.to_csv(output_dir+"/cos_sim_df_expanded_500_cult_2004_2014.csv")
dem_exp4.to_csv(output_dir+"/cos_sim_df_expanded_500_dem_2004_2014.csv")
relt_exp4.to_csv(output_dir+"/cos_sim_df_expanded_500_relt_2004_2014.csv")


####################################
###### get similarities of refined dicts
####################################

cult_ref1,dem_ref1 , relt_ref1=get_results_decade(m1, cult_core, dem_core, relt_core, cult_expanded_1, dem_expanded_1, relt_expanded_1)

cult_ref2,dem_ref2 , relt_ref2=get_results_decade(m2, cult_core, dem_core, relt_core, cult_expanded_2, dem_expanded_2, relt_expanded_2)

cult_ref3,dem_ref3 , relt_ref3=get_results_decade(m3, cult_core, dem_core, relt_core, cult_expanded_3, dem_expanded_3, relt_expanded_3)

cult_ref4,dem_ref4 , relt_ref4=get_results_decade(m4, cult_core, dem_core, relt_core, cult_expanded_4, dem_expanded_4, relt_expanded_4)


cult_ref1.to_csv(output_dir+"/cos_sim_df_expanded_cult_1971-1981.csv")
dem_ref1.to_csv(output_dir+"/cos_sim_df_expanded_dem_1971-1981.csv")
relt_ref1.to_csv(output_dir+"/cos_sim_df_expanded_relt_1971-1981.csv")

cult_ref2.to_csv(output_dir+"/cos_sim_df_expanded_cult_1982_1992.csv")
dem_ref2.to_csv(output_dir+"/cos_sim_df_expanded_dem_1982_1992.csv")
relt_ref2.to_csv(output_dir+"/cos_sim_df_expanded_relt_1982_1992.csv")

cult_ref3.to_csv(output_dir+"/cos_sim_df_expanded_cult_1993_2003.csv")
dem_ref3.to_csv(output_dir+"/cos_sim_df_expanded_dem_1993_2003.csv")
relt_ref3.to_csv(output_dir+"/cos_sim_df_expanded_relt_1993_2003.csv")

cult_ref4.to_csv(output_dir+"/cos_sim_df_expanded_cult_2004_2014.csv")
dem_ref4.to_csv(output_dir+"/cos_sim_df_expanded_dem_2004_2014.csv")
relt_ref4.to_csv(output_dir+"/cos_sim_df_expanded_relt_2004_2014.csv")