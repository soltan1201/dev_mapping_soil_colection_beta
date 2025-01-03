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
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    # 'inputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/aggrements',
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
    'driverFolder': 'AREA-SOIL-EXPORT', 
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
    "Pampa": ['51','52','53'],
    "Cerrado": ['31','32','35','34','33'],
    'Caatinga': ['21','22','23','24'],
    "Pantanal": ['60'],
    'Amazônia': ['11','12','13','14','15','16','17','18','19'],
    "Mata Atlântica":['41','42','44','45','46','47']
};



# arq_area =  arqParamet.area_bacia_inCaat

def gerenciador(cont, paramet):
    #0, 18, 36, 54]
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
    
    elif cont > paramet['numeroLimit']:
        cont = 0
    
    cont += 1    
    return cont

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
mapsSoilsV4 = ee.ImageCollection(param['classmappingV4']).filter(
                                ee.Filter.eq('version', '5'))
print('numero de imagens da versao 5 ', mapsSoilsV4.size().getInfo())
# get raster with area km2
lstBands = ['classification_' + str(yy) for yy in range(1985, 2023)]
lstnameBioma = [kk for kk in dictNameBiome.keys()]
lstBioma = [kk for kk in dictNameBiome.values()]
lstReg = []
featSHPreg = ee.FeatureCollection([])
# for kk, val in dictRegions.items():
#     lstReg += val
lstReg = ['31','32','35','34','33']
for region_selected in lstReg:
    regioes = ee.FeatureCollection(param['regions']).filter(
                            ee.Filter.eq('region', int(region_selected))).geometry();
    mapsSoilsV4tmp = mapsSoilsV4.filter(
                            ee.Filter.eq('region', region_selected))
    numbImgs =  mapsSoilsV4tmp.size().getInfo()
    print(f'numero de {numbImgs} imagens da região {region_selected}')
    if numbImgs > 0:
        for nyear in range(1985, 2023):
            mapsSoilsV4YY = mapsSoilsV4tmp.filter(ee.Filter.eq('year', nyear))
            numbImgsYY =  mapsSoilsV4YY.size().getInfo()
            if numbImgsYY > 0:
                mapsSoilsV4YY = mapsSoilsV4YY.max().gt(0.0).selfMask()
                # nameCamada = "maskV5_reg_" + region_selected + "_y" + str(nyear)
                areaM, exportArea = iterandoXanoImCruda(mapsSoilsV4YY, pixelArea, region_selected, regioes, nyear)              
                if exportArea: 
                    print('exporting ', nyear, " with ", numbImgsYY) 
                    featSHPreg = featSHPreg.merge(areaM)
            # try:                  
        print("passso ", areaM.first().getInfo())
        nameCamada = "maskV50_reg_" + region_selected
        processoExportar(featSHPreg, nameCamada)
        # except:
            # print("estava vacio ")
            #sys.exit()
        # cont = gerenciador(cont, param)


    


