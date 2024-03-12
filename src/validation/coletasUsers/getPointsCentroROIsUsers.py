#-*- coding utf-8 -*-
import ee
import gee #as gee
import sys
import json
import random
import math
import copy
from datetime import date

# import arqParametros as aparam
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

param = {
    'class_solo': 'projects/mapbiomas-workspace/DEGRADACAO/COLECAO/BETA/PROCESS/CAMADA_SOLO',
    'classmappingV2': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  : [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
    'folder_rois': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIs'},
    'folder_roisVeg': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg'},
    'folder_rois_manual': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoil'},
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_mosaic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2', 
    'bandas': ['red_median', 'green_median', 'blue_median'], 
    'integrantes': ['francielle'], #'lazaro', 'bruno', 'daniela', 'francielle'
};

# get list of all files featuresCollection in the folder ROIs
def getPolygonsfromFolder():    
    getlistPtos = ee.data.getList(param['folder_rois_manual']);   
    lstFeatsPtos = ee.FeatureCollection([]);
    # print("getlistPtos ", getlistPtos);
    for idAsset in getlistPtos:         
        path_ = idAsset.get('id')
        featCol = ee.FeatureCollection(path_)
        lstFeatsPtos=  lstFeatsPtos.merge(featCol)    
        
    return  ee.FeatureCollection(lstFeatsPtos)

colshpAmostras = getPolygonsfromFolder();
colshpAmostras = ee.FeatureCollection(colshpAmostras)
print("list de asset amostras ", colshpAmostras.size().getInfo());
print("list by analist users ", colshpAmostras.aggregate_histogram('analista').getInfo())

lstPoints = ee.List([]);

for nameInt in param['integrantes']:
    print("get information from << " + nameInt + " >>")
    feat_tmp = colshpAmostras.filter(ee.Filter.eq('analista', nameInt))
    sizeFeat = feat_tmp.size()
    # print("regions feitas ", feat_tmp.aggregate_histogram('region').getInfo())
    
    lstPoints = feat_tmp.toList(sizeFeat).map(lambda nfeat: ee.Feature(nfeat).centroid(0.1).geometry().coordinates())                                   
    print('show list centroides \n', lstPoints.getInfo());

    
