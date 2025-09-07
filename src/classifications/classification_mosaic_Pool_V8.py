#-*- coding utf-8 -*-
import ee
import os
import sys
import time
import json
import collections
collections.Callable = collections.abc.Callable
import pandas as pd
from tqdm import tqdm
from multiprocessing.pool import ThreadPool

from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
print("pathparent ", pathparent)
# pathparent = str('/home/superuser/Dados/projAlertas/proj_alertas_ML/src')
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
from gee_tools import *
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
    'assetMapbiomas100': 'projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v2',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    # 'asset_rois': {'id' : 'projects/geo-data-s/assets/ROIsSoil'},
    'asset_rois': {"id" : "projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilexposto"},
    'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV6',
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'classMapB' :   [15,18,19,20,21,22,23,24,25,29,30,32,35,36,37,38,39,40,41,42,43,44,45,46,47,48,62],
    'classNotSoil': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    'regionsSel': [
        '21','22','23','24',
        # '31','32','35','34','33', #
        # '60','51','52','53',
        # '41','42','44','45','46','47'
        # '11','12','13','14','15','16','17','18','19',
    ],
    'lstYear': [
        # 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 
        # 1999,
        2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
        2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
    ],
    'pmtGTB': {
        'numberOfTrees': 35, 
        'shrinkage': 0.1,  
        'maxNodes': 3,
        'samplingRate': 0.8, 
        'loss': "LeastSquares", #'Huber',#'LeastAbsoluteDeviation', 
        'seed': 0
    },
    'numeroTask': 10,
    'numeroLimit': 2024,
    'conta' : {
        '2013': 'caatinga01',
        '2014': 'caatinga02',
        '2015': 'caatinga03',
        '2016': 'caatinga04',
        '2017': 'caatinga05',        
        '2018': 'solkan1201',        
        '2019': 'superconta'        
    },
    'version': 5
}
dictNameBiome = {
    'AMAZONIA': 'Amazônia', 
    'CERRADO': 'Cerrado',
    'CAATINGA': 'Caatinga',
    'MATA_ATLANTICA': 'Mata Atlântica', 
    'PAMPA': 'Pampa',
    'PANTANAL': 'Pantanal'
}
dictRegions = {
    '11': 'AMAZONIA',
    '12': 'AMAZONIA',
    '13': 'AMAZONIA',
    '14': 'AMAZONIA',
    '15': 'AMAZONIA',
    '16': 'AMAZONIA',
    '17': 'AMAZONIA',
    '18': 'AMAZONIA',
    '19': 'AMAZONIA',
    '21': 'CAATINGA',
    '22': 'CAATINGA',
    '23': 'CAATINGA',
    '24': 'CAATINGA',
    '31': 'CERRADO',
    '32': 'CERRADO',
    '35': 'CERRADO',
    '34': 'CERRADO',
    '33': 'CERRADO',
    '41': 'MATA_ATLANTICA',
    '42': 'MATA_ATLANTICA',
    '44': 'MATA_ATLANTICA',
    '45': 'MATA_ATLANTICA',
    '46': 'MATA_ATLANTICA',
    '47': 'MATA_ATLANTICA',
    '51': 'PAMPA',
    '52': 'PAMPA',
    '53': 'PAMPA',
    '60': 'PANTANAL'
};
dictHypePmtro = {
    'region_31': {'learning_rate': 0.05, 'max_features': 4, 'n_estimators': 35},
    'region_32': {'learning_rate': 0.05, 'max_features': 5, 'n_estimators': 35},
    'region_33': {'learning_rate': 0.05, 'max_features': 3, 'n_estimators': 35},
    'region_35': {'learning_rate': 0.05, 'max_features': 4, 'n_estimators': 35},
    'region_34': {'learning_rate': 0.05, 'max_features': 4, 'n_estimators': 35},
    'region_21': {'learning_rate': 0.05, 'max_features': 4, 'n_estimators': 45},
    'region_22': {'learning_rate': 0.05, 'max_features': 5, 'n_estimators': 45},
    'region_23': {'learning_rate': 0.05, 'max_features': 3, 'n_estimators': 45},
    'region_24': {'learning_rate': 0.05, 'max_features': 4, 'n_estimators': 45},
}
# // 4. Calcule o índice NDVI
def index_select(nImg):
    # var nImg = applyScaleFactors(image);
    ndvi = nImg.normalizedDifference(['nir', 'red']).rename('ndvi')
    ndvi = ndvi.add(1).multiply(10000).toUint16()
    
    # normalized difference soil index (NDSI)
    #(B7 - B2)/ (B7 + B2)
    ndsi = nImg.normalizedDifference(['swir1', 'blue']).rename('ndsi')
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
    mbi = (nImg.expression(
            "float(((b('swir1') - b('swir2') - b('nir')) /" + 
                " (b('swir1') + b('swir2') + b('nir'))) + 0.5)")
                    .rename(['mbi']).toFloat() 
        )
    mbi = mbi.add(1).multiply(10000).toUint16()

    vdvi = (nImg.expression(
            "float((2 * b('green') - b('red') - b('blue')) /" + 
                " (2 * b('green') + b('red') + b('blue')))")
                    .rename(['vdvi']).toFloat() 
        )
    vdvi = vdvi.add(1).multiply(10000).toUint16()
    
    # NDBI=(TM5−TM4)/(TM5+TM4) 
    # Normalized Diﬀerence Built-up Index (NDBI) 
    ndbi = (nImg.expression(
            "float( (b('swir1') - b('red')) / (b('swir1') + b('red')) )")
                    .rename(['ndbi']).toFloat() 
        )
    ndbi = ndbi.add(1).multiply(10000).toUint16()

    # mid-infrared index maps
    # (TM5 - TM7) / (TM5 + TM7)
    # (swir1 - swir2) / (swir1 + swir2)
    miim = (nImg.expression(
            "float((b('swir1') - b('swir2')) / (b('swir1') + b('swir2')))")
                .rename(['miim']).toFloat()) 
    miim = miim.add(1).multiply(10000).toUint16()

    # IBI (Index-based Built-Up Index) [1]  
    # (2 * B5 / (B5 + B4) - [B4/(B4 + B3) + B2/(B2+B5)])/ (2 * B5 / (B5 + B4) + [B4/(B4 + B3) + B2/(B2+B5)])
    ibi = (nImg.expression(
            "float((((2 * b('swir1')) / (b('swir1') + b('nir'))) - (b('nir') / (b('nir') + b('red'))) + ( b('green') / (b('swir1') + b('green')))) /" +     
                 " (((2 * b('swir1')) / (b('swir1') + b('nir'))) + (b('nir') / (b('nir') + b('red'))) + ( b('green') / (b('swir1') + b('green')))))")
                    .rename(['ibi']).toFloat() 
        )
    ibi = ibi.add(1).multiply(10000).toUint16()

    # Bare Soil Index (BI) ok
    # (swir2 + red) - (nir + blue) / ((swir2 + red) + (nir + blue))
    bi = (nImg.expression(
            "float(((b('swir2') + b('red')) - (b('nir') + b('blue')))/ ((b('swir2') + b('red')) + (b('nir') + b('blue'))))")
                    .rename(['bi']).toFloat() 
        )
    bi = bi.add(1).multiply(10000).toUint16()

    # Hyperspectral Bare Soil Index (HBSI)
    # (swir2 + green) - (nir + blue) / ((swir2 + green) + (nir + blue))
    hbsi = (nImg.expression(
            "float(((b('swir2') + b('green')) - (b('nir') + b('blue')))/ ((b('swir2') + b('green')) + (b('nir') + b('blue'))))")
                    .rename(['hbsi']).toFloat() 
        )
    hbsi = hbsi.add(1).multiply(10000).toUint16()

    imgM = nImg.multiply(10000)
    return (imgM.addBands(ndvi).addBands(ndsi)
                .addBands(bsi).addBands(evi)
                .addBands(msavi).addBands(ui)
                .addBands(vdvi).addBands(ndbi)
                .addBands(bi).addBands(hbsi)
                .addBands(miim).addBands(ibi)
                .addBands(mbi).toUint16()
                .copyProperties(nImg)
        )

def GET_NDFIA(IMAGE):
        
    lstBands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    lstFractions = ['gv', 'npv', 'soil', 'shade', 'cloud']
    endmembers = [            
        [0.05, 0.09, 0.04, 0.61, 0.30, 0.10], #/*gv*/
        [0.14, 0.17, 0.22, 0.30, 0.55, 0.30], #/*npv*/
        [0.20, 0.30, 0.34, 0.58, 0.60, 0.58], #/*soil*/
        [0.0 , 0.0,  0.0 , 0.0 , 0.0 , 0.0 ], #/*Shade*/
        [0.90, 0.96, 0.80, 0.78, 0.72, 0.65]  #/*cloud*/
    ];
    # , sumToOne= True, nonNegative= True
    fractions = ee.Image(IMAGE).select(lstBands).unmix(endmembers= endmembers).float()
    fractions = fractions.rename(lstFractions)
    
    # // print(UNMIXED_IMAGE);
    # GVshade = GV /(1 - SHADE)
    # NDFIa = (GVshade - SOIL) / (GVshade + )
    NDFI_ADJUSTED = ( fractions.expression(
                            "float(((b('gv') / (1 - b('shade'))) - b('soil')) / ((b('gv') / (1 - b('shade'))) + b('npv') + b('soil')))" )
                            .rename('ndfia')
                    )

    NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()
    RESULT_IMAGE = (ee.Image(index_select(IMAGE)) ## adicionando indices extras
                                .addBands(fractions.multiply(10000).toUint16())
                                .addBands(NDFI_ADJUSTED))

    return ee.Image(RESULT_IMAGE).toUint16()


def exportImage(imgYear, name, geom):        
    idasset =  params['outputAsset'] + '/' + name
    optExp = {   
        'image': imgYear, 
        'description': name, 
        'assetId': idasset, 
        'region': ee.Geometry(geom), #['coordinates'],  #getInfo(), #
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy": {".default": "mode"}
    }

    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + name + "..!")


def gerenciador(cont):
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in params['conta'].keys()]    
    print(numberofChange)    
    if str(cont) in numberofChange:
        print(f"inicialize in account #{cont} <> {params['conta'][str(cont)]}")
        switch_user(params['conta'][str(cont)])
        projAccount = get_project_from_account(params['conta'][str(cont)])
        try:
            ee.Initialize(project= projAccount) # project='ee-cartassol'
            print('The Earth Engine package initialized successfully!')
        except ee.EEException as e:
            print('The Earth Engine package failed to initialize!') 
        tarefas = tasks(
            n= params['numeroTask'],
            return_list= True)
        
        for lin in tarefas:   
            print(str(lin))         
            # relatorios.write(str(lin) + '\n')    
    elif cont > params['numeroLimit']:
        return 0
    cont += 1    
    return cont


def get_theBest_hyperparameter_tuning(nameRegion):
    npath = f"ROIs/rois_shp_CERRADO_{nameRegion}_fineTuring.csv"
    print("reading " + npath)
    tableHP_CSV = pd.read_csv(npath)
    nrow = tableHP_CSV.iloc[0]
    learning_rate = nrow["learning_rate"]
    n_estimators = nrow["n_estimators"]
    max_features = nrow["max_features"]

    return learning_rate, n_estimators, max_features

def getPointsfromFolderManual(idreg, nyear):
    
    print(f" região {idreg} => {nyear} ")
    getlistPtos = ee.data.listAssets(params['asset_rois']['id'])  
    featColsPtos = ee.FeatureCollection([])
    
    # print("getlistPtos ", getlistPtos['assets']);
    for idAsset in tqdm(getlistPtos['assets']):    
        # print(" dict >> ", idAsset['id'])     
        path_ = idAsset['id']
        name_file = path_.split('/')[-1]
        # print(name_file)
        if str(idreg) in name_file and str(nyear) in name_file:
            print(f"loading and merge .... featureCollection >>> {name_file}")
            mes =  name_file.split('_')[-1]
            feat_tmp = ee.FeatureCollection(path_)
            feat_tmp= feat_tmp.map(lambda feat: feat.set('month', int(mes)))
            featColsPtos = featColsPtos.merge(feat_tmp)    
        
    return  featColsPtos


def export_classification_soilMap_by_Year(nkeyPathRow_YY):
    # f"classSoil_reg_{regionSelect}_{yyear}_{mmonth}_v{params['version']}"['version'] 
    partes = nkeyPathRow_YY.split('_')
    print("partes ", partes)
    reg = int(partes[2])
    yyear = int(partes[3])
    mmonth = int(partes[4])
    version = partes[5]
    print(f"region: {reg} | year : {yyear} | mmonth {mmonth} | version: {version} ")
    
    # bandasInt = [
    #     'blue', 'red', 'nir', 'swir1', 'swir2',
    #     'ndvi', 'ndsi', 'bsi', 'gv', 'npv', 'soil',
    #     'ndfia', 'msavi', 'ui', 'mbi', 'vdvi', 'ndbi',
    #     'evi', 'bi', 'hbsi','miim','ibi', 'class'
    # ]
    bandasInt = [
        'ui', 'miim', 'ndsi', 'soil', 'bsi', 'bi', 'mbi', 'vdvi', 'blue',
       'hbsi', 'gv', 'ndbi', 'ibi' # , 'ndfia'
    ]
    regionSel = ee.FeatureCollection(params['region']).filter(ee.Filter.eq('region', reg))
    regionSel = regionSel.map(lambda feat: feat.set('id_codigo', 1))
    # print(regionSel.aggregate_histogram('region').getInfo())
    
    imgMaskReg = regionSel.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)
    # sys.exit()
    try:
        print("region selecionadas ", regionSel.size().getInfo())
        band_class = 'classification_' + str(yyear)  
        band_class_pos = 'classification_' + str(yyear + 1)         
        
        mMapbiomas_yy = (
                    ee.Image(params['assetMapbiomas100'])
                        .select(band_class)
                        .remap(params['classMapB'], params['classNotSoil'], 0)
                        .updateMask(imgMaskReg)
                )
        print("banda carregada >> ", mMapbiomas_yy.bandNames().getInfo())

        mMapbiomas_pos = (
                    ee.Image(params['assetMapbiomas100'])
                        .select(band_class_pos)
                        .remap(params['classMapB'], params['classNotSoil'], 0)
                        .updateMask(imgMaskReg)
                    )
        print("banda carregada >> ", mMapbiomas_pos.bandNames().getInfo())

        mMapbiomas_pos = mMapbiomas_pos.add(mMapbiomas_yy).gt(0)

        data_inicial = ee.Date.fromYMD(yyear, mmonth, 1)
        imColMonth = (ee.ImageCollection(params['asset_collectionId'])
                        .filterBounds(regionSel.geometry())
                        .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                        .select(params['bnd_L']).first()
                        .updateMask(mMapbiomas_pos)
                )

        print(" Loaded Imagem Collection Month  ", imColMonth.bandNames().getInfo())
        imColMonth = GET_NDFIA(imColMonth)    
        # imColMonth = imColMonth.divide(10000).toFloat()

        shp_ROIs = getPointsfromFolderManual(reg, yyear)
        shp_ROIs = ( shp_ROIs                        
                        .remap([1,2], [1,0], 'class')
                )

        sizeROIs = shp_ROIs.aggregate_histogram('class').getInfo()
        print("============== first size conditions = ", sizeROIs)

        classifierGTB = (ee.Classifier.smileGradientTreeBoost(**params['pmtGTB'])
                            .train(shp_ROIs, 'class', bandasInt)
                            .setOutputMode('PROBABILITY')
                    )
        classifiedGTB = imColMonth.classify(classifierGTB, 'classification_' + str(yyear))
        classifiedGTB = classifiedGTB.multiply(10000).toInt16()
        mydict = {                        
            'version': version,
            'year': yyear,
            'month': mmonth,
            'biome': dictRegions[str(reg)],
            'region': reg,
            'layer': 'soil',
            'sensor': 'Landsat',
            'source': 'geodatin'                
        }         
        classifiedGTB = classifiedGTB.set(mydict)
        exportImage(classifiedGTB, nkeyPathRow_YY, regionSel.geometry())

    except:           
        print('FAILS BY SIZE ROIs 0 => ', nkeyPathRow_YY)
    #     arqFeitos.write(nkeyPathRow_YY + '\n')


      
regionSelect = 31
# regionSel = ee.FeatureCollection(params['region']).filter(ee.Filter.eq('region', regionSelect))
# imgMaskReg = regionSel.reduceToImage(['region'], ee.Reducer.first()).gt(1)
# print("region selecionadas ", regionSel.first().get('region').getInfo())
# mMapbiomas = ee.Image(params['assetMapbiomas90']).updateMask(imgMaskReg)
# exemplo filtrado 
# https://code.earthengine.google.com/343381e6f097b46363cff77fe44d4c2d
##
lstIdsmapsSaved = []
# sys.exit()

arqFeitos = open("registros/orbitas_tiles_AnosV5.txt", 'w+')
lst_imgFails = [] 
lstImgtoProc = []
for regionSelect in params['regionsSel'][1:]:
    print('regions >> ', regionSelect)
    for yyear in params['lstYear']:
            # nameExport = 'classSoil_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR + 'V' + params['version'] 
        for mmonth in range(1, 13):
            data_inicial = ee.Date.fromYMD(yyear, mmonth, 1)
            nameMapSoilIm = f"classSoil_reg_{regionSelect}_{yyear}_{mmonth}_v{params['version']}"
            if nameMapSoilIm not in lstIdsmapsSaved:
                # print(nameMapSoilIm)
                lstImgtoProc.append(nameMapSoilIm)
    print("len ", len(lstImgtoProc))
    # print(lstImgtoProc)
    # sys.exit()
    if len(lstImgtoProc) > 0:
        # create the pool with the default number of workers
        with ThreadPool() as pool:
            # issue one task for each call to the function
            for result in pool.map(export_classification_soilMap_by_Year, lstImgtoProc):
                # handle the result
                print(f'>got {result}')
        
        # report that all tasks are completed
        print(f'images  from region # {regionSelect} go doing to process')
    else:
        print(f'All images  from region # {regionSelect} was to DOING')

    time.sleep(60)