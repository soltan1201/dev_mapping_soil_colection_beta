#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee 
import sys
# import glob
import collections
collections.Callable = collections.abc.Callable

try:
    ee.Initialize(project= 'geo-data-s')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

keyAssetr = 'integracao'
# keyAssetr = ''

param = {
    'classmappingV5': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV5',
    'inputAsset': "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'geral':  True,
    'isImgCol': True,  
    'inBacia': True,
    'version': '',
    'assetBiomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil', 
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'asset_bacias': "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga",
    'biome': 'CAATINGA', 
    'source': 'geodatin',
    'scale': 30,
    'driverFolder': 'statisc_AreasSoil', #'AREA-SOIL-EXPORT', 
    'lsClasses': [3,4,12,21,22,33,29],
    'numeroTask': 0,
    'numeroLimit': 16500,
    'conta' : {
        '0': 'caatinga03',
        '10000': 'caatinga04',
        '18000': 'caatinga05'
    }
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
    "PAMPA": ['51','52','53'],
    "CERRADO": ['31','32','35','34','33'],
    'CAATINGA': ['21','22','23','24'],
    "PANTANAL": ['60'],
    'AMAZONIA': ['11','12','13','14','15','16','17','18','19'],
    "MATAATLANTICA":['41','42','44','45','46','47']
};



# arq_area =  arqParamet.area_bacia_inCaat
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
    pixelArea = pixelArea.addBands(image.rename('classe')).clip(geometry)
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

def iterandoXanoImCruda(imgMapp, nameReg, limite, myear, nmonth):    
    try:
        # imgAreaRef = imgAreaRef.clip(limite)     
        imgAreaRef = ee.Image.pixelArea().divide(10000)   
        print("calculando area ")       
        areaGeral = calculateArea (imgMapp, imgAreaRef, limite)  
        print(" colocar umas propiedades de ano mes e região ")      
        areaGeralProp = areaGeral.map( lambda feat: feat.set('year', int(myear), 'region', nameReg, 'month', int(nmonth)))        
        return areaGeralProp, True
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
makeMapbiomas = False
exportSta = True
verificarSalvos = True
# lista de imagens de correção com Sentinel Data 
namBioma =  'PAMPA' #'CAATINGA' #'CERRADO'
makebyMonth = False
bioma250mil = ee.FeatureCollection(param['assetBiomas'])\
                    .filter(ee.Filter.eq('Bioma', namBioma)).geometry()
mapsSoilsV5 = ee.ImageCollection(param['classmappingV5'])
layerMapbiomas = ee.Image(param['inputAsset'])

print('numero de imagens da versao 5 ', mapsSoilsV5.size().getInfo())
print("statistica of regions ", mapsSoilsV5.aggregate_histogram('region').getInfo())
# get raster with area km2
lstBands = ['classification_' + str(yy) for yy in range(1985, 2025)]
lstnameBioma = [kk for kk in dictNameBiome.keys()]
lstBioma = [kk for kk in dictNameBiome.values()]
lstReg = []

# for kk, val in dictRegions.items():
#     lstReg += val
for namBioma in [ 'PAMPA','CAATINGA','CERRADO', 'PANTANAL']:    
    lstReg = dictRegions[namBioma]                  #['31','32','35','34','33']
    for region_sel in lstReg:
        featSHPreg = ee.FeatureCollection([])
        print(f"load region {region_sel} of bioma {namBioma}")
        regioesGeom = ee.FeatureCollection(param['regions']).filter(
                                ee.Filter.eq('region', int(region_sel))).geometry();

        for nyear in range(2013, 2024):
            areaM = 0            
            if makebyMonth:
                for mmonth in range(1, 13):
                    mapsSoilsV5YM = (mapsSoilsV5.filter(ee.Filter.eq('region', int(region_sel)))
                                                .filter(ee.Filter.eq('year', nyear))
                                                .filter(ee.Filter.eq('month', mmonth))                                                        
                                    )
                    numbImgsYY =  mapsSoilsV5YM.size().getInfo()
                    print(f'numero de {numbImgsYY} imagens da região {region_sel}')
                    mapsSoilsV5YM = mapsSoilsV5YM.max().gt(0.0).selfMask()

                    areaM, exportArea = iterandoXanoImCruda(mapsSoilsV5YM, region_sel, regioesGeom, nyear, mmonth) 
                    if exportArea: 
                        print('exporting ', nyear, " with ", numbImgsYY) 
                        featSHPreg = featSHPreg.merge(areaM) 
            else:
                if makeMapbiomas:
                    numbImgsYY = 1
                    bandaYY = 'classification_' + str(nyear)
                    print('load ', bandaYY)
                    mapsSoilsV5YM = (layerMapbiomas.select(bandaYY).eq(23)
                                        .add(layerMapbiomas.select(bandaYY).eq(24))
                                        .add(layerMapbiomas.select(bandaYY).eq(30))
                                        .add(layerMapbiomas.select(bandaYY).eq(25))
                    )
                    mapsSoilsV5YM = mapsSoilsV5YM.gte(1).selfMask()
                else:
                    mapsSoilsV5YM = (mapsSoilsV5.filter(ee.Filter.eq('region', int(region_sel)))
                                                    .filter(ee.Filter.eq('year', nyear))                                                    
                                        )
                    numbImgsYY =  mapsSoilsV5YM.size().getInfo()
                    print(f'numero de {numbImgsYY} imagens da região {region_sel}')
                    mapsSoilsV5YM = mapsSoilsV5YM.sum().gt(6).selfMask()
                
                print("=========== camada anual ===========")
                # nameCamada = "maskV5_reg_" + region_sel + "_y" + str(nyear)
                areaM, exportArea = iterandoXanoImCruda(mapsSoilsV5YM,region_sel, regioesGeom, nyear, 12)              
                if exportArea: 
                    print('exporting ', nyear, " with ", numbImgsYY) 
                    featSHPreg = featSHPreg.merge(areaM)
            # try:                  
            # print("passso ", areaM.first().getInfo())
        if makebyMonth:
            nameCamada = "layer_soil_V5_byMonth_reg_" + region_sel
        else:
            if makeMapbiomas:
                nameCamada = "layer_soil_V5_byMapbiomas_reg_" + region_sel
            else:
                nameCamada = "layer_soil_V5_byGTdegrad_reg_" + region_sel
        processoExportar(featSHPreg, nameCamada)
            # except:
                # print("estava vacio ")
                #sys.exit()
            # cont = gerenciador(cont, param)


    


