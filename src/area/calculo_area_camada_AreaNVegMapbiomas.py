#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee 
import gee
import sys
import glob
import collections
collections.Callable = collections.abc.Callable

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

keyAssetr = 'integracao'
# keyAssetr = ''

param = {
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',    
    'assetBiomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil', 
    'source': 'geodatin',
    'scale': 30,
    'driverFolder': 'AREA-SOIL-EXPORT'
}

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
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
def calculateArea (image, pixelArea, geometry):
    pixelArea = pixelArea.addBands(image.rename('classe')).clip(geometry)#.addBands(
                                # ee.Image.constant(yyear).rename('year'))
    reducer = ee.Reducer.sum().group(1, 'classe')
    optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': param['scale'],
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas

# pixelArea, imgMapa, bioma250mil

def iterandoXanoImCruda(imgMapp, imgAreaRef, nameReg, limite, myear):
    try:
        imgAreaRef = imgAreaRef.clip(limite)
        areaGeral = ee.FeatureCollection([])         
        areaGeral = calculateArea (imgMapp, imgAreaRef, limite)        
        areaGeral = areaGeral.map( lambda feat: feat.set('year', int(myear), 'region', nameReg))        
        return areaGeral, True
    except:
        print("FAIL by don't exist")
        return ee.FeatureCollection([]), False

        
#exporta a imagem classificada para o asset
def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': param["driverFolder"]        
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!")      

#testes do dado
# https://code.earthengine.google.com/8e5ba331665f0a395a226c410a04704d
# https://code.earthengine.google.com/306a03ce0c9cb39c4db33265ac0d3ead
cont = 4500
# gerenciador(0, param)
pixelArea = ee.Image.pixelArea().divide(10000)
exportSta = True
verificarSalvos = True
# lista de imagens de correção com Sentinel Data 
namBioma = 'CERRADO'
bioma250mil = ee.FeatureCollection(param['assetBiomas'])\
                    .filter(ee.Filter.eq('Bioma', namBioma)).geometry()
mapsBiomasSoils = ee.Image(param['inputAsset'])# 
lstReg = []
featSHPreg = ee.FeatureCollection([])
# for kk, val in dictRegions.items():
#     lstReg += val
lstReg = ['31','32','35','34','33']
for region_selected in lstReg:
    regioes = ee.FeatureCollection(param['regions']).filter(
                            ee.Filter.eq('region', int(region_selected))).geometry();
    
    for nyear in range(1985, 2023):
        bandsCC = 'classification_' + str(nyear)
        print(f"runing band >> {bandsCC} region >> {region_selected}")
        mapBiomasSoilsYY = mapsBiomasSoils.select(bandsCC).eq(25).selfMask()
        # nameCamada = "maskMapbiomas_reg_" + region_selected + "_y" + str(nyear)
        areaM, exportArea = iterandoXanoImCruda(mapBiomasSoilsYY, pixelArea, region_selected, regioes, nyear)   
        if exportArea:
            featSHPreg = featSHPreg.merge(areaM)     
    
    try:                  
        print(" ===== Salvando ====== ")
        nameCamada = "maskMapbiomas_reg_" + region_selected
        processoExportar(ee.FeatureCollection(featSHPreg), nameCamada)
    except:
        print("estava vacio ")
        #sys.exit()
    # cont = gerenciador(cont, param)


    


