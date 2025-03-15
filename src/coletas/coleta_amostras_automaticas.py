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
import copy
# import math
import argparse
import collections
collections.Callable = collections.abc.Callable

from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
print("pathparent ", pathparent)
# pathparent = str('/home/superuser/Dados/projAlertas/proj_alertas_ML/src')
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
courrentAcc, projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize( project= projAccount )
    print(' 🕸️ 🌵 The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


params = {
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',         
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'assetMapbiomas90': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'classMapB' :   [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNotSoil': [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0],
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'regionsSel': [21,31,32],
    'harmonics': 2,  
    'dates':{
        '0': '-01-01',
        '1': '-12-31'
    },      
    'zeroT1_SR' : False,
    
    'initYear': 1985,
    'endYear': 2023,
    'dependent': 'NDFIa',
    'dateInit': '1987-01-01', 
    'lstYear': [
        # 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 
        # 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
        2013, 2014, 2015, 2016, 2017, 2018, 2019, 
        2020, 2021, 2022, 2023, 2024
    ]
  
}

def defineSensor(nyear, mmes):
    ss = 'L8'
    arrayYY = [2000, 2001, 2002, 2012,2013]
    if nyear > 2012:
        ss = 'L8'
        if nyear == 2013 and mmes < 4:
            ss = "L7"
    elif nyear in arrayYY:
        ss = "L7"        
    else:
        ss = 'L5'
    print("SS " + ss)
    return ss


# https://code.earthengine.google.com/8f738cdf510e475ab685e3a85e366aec


# // 4. Calcule o índice NDVI
def index_select(nImg):
    # var nImg = applyScaleFactors(image);
    ndvi = nImg.normalizedDifference(['nir', 'red']).rename('ndvi')
    ndvi = ndvi.add(1).multiply(10000).toUint16()
    ndsi = nImg.normalizedDifference(['swir1', 'nir']).rename('ndsi')
    ndsi = ndsi.add(1).multiply(10000).toUint16()
    bsi = nImg.expression(
                "float(((b('red') + b('swir1')) - (b('nir') + b('blue'))) / ((b('red') + b('swir1')) + (b('nir') + b('blue'))))"
            ).rename('bsi')
    bsi = bsi.add(1).multiply(10000).toUint16()
    evi = nImg.expression(
                "float(2.4 * (b('nir') - b('red')) / (1 + b('nir') + b('red')))"
                ).rename('evi')
    evi = evi.add(10).multiply(1000).toUint16()
    
    msavi =  nImg.expression(
                "float((2 * b('nir') + 1 - sqrt((2 * b('nir') + 1) * (2 * b('nir') + 1) - 8 * (b('nir') - b('red'))))/2)"
            ).rename('msavi')
    msavi = msavi.add(10).multiply(1000).toUint16()
    # UI	Urban Index	urban
    ui = nImg.expression(
            "float((b('swir2') - b('nir')) / (b('swir2') + b('nir')))")\
                .rename(['ui']).toFloat() 
    ui = ui.add(1).multiply(10000).toUint16()
    # MBI	Modified Bare Soil Index
    mbi = nImg.expression(
            "float(((b('swir1') - b('swir2') - b('nir')) /" + 
                " (b('swir1') + b('swir2') + b('nir'))) + 0.5)")\
                    .rename(['mbi']).toFloat() 
    mbi = mbi.add(1).multiply(10000).toUint16()

    imgM = nImg.multiply(10000)
    return (imgM.addBands(ndvi).addBands(ndsi)
                .addBands(bsi).addBands(evi)
                .addBands(msavi).addBands(ui)
                .addBands(mbi).toUint16()
                .copyProperties(nImg)
        )

def GET_NDFIA(IMAGE):
        
    lstBands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    lstFractions = ['gv', 'shade', 'npv', 'soil', 'cloud']
    endmembers = [            
        [0.05, 0.09, 0.04, 0.61, 0.30, 0.10], #/*gv*/
        [0.14, 0.17, 0.22, 0.30, 0.55, 0.30], #/*npv*/
        [0.20, 0.30, 0.34, 0.58, 0.60, 0.58], #/*soil*/
        [0.0 , 0.0,  0.0 , 0.0 , 0.0 , 0.0 ], #/*Shade*/
        [0.90, 0.96, 0.80, 0.78, 0.72, 0.65]  #/*cloud*/
    ];

    fractions = ee.Image(IMAGE).select(lstBands).unmix(endmembers= endmembers, sumToOne= True, nonNegative= True).float()
    fractions = fractions.rename(lstFractions)
    # // print(UNMIXED_IMAGE);
    # GVshade = GV /(1 - SHADE)
    # NDFIa = (GVshade - SOIL) / (GVshade + )
    NDFI_ADJUSTED = fractions.expression(
                            "float(((b('gv') / (1 - b('shade'))) - b('soil')) / ((b('gv') / (1 - b('shade'))) + b('npv') + b('soil')))"
                            ).rename('ndfia')

    NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()
    RESULT_IMAGE = (ee.Image(index_select(IMAGE)) ## adicionando indices extras
                                .addBands(fractions.multiply(10000).toUint16())
                                .addBands(NDFI_ADJUSTED))

    return ee.Image(RESULT_IMAGE).toUint16()

def getIntervalo(nyear):
    intervalo = []
    if nyear == 1985:
        intervalo = [nyear, nyear + 1, nyear + 2]
    elif nyear > 2022:
        intervalo = [2021, 2022, 2023]
    else:
        intervalo = [nyear - 1, nyear, nyear + 1]

    return intervalo

 # salva ftcol para um assetindexIni
# lstKeysFolder = ['cROIsN2manualNN', 'cROIsN2clusterNN'] 
def save_ROIs_toAsset(collection, name):
    assetIds = 'projects/geo-data-s/assets/ROIsSoil/' + name
    # optExp = {
    #     'collection': collection,
    #     'description': name,
    #     'assetId': assetIds
    # }
    # task = ee.batch.Export.table.toAsset(**optExp)

    optExp = {
        'collection': collection,
        'description': name,
        'folder': 'ROIS_soilnew'
    }
    task = ee.batch.Export.table.toDrive(**optExp)

    task.start()
    print("exportando ROIs da bacia $s ...!", name)

print("=====================  INICIALIZANDO PROCESSOS  =================================")


shpGrade = ee.FeatureCollection(params['gradeLandsat'])
regionSelect = 31
regionSel = ee.FeatureCollection(params['region']).filter(ee.Filter.eq('region', regionSelect))
imgMaskReg = regionSel.reduceToImage(['region'], ee.Reducer.first()).gt(1)
print("region selecionadas ", regionSel.first().get('region').getInfo())
mMapbiomas = ee.Image(params['assetMapbiomas90']).updateMask(imgMaskReg)
# exemplo filtrado 
# https://code.earthengine.google.com/343381e6f097b46363cff77fe44d4c2d
##
yyear = 2024
mmonth = 12
bandasInt = [
    'blue', 'red', 'nir', 'swir1', 'ndvi', 'ndsi', 'bsi', 
    'gv', 'shade', 'soil', 'ndfia', 'msavi', 'ui', 'mbi',
    'evi', 'class'
]


for yyear in params['lstYear']:
    mapaYY = mMapbiomas.select('classification_' + str(yyear));
    lstIntervaloYY = getIntervalo(yyear)
    print(f'processing year {yyear} and list >> {lstIntervaloYY}')
    lstIntBands = ['classification_' + str(kk) for kk in lstIntervaloYY]
    # selecionando a clase de solo para valor 1
    maskYYSoil = mMapbiomas.select(lstIntBands).eq(25).reduce(ee.Reducer.sum()).eq(3)

    maskNotSoilPre = (mMapbiomas.select(lstIntBands[0])
                        .remap(params['classMapB'], params['classNotSoil']))
    maskNotSoilCourr = (mMapbiomas.select(lstIntBands[1])
                        .remap(params['classMapB'], params['classNotSoil']))
    maskNotSoilPos = (mMapbiomas.select(lstIntBands[2])
                        .remap(params['classMapB'], params['classNotSoil']))
    # extraindo a mascara de not Soil 
    # levando tudo a valor 2 para a mascara not soil                     
    maskNotSoil = maskNotSoilCourr.add(maskNotSoilPre).add(maskNotSoilPos).gt(1).multiply(2)
    # juntando as duas classes 
    maskYYSoil = maskYYSoil.add(maskNotSoil)
    for mmonth in range(1, 13):
        data_inicial = ee.Date.fromYMD(yyear, mmonth, 1)
        imColMonth = (ee.ImageCollection(params['asset_collectionId'])
                        .filterBounds(regionSel.geometry())
                        .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                        .select(params['bnd_L']).first()
                        .updateMask(imgMaskReg)
                        )
        print(" Loaded Imagem Collection Month  ", imColMonth.bandNames().getInfo())

        #// Create a cloud-free, most recent value composite.
        # sys.exit()
        imColMonth = GET_NDFIA(imColMonth)
        # imColMonth = imColMonth.qualityMosaic('ndfia')#.updateMask(maskYYSoil.gt(0)).selfMask()
        # imColMonth = imColMonth.updateMask(imgMaskReg)
        # addicionando a mascara como banda de classe e mascarando por ela mesma
        # print("bandas do mosaico ", imColMonth.bandNames().getInfo())
        MosaicoClean = (imColMonth.addBands(maskYYSoil.rename('class'))
                            .select(bandasInt).updateMask(maskYYSoil.gt(0))
                            .selfMask())
        ptosTemp = MosaicoClean.stratifiedSample(
                                    numPoints= 5000, 
                                    classBand= 'class', 
                                    region= regionSel.geometry(),                                       
                                    scale= 30,                                     
                                    dropNulls= True,
                                    geometries= True
                                )

        # ptosTemp = MosaicoClean.sample(
        #                             region= regionSel.geometry(),                                       
        #                             scale= 30,   
        #                             numPixels= 15000,                                  
        #                             dropNulls= True,
        #                             geometries= True
        #                         )
        # print(ptosTemp.limit(5).getInfo())
        # insere informacoes em cada ft
        # ptosPreench = ptosTemp.map(lambda feat : feat.set('year', yyear, 'month', mmonth, 'region',regionSelect) )
        # salvando o processo 
        save_ROIs_toAsset(ptosTemp, f'ROIs_reg_{regionSelect}_{yyear}_{mmonth}')
        # sys.exit()