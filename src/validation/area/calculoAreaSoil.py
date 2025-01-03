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
# from pathlib import Path
# pathparent = str(Path(os.getcwd()).parents[0])
# sys.path.append(pathparent)
# from configure_account_projects_ee import get_current_account, get_project_from_account
# projAccount = get_current_account()
# print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= 'mapbiomas-caatinga-cloud02')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


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


classMapB = [ 0, 3, 4, 5, 6, 9,11,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62]
classNew =  [27, 3, 4, 3, 3, 3,12,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,33,33,21,21,21,21,21,21,21,21,21,21, 4,12,21]

# pixelArea, imgMapa, bioma250mil

def iterandoXanoImCruda(imgMapp, limite, myBioma, myestado, getCobert):
    # layer mask rasters 
    biomaraster = ee.Image(param['asset_biomas_raster']).eq(dictIdbiomas[myBioma]);
    estadosRaster = ee.Image(param['asset_estados_raster']).eq(int(myestado))
    # imagem area delimitada ao estado
    imgAreaRef = ee.Image.pixelArea().divide(10000)
    eImgAreaRef = imgAreaRef.updateMask(biomaraster).updateMask(estadosRaster)
    year_end = 2023
    if myBioma == 'Caatinga':
        year_end = 2018

    if getCobert:
        mapbiomasCol = ee.Image(param['asset_colection_9']).updateMask(biomaraster).updateMask(estadosRaster)
    
    areaGeral = ee.FeatureCollection([])    
    for year in range(1985, year_end + 1):
        bandAct = "classification_" + str(year) 
        if myBioma == 'Caatinga':
            bandAct = "Caatinga_" + str(year) + "_" + bandAct
            mapToCalc = imgMapp.select(bandAct)
        else:
            mapToCalc = (
                imgMapp.filter(ee.Filter.eq('year', year))
                            .max().gte(0.84).selfMask()
            );          
        if getCobert:
            bandAct = "classification_" + str(year) 
            mapToCalc = mapbiomasCol.select(bandAct).updateMask(mapToCalc).remap(classMapB, classNew)
        else:
            mapToCalc = mapToCalc.updateMask(biomaraster).updateMask(estadosRaster)
        
        areaTemp = calculateArea(mapToCalc, eImgAreaRef, limite)        
        areaTemp = areaTemp.map(lambda feat: feat.set('year', year, 'bioma', myBioma, 'estado', myestado))    
        areaGeral = areaGeral.merge(areaTemp)      
    name_export = f'areas_soil_{myBioma}_{myestado}'
    if getCobert:
        name_export = name_export + '_cover'
    processoExportar(areaGeral, name_export)  #  + str(year)
    # return areaGeral


       
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

dict_estados = {
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
        'featureid': 1,
        'CD_GEOCUF': ['11','12','13','14','15','16','17','21','51']
    },
    'Caatinga': {
        'CD_Bioma': 2,
        'featureid': 5,
        'CD_GEOCUF': ['22','23','24','25','26','27','28','29','31']
    },
    'Cerrado': {
        'CD_Bioma': 3,
        'featureid': 4,
        'CD_GEOCUF': ['11','15','17','21','22','29','31','35','41','50','51','52','53']
    },
    'Mata Atlântica': {
        'CD_Bioma': 4,
        'featureid': 2,
        'CD_GEOCUF': ['33','31','35','32','29','26','27','28','25','24','52','50','43','41','42']
    }, 
    'Pampa': {
        'CD_Bioma': 5,
        'featureid': 6,
        'CD_GEOCUF': ['43']
    },
    'Pantanal': {
        'CD_Bioma': 6,
        'featureid': 3,
        'CD_GEOCUF': ['50','51']
    }        
}
dictIdbiomas = {
    'Amazônia': 1,
    'Caatinga': 5,
    'Cerrado': 4,
    'Mata Atlântica': 2,
    'Pampa': 6,
    'Pantanal': 3
}
param = {
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'classmappingV0Caat':  'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'asset_colection_9': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'asset_biomas_raster': 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'asset_biomas_shp': 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019',
    'asset_estados_shp': 'projects/mapbiomas-workspace/AUXILIAR/estados-2016',
    'asset_estados_raster': 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster'
};
bioma_select= 'Caatinga' # 'Cerrado';
getCover = False
 
if bioma_select == 'Caatinga':
    layerSoil = ee.Image(param['classmappingV0Caat']);
    print(" para caatinga ver as bandas ", layerSoil.bandNames().getInfo())
else:
    layerSoil =  (ee.ImageCollection(param['classmappingV4'])
                        .filter(ee.Filter.eq('biome', bioma_select))      
    )
    print("número de mapas ", layerSoil.size().getInfo())

limitBioma = (
        ee.FeatureCollection(param['asset_biomas_shp'])
                .filter(ee.Filter.eq("featureid", dictIdbiomas[bioma_select]))
)
print(" limite do biomas ", limitBioma.size().getInfo())
shp_estados = ee.FeatureCollection(param['asset_estados_shp'])

lstEstados = dictBiomas[bioma_select]['CD_GEOCUF']
for geocuf in lstEstados:
    print("pocessing ==> ", geocuf)
    tmp_shp_est = shp_estados.filter(ee.Filter.eq('CD_GEOCUF', geocuf))
    tmp_limit_Inters = ee.Geometry(limitBioma.geometry()).intersection(tmp_shp_est.geometry())
    
    areeaGeral = iterandoXanoImCruda(layerSoil, tmp_limit_Inters, bioma_select, geocuf, getCover)

