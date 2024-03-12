#-*- coding utf-8 -*-
import ee
import gee
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


param = {
    'classmapping': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOIL',
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'classmappingV3': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    # 'outputAsset': "projects/mapbiomas-workspace/DEGRADACAO/COLECAO/BETA/PROCESS/CAMADA_SOLO",
    'outputAsset': "projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4reg",
    'classMapB' :   [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  :   [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
    'classFlorest': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_mosaic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2', 
    'bandas': ['red_median', 'green_median', 'blue_median'], 
    'lstBiomes' : ['Pantanal','Amazônia', 'Cerrado','Mata Atlântica'], #  'Caatinga', ,'Pampa', 
    'initYear': 1985,
    'endYear': 2023,
    'numeroTask': 3,
    'numeroLimit': 100,
    'conta' : {
        # '0': 'caatinga01',
        '0': 'caatinga02',
        '10': 'caatinga03',
        '20': 'caatinga04',
        '30': 'caatinga05',        
        '40': 'solkan1201',
        '50': 'superconta'
        # '300': 'diegoGmail',      
    },
};

def exportImage(imgYear, name, geom):    
    
    idasset =  param['outputAsset'] + '/' + name
    optExp = {   
        'image': imgYear, 
        'description': name, 
        'assetId': idasset, 
        'region': ee.Geometry(geom),  #getInfo(), #.getInfo()['coordinates']
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy": {".default": "mode"}
    }

    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + name + "..!")

def gerenciador(cont, paramet):    
    # 0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in paramet['conta'].keys()]    
    if str(cont) in numberofChange:

        print("conta ativa >> {} <<".format(paramet['conta'][str(cont)]))        
        gee.switch_user(paramet['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    
    if cont > paramet['numeroLimit'] and cont > 0:
        cont = 0    
    else:
        cont += 1    
    return cont


dictNameBiome = {
    'Amazônia': 'AMAZONIA', 
    'Cerrado': 'CERRADO',
    'Caatinga': 'CAATINGA',
    'Mata Atlântica': 'MATAATLANTICA', 
    'Pampa': 'PAMPA',
    'Pantanal': 'PANTANAL'
};
dictRegions = {
    "Pampa": ['51','52','53'],
    "Cerrado": ['31','32','35','34','33'],
    'Caatinga': ['21','22','23','24'],
    "Pantanal": ['60'],
    'Amazônia': ['11','12','13','14','15','16','17','18','19'],
    "Mata Atlântica":['41','42','44','45','46','47']
};
limiarCerteza = 0.84  # a partir dessa porcentagem conveniamos que é solo
regionss = ee.FeatureCollection(param['regions']);     
mapbiomas = ee.Image(param['inputAsset']);
mapsSoilsV4 = ee.ImageCollection(param['classmappingV4']);
mosaicHarms = ee.ImageCollection(param['asset_mosaic']);
cont = 0;
cont = gerenciador(cont, param);
for bioma in param['lstBiomes'][:]:
    print(f"=============== processing Bioma {bioma} ==================")
    for region in dictRegions[bioma]:
        for yyear in range(param['initYear'], param['endYear']):
            bandaActiva  = 'classification_' + str(yyear);
            regioes = regionss.filter(ee.Filter.eq('region', int(region))).geometry();
            mapsSoilsV4Yyear = mapsSoilsV4.filterBounds(regioes).filter(
                                                ee.Filter.eq('year', yyear)).max().clip(regioes);
            areasIntMapb = mapbiomas.select(bandaActiva).clip(regioes);            
            
            maskWater = areasIntMapb.eq(33);
            areasIntMapb = areasIntMapb.remap(param['classMapB'], param['classNew'])
            maskExcluir = areasIntMapb.eq(1);
            maskAgrop = areasIntMapb.eq(2);
            maskExcluir = maskExcluir.add(maskAgrop).add(maskWater).gt(0).focal_max(1);
            # selecionando a classe de Solo
            mapsSoilsV4Yyear = mapsSoilsV4Yyear.gt(limiarCerteza)
            mapsSoilsV4Yyear = mapsSoilsV4Yyear.subtract(maskExcluir);
            # print("mapas de solo ", mapsSoilsV2Yyear);
            mapsSoilsV4Yyear = mapsSoilsV4Yyear.gt(0).set(
                                    'biome', bioma,
                                    'region', region,
                                    'year', yyear,
                                    'version', '4R',
                                    'GT', 'degradação'
                                )
            name_exp = 'map_soil_' + dictNameBiome[bioma] + '_region_' + str(region) + '_' + str(yyear);
            exportImage(mapsSoilsV4Yyear, name_exp, regioes);
            cont = gerenciador(cont, param);