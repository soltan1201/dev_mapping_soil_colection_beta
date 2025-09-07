#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
# import gee
import sys
import os
import glob
from pathlib import Path
from tqdm import tqdm
import collections
from pathlib import Path
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
projAccount = get_current_account()[1]
print(f"projetos selecionado >>> {projAccount} <<<")


try:
    ee.Initialize(project= projAccount)
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
# sys.setrecursionlimit(1000000000)


param = {
    'asset_rois': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilexposto'}
}

def getPointsfromFolderManual(idreg, nyear):
    print(f" região {idreg} => {nyear} ")
    getlistPtos = ee.data.listAssets(param['asset_rois']['id']);   
    featColsPtos = ee.FeatureCollection([])
    # print("getlistPtos ", getlistPtos['assets']);
    for idAsset in tqdm(getlistPtos['assets']):    
        # print(" dict >> ", idAsset['id'])     
        path_ = idAsset['id']
        name_file = path_.split('/')[-1]
        # print(f"idReg {idreg} >> {nyear }  search in {name_file}  >> {str(idreg) in name_file }")  # and str(nyear) in name_file
        if str(idreg) in name_file and str(nyear) in name_file:
            print(f"loading and merge .... featureCollection >>> {name_file}")
            mes =  name_file.split('_')[-1]
            feat_tmp = ee.FeatureCollection(path_)
            feat_tmp= feat_tmp.map(lambda feat: feat.set('month', int(mes)))
            featColsPtos = featColsPtos.merge(feat_tmp)    
        
    return  featColsPtos

def save_ROIs_toAsset(collection, name):

    optExp = {
        'collection': collection,
        'description': name,
        'folder': 'ROIS_soilnew'
    }
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start()
    print("exportando ROIs da bacia $s ...!", name)


lst_regions = [21, 22, 23, 24]
start_year = 2020
end_year = 2024

for regionSelect in lst_regions[:]:
    print('regions >> ', regionSelect)
    for myear in range(start_year, end_year + 1):
        print(f"load datas of year {myear} ")
        feat_rois =  getPointsfromFolderManual(regionSelect, myear)
        feat_rois = ee.FeatureCollection(feat_rois)
        feat_rois = feat_rois.map(lambda feat:  feat.set('region', regionSelect, 'year', myear))
        name_export = f'rois_coleta_soil_reg{regionSelect}_{myear}'
        print("show size of FeatureCollection ", feat_rois.size().getInfo())
        save_ROIs_toAsset(feat_rois, name_export)
        # sys.exit()