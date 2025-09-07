#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import ee
import os
import sys
from tqdm import tqdm
import collections
collections.Callable = collections.abc.Callable
from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
print("pathparent ", pathparent)
# pathparent = str('/home/superuser/Dados/projAlertas/proj_alertas_ML/src')
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
from gee_tools import *
courrentAcc, projAccount = get_current_account()
print(f"projetos selecionado {courrentAcc} >>> {projAccount} <<<")

try:
    ee.Initialize( project= projAccount )
    print(' 🕸️ 🌵 The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


params = {
    'asset_ROIs' : {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilexposto'}
  
}
# get list of all files featuresCollection in the folder ROIs
def getPolygonsfromFolder(assetFolderROIs):    
    getlistPtos = ee.data.getList(assetFolderROIs)
    lstFeatsPtos = [];
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        # name = path_.split('/')[-1]
        lstFeatsPtos.append(path_)                  
        
    return  lstFeatsPtos

lstFeatCols = getPolygonsfromFolder(params['asset_ROIs'])

for cc, asset_idc in enumerate(lstFeatCols):
    print(f' #{cc} >>> load featCol in >> {asset_idc}')
    feat_rois = ee.FeatureCollection(asset_idc)
    print(feat_rois.aggregate_histogram('class').getInfo())