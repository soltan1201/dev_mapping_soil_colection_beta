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
import glob
import time
import argparse
import requests
from tqdm import tqdm
import multiprocessing
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
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_grade_15Km': 'projects/geo-data-s/assets/fotovoltaica/shp/grid_15_15km_id', # idCod
    'assetMapbiomas90': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'classMapB' :   [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNotSoil': [0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],

    'regionsSel': [21,31,32],
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

path_folder = '/home/superuser/Dados/mapbiomas/dev_mapping_soil_colection_beta/src/dados/patchs'
parser = argparse.ArgumentParser()
parser.add_argument('dir_folder', type=str,  
                    default=path_folder, 
                    help="set the dir of folder to save patchs images" 
            )
try:
    args = parser.parse_args()
    path_Fold = args.dir_folder
    if str(path_folder) != str(path_Fold):
        path_folder = path_Fold
except argparse.ArgumentTypeError as e:
    print(f"Invalid argument: {e}")

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

# @retry(tries=10, delay=1, backoff=2)
def getResult(cont, cod_name_exp):
    
    """Handle the HTTP requests to download an image."""
    print("entrando ao threadss ", cod_name_exp)
    #f"{idCode}_{mmonth}_{yyear}_r{regionSelect}_v{version}"
    partes = cod_name_exp.split('_')
    idCode = partes[0]
    mmonth = int(partes[1])
    yyear = int(partes[2])
    # region = int(partes[3])
    print(f">>>>>>>>>   idCod {idCode} >> month {mmonth} >> year {yyear}")
    bandasInt = [
        'blue', 'red', 'nir', 'swir1', 'ndvi', 'ndsi', 'bsi', 
        'gv', 'shade', 'soil', 'ndfia', 'msavi', 'ui', 'mbi',
        'evi'
    ]
    
    rectGrades15km = (ee.FeatureCollection(params['asset_grade_15Km'])
                    .filter(ee.Filter.eq('idCod', idCode)))
    # print(rectGrades15km.size().getInfo())
    geoGrade = rectGrades15km.geometry()

    bandSelect = 'classification_' + str(yyear)
    if yyear == 2024:
        bandSelect = 'classification_2023'
    # building the mask of areas to mapping mosaic
    maskYYSoil = (ee.Image(params['assetMapbiomas90'])
                        .select(bandSelect)
                        .remap(params['classMapB'], params['classNotSoil'])
                        .clip(geoGrade)
                    )
    data_inicial = ee.Date.fromYMD(yyear, mmonth, 1)
    imColMonth = (ee.ImageCollection(params['asset_collectionId'])
                    .filterBounds(geoGrade)
                    .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                    .first()
                    .updateMask(maskYYSoil.eq(1))
                )
    # imMonthGrade = 
    # print(" Loaded Imagem Collection Month  ", imColMonth.bandNames().getInfo())
    imMonthGrade = GET_NDFIA(imColMonth.clip(geoGrade))
    # print(" Loaded Imagem Collection Month  ", imMonthGrade.bandNames().getInfo())
    exportImage_viaURL(imMonthGrade.select(bandasInt), cod_name_exp + '.tif', geoGrade, bandasInt)

    

def exportImage_viaURL(imgBuild, nameImg, mgeomRect, bnd_mosaic):    
    pathExp = os.path.join(path_folder , nameImg)
    # Fetch the URL from which to download the image.
    # Multi-band GeoTIFF file.
    download_idV = ee.data.getDownloadId({
        'image': imgBuild,
        'bands': bnd_mosaic,
        'region': mgeomRect,
        'scale': 30,
        'format': 'GEO_TIFF'
    })
    response = requests.get(ee.data.makeDownloadUrl(download_idV))
    with open(pathExp, 'wb') as fd:
        fd.write(response.content)

    print("Done: ", nameImg)

print("=====================  INICIALIZANDO PROCESSOS  =================================")

regionSelect = 31
regionSel = ee.FeatureCollection(params['region']).filter(ee.Filter.eq('region', regionSelect))
# Retrieve the projection information from a band of the original image.
# Call getInfo() on the projection to request a client-side object containing
# the crs and transform information needed for the client-side Export function.
mMapbiomas = ee.Image(params['assetMapbiomas90'])
projection = mMapbiomas.projection().getInfo()
shp_grades15km = (ee.FeatureCollection(params['asset_grade_15Km'])
                    .filterBounds(regionSel.geometry()))
lstIdCodGrade = shp_grades15km.reduceColumns(ee.Reducer.toList(), ['idCod']).get('list').getInfo()
numIDCod = 2228
print(f"we loaded {numIDCod} from asset ")
version = 1

lstTIFsaved = [fTIF.split("/")[-1] for fTIF in glob.glob(path_folder + '/*')]
print(f"we have {len(lstTIFsaved)} TIF saved ")
print(" >> ", lstTIFsaved[:5])
# sys.exit()
step = 100
for yyear in params['lstYear'][:3]:
    for ii in range(0, len(lstIdCodGrade), step):    
        idCodeGroup = lstIdCodGrade[ii: ii + step]
        lstCodeG = []
        for idCode in idCodeGroup:            
            for mmonth in range(1, 13):
                name_export = f"{idCode}_{mmonth}_{yyear}_r{regionSelect}_v{version}"
                lstCodeG.append(name_export)

    print(f"========= exporting {len(lstCodeG)} process ================================")
    pool = multiprocessing.Pool(5)
    pool.starmap(getResult, enumerate(lstCodeG))

    pool.close()
    pool.join()
    time.sleep(60)
        # sys.exit()


