#-*- coding utf-8 -*-
import ee
import sys
import random
import json
import collections
collections.Callable = collections.abc.Callable
from tqdm import tqdm

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB):
    
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'folder': "folderROIs"          
        }
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")

params = {
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84
    'inputAsset': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',     
    'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
    'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'folder_roisSoil': {'id':'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil'},
    'folder_roisVeg': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2'},
    'folder_roisInt': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsInt3CC'},
    'list_biomes': ['AMAZONIA', 'CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'],
}

dictNameBiome = {
    'AMAZONIA': 'Amazônia', 
    'CERRADO': 'Cerrado',
    'CAATINGA': 'Caatinga',
    'MATA_ATLANTICA': 'Mata Atlântica', 
    'PAMPA': 'Pampa',
    'PANTANAL': 'Pantanal'
}


def GetPolygonsfromFolder(assetROIs):    
    getlistPtos = ee.data.getList(assetROIs);   

    lst_asset = []
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        # print(cc, " Loading path ", path_);
        name = path_.split('/')[-1]  
        lst_asset.append(name)    
    
    return  lst_asset

exportROIs = True
numfeat = 5
biomascoletados = []
gradeLandsat = ee.FeatureCollection(params['gradeLandsat'])
lst_featROIsSoil = GetPolygonsfromFolder(params['folder_roisSoil'])
lst_featROIsVeg = GetPolygonsfromFolder(params['folder_roisVeg'])
lst_featROIsInt = GetPolygonsfromFolder(params['folder_roisInt'])

for biomeAct in params['list_biomes']:
    lst_FC_soilBiome = []
    lst_FC_VegBiome = []
    lst_FC_intBiome = []

    for nName in lst_featROIsSoil:
        if biomeAct in nName:
            lst_FC_soilBiome.append(nName)
    
    for nName in lst_featROIsVeg:
        if biomeAct in nName:
            lst_FC_VegBiome.append(nName)

    for nName in lst_featROIsInt:
        if biomeAct in nName:
            lst_FC_intBiome.append(nName)

    print(f"{biomeAct} had {len(lst_FC_soilBiome)} ROIs SOIL saved")
    print(f"{biomeAct} had {len(lst_FC_VegBiome)} ROIs VEG saved")
    print(f"{biomeAct} had {len(lst_FC_intBiome)} ROIs Integrados saved")

    # if exportROIs == True and biomeAct not in biomascoletados and len(lst_temp) > 1:

    #     for cc in range(numfeat):
    #         numramdom = random.randint(0, len(lst_temp))
    #         nameSelect = lst_temp[numramdom]
    #         print(f"select {numramdom} path {nameSelect}")

    #         # Loading vegetation 
    #         try:
    #             featRoi = ee.FeatureCollection(params['folder_rois']['id'] + '/' + nameSelect)
    #             processoExportar(featRoi, nameSelect + "_Soil")

    #             featRoi = ee.FeatureCollection(params['folder_roisVeg']['id'] + '/' + nameSelect)
    #             processoExportar(featRoi, nameSelect + "_Veg")
    #         except:
    #             numfeat += 1