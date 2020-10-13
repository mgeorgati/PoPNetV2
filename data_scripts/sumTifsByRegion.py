import os
import rasterio
import numpy as np

#18subregion names and others
# othna is the only dfference between 2011 and 2017
country_dict = {"australia" : ["aus","cxr", "cck", "hmd", "nzl", "nfk"],
            "antarctica" : ["ata"],
            "eastern_asia":["chn", "hkg", "mac", "prk", "jpn", "mng", "kor"],
            "central_asia":["kaz","kgz","tjk","tkm","uzb"],
            "western_asia":["irq","jor","lbn", "syr"], #"tur",
            "southern_asia":["afg","ind","irn","pak","bgd","btn","npl", "mdv","lka"],
            "southern_eastern_asia":["phl","vnm""brn","khm","idn","lao","mys","mmr","sgp","tha","tls"],
            "micronesia": ["gum","kir","mhl","fsm","nru","mnp","plw","umi"],
            "malanesia":["fji","ncl","png","slb","vut"],
            "polynesia": ["asm","cok","pyf","niu","pcn","wsm","tkl","ton","tuv","wlf"],
            "latin_america_and_the_caribbean": ["aia","atg","abw","bhs","brb","bes","vgb","cym","cub","cuw","dma","dom","grd","glp","hti","jam","mtq","msr","pri","blm","kna","lca",
                "maf","vct","sxm","tto","tca","vir","blz","cri","slv","gtm","hnd","mex","nic","pan","arg","bol","bvt","bra","chl","col","ecu","flk","guf","guy","pry","per","sgs",
                "sur","ury","ven"],
            "northern_america":["bmu","can","grl","spm","usa"],
            "eastern_europe":["pol", "blr","bgr","cze","hun","mda","rou","rus","svk","ukr"],
            "southern_europe":["bih","mkd","alb","and","hrv","gib","grc","vat","mlt","mne","prt","ita","smr","srb","svn","esp"],
            "northern_africa":["mar","dza","egy","lby","sdn","tun","esh"],
            "sub_saharan_africa":["cmr","som","nga","sen", "iot","bdi","com","dji","eri","eth","atf","ken","mdg","mwi","mus","myt","moz","reu","rwa","syc","ssd","uga","tza","zmb","zwe",
                "ago","caf","tcd","cog","cod","gnq","gab","stp","bwa","swz","lso","nam","zaf","ben","bfa","cpv","civ","gmb","gha","gin","gnb","lbr","mli","mrt","ner","shn","sle","tgo"],
            "western_europe": ["deu","nld","aut","bel","fra","lie","lux","mco","che"],
            "northern_europe": ["gbr","nor","irl","swe","lva","est","isl","sjm","fro","fin","jey","imn","ltu","ggy","dnk","ala"],
            "others": ["ocean","twn","unk","othe","urs","otham","yug","othaf","cenam","nstd","othme","othas","scg","tch","othna","sta"] }

def sumUpTif(dictionary, tif_path, out_folder, year):
    pop_list=[]
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    for key in dictionary:
        for value in dictionary[key]:
            for file in os.listdir(tif_path):
                #print(value)
                if file.endswith('{}.tif'.format(value)) and file.startswith('cph_{}'.format(year)):
                    print(key, '--',file)
                    with rasterio.open('{}/{}'.format(tif_path, file)) as src:
                        pop = src.read(1)
                        p1 = src.crs
                        height = src.shape[0],
                        width= src.shape[1],
                        bb= src.transform,
                        pop[pop<0]=0
                        pop_list.append(pop)

        total_pop=np.add.reduce(pop_list)
        print(key, total_pop)

        with rasterio.open('{0}/cph_{1}_pop_origin_new_dnk.tif'.format(tif_path,year)) as dd:

            new_dataset = rasterio.open(
                 '{0}/totalPop_{1}_{2}.tif'.format(out_folder,key,year),
                 'w',
                 driver='GTiff',
                 height=total_pop.shape[0],
                 width=total_pop.shape[1],
                 count=1,
                 dtype=total_pop.dtype,
                 crs=p1,
                 transform= dd.transform
             )
        new_dataset.write(total_pop, 1)
        new_dataset.close()

year= "2011"
tif_path ="C:\FUME\DST_Data\Project_data\\temp_tif\\{}".format(year)
out_folder ="C:\FUME\DST_Data\Project_data\\temp_tif\\{}\\merged".format(year)
sumUpTif(country_dict, tif_path, out_folder,year)

#mismatch = ["atg","kir","kna","stp","tls","vut","othna"]