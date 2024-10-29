#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''
import os
import ee 
import gee
import sys
import json
import collections
collections.Callable = collections.abc.Callable


try:
    ee.Initialize(project= 'mapbiomas-caatinga-cloud')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
sys.setrecursionlimit(1000000000)

##############################################
###     Helper function
###    @param item 
##############################################
def convert2featCollection (item):
    item = ee.Dictionary(item)
    feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'classe', item.get('classe'),"area", item.get('sum'))

    return feature

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################

def calculateArea (image, pixelArea, geometry):
    pixelArea = pixelArea.addBands(image.rename('classe'))#.addBands(
                                # ee.Image.constant(yyear).rename('year'))
    reducer = ee.Reducer.sum().group(1, 'classe')

    optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': 30,
        'bestEffort': True,
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas




# pixelArea, imgMapa, bioma250mil

def iterandoXanoImCruda(imgAreaRef, imgMapp, limite):
    biomaraster = ee.Image(param['asset_biomas_raster']).eq(4);
    areaGeral = ee.FeatureCollection([])    
    for year in range(1985, 2023):  # 
        bandAct = "classification_" + str(year) 

        mapToCalc = (
            imgMapp.filter(ee.Filter.eq('year', year))
                        .max().gte(0.84).selfMask()
                        .updateMask(biomaraster)
        );   
        areaTemp = calculateArea(mapToCalc, imgAreaRef, limite)
     
        areaTemp = areaTemp.map(lambda feat: feat.set('year', year))
        processoExportar(areaTemp, 'areas_soil_cerrado_' + str(year))
        areaGeral = areaGeral.merge(areaTemp)      
    
    return areaGeral


       
#exporta a imagem classificada para o asset
def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': 'area_soil',
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print(f"🔉 salvando ...📲   {nameT} ... ")      

var dict_estados = {
    "RONDÔNIA":"11",
    "ACRE":"12",
    "AMAZONAS":"13",
    "RORAIMA":"14",
    "PARÁ":"15",
    "AMAPÁ":"16",
    "TOCANTINS":"17",
    "MARANHÃO":"21",
    "PIAUÍ":"22",
    "CEARÁ":"23",
    "RIO GRANDE DO NORTE":"24",
    "PARAÍBA":"25",
    "PERNAMBUCO":"26",
    "ALAGOAS":"27",
    "SERGIPE":"28",
    "BAHIA":"29",
    "MINAS GERAIS":"31",
    "ESPÍRITO SANTO":"32",
    "RIO DE JANEIRO":"33",    
    "SÂO PAULO":"35",
    "PARANÁ":"41",
    "SANTA CATARINA":"42",
    "RIO GRANDE DO SUL":"43",
    "MATO GROSSO DO SUL":"50",    
    "MATO GROSSO":"51",    
    "GOIÁS":"52",
    "DISTRITO FEDERAL":"53",    
}
dictBiomas = {
    'Amazônia': {
        'CD_Bioma': 1,
        'CD_GEOCUF': ['11','12','13','14','15','16','17','21','51']
    },
    'Caatinga': {
        'CD_Bioma': 2,
        'CD_GEOCUF': ['21','22','23','24','25','26','27','28','29','31']
    },
    'Cerrado': {
        'CD_Bioma': 3,
        'CD_GEOCUF': ['11','15','17','21','22','29','31','35','41','50','51','52','53']
    },
    'Mata Atlântica': {
        'CD_Bioma': 4,
        'CD_GEOCUF': ['33','31','35','32','29','26','27','28','25','24','52','50','43','41','42']
    }, 
    'Pampa': {
        'CD_Bioma': 5,
        'CD_GEOCUF': ['43']
    },
    'Pantanal': {
        'CD_Bioma': 6,
        'CD_GEOCUF': ['50','51']
    }        
}
var dictIdbiomas = {
    'Amazônia': 1,
    'Caatinga': 2,
    'Cerrado': 3,
    'Mata Atlântica': 4,
    'Pampa': 5,
    'Pantanal': 6
}
param = {
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'classmappingV0Caat':  'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'asset_biomas_raster': 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'assetBiomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019',
    'asset_estados_shp': 'projects/mapbiomas-workspace/AUXILIAR/estados-2016',
    'asset_estados_raster': 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster'
};
bioma_select= 'Cerrado';
biomaraster = ee.Image(param['asset_biomas_raster']).eq(dictIdbiomas[bioma_select]);
if bioma_select === 'Caatinga':
    layerSoil = ee.Image(param.classmappingV0Caat);
    print(" para caatinga ver as bandas ", layerSoil.bandNames().getInfo())
else:
    layerSoil =  (ee.ImageCollection(param['classmappingV4'])
                        .filter(ee.Filter.eq('biome', bioma_select))      
    )
    print("número de mapas ", layerSoil.size().getInfo())
imgArea = ee.Image.pixelArea().divide(10000).updateMask(biomaraster)
limitCe = (
        ee.FeatureCollection(param['assetBiomas'])
                .filter(ee.Filter.eq("CD_Bioma", dictIdbiomas[bioma_select]))
)
estadosRaster = ee.Image(param['asset_estados_raster'])
shp_estados = ee.FeatureCollection(param['asset_estados_shp'])

lstEstados = dictBiomas[bioma_select]['CD_GEOCUF']
for geocuf in lstEstados:
    print("pocessing ==> ", geocuf)
    tmp_shpest = shp_estados.filter(ee.Filter.eq('CD_GEOCUF', geocuf))
    


# areeaGeral = iterandoXanoImCruda(imgArea, layerSoil, limitCe.geometry())

