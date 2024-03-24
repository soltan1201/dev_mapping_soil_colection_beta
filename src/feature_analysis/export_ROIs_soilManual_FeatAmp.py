#-*- coding utf-8 -*-
import ee
import gee 
import sys
import json
from tqdm import tqdm
import random
from datetime import date
import pandas as pd
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

class ClassMosaics(object):

    # default options
    options = { 
        'bnd_LG': ['blue','green','red','nir','swir1','temp','swir2','pixel_qa'],
        'bnd_L': ['blue','green','red','nir','swir1','swir2'], 
        'dependent': 'NDFIa',
        'harmonics': 2         
    }  
    harmonicFrequencies = []
    cosNames = []
    sinNames = []
    independents = []
    bandasRegresion = []
    newBandasIndependentes = []
    harmonicTrendCoefficients = None
    valMean = None

    coefficients = {
        'itcps': ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]).multiply(10000),
        'slopes': ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949])
    }

    def __init__(self, geom, paramet):

        self.options["bnd_LG"] = paramet["bnd_LG"]
        self.options["bnd_L"] = paramet["bnd_L"]
        self.options['harmonics'] = paramet['harmonics']
        self.geomet = geom ## .buffer(buffer)

        self.bluidingVariabel()
    
#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB, assetSoil):
    # assetOutput = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIs/' + nameB
    if assetSoil:
        assetOutput = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoilPtos/' + nameB
    else:
        assetOutput = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualVeg/' + nameB
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetOutput          
        }
    taskA = ee.batch.Export.table.toAsset(**optExp)
    taskA.start() 
    print("salvando ...in Asset " + nameB + "..!")

    # optExpD = {
    #       'collection': ROIsFeat, 
    #       'description': nameB, 
    #       'folder': 'SHP_pointsSoil'          
    #     }
    # taskD = ee.batch.Export.table.toDrive(**optExpD)
    # taskD.start() 
    print("salvando ... on drive " + nameB + "..!")

def getPolygonsfromFolder():
    
    getlistPtos = ee.data.getList(params['assets']['inputROIs']);   
    lstFeatsPtos = [];
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        name = path_.split('/')[-1]
        lstFeatsPtos.append(path_)
        # "rois_fitted_image_PANTANAL_1995_227_74_Soil"           
        
    return  lstFeatsPtos

params = {
    'assets':{
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'regiones': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",   
        'mapbiomas': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
        'inputROIs': {'id':'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManual'},
        # 'inputROIs': {'id':'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg'}
    },
    'classMapB' : [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNewAg': [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
    'classNew'  : [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
    'sensorIds': {        
        'L5': 'LANDSAT/LT05/C01/T1_SR',
        'L7': 'LANDSAT/LE07/C01/T1_SR',
        'L8': 'LANDSAT/LC08/C01/T1_SR'
    }, 
    'zeroT1_SR' : False,
    'sensorIdsToa': {        
        'L5': 'LANDSAT/LT05/C01/T2_TOA',
        'L7': 'LANDSAT/LE07/C01/T1_SR',
        'L8': 'LANDSAT/LC08/C01/T2_TOA'
    },      
    'dates':{
        '0': '-01-01',
        '1': '-12-31'
    },
    'lsPath' : {
        'AMAZONIA' : ['1','2','3','4','5','6','220','221','222','223','224','225','226','227','228','229','230','231','232','233'], # 
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'],
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], # 
        'PAMPA':['220','221','222','223','224','225'],
        'PANTANAL':['225','226','227','228']
    },  #
    'region': [
        51,52,53,31,32,35,34,33,21,22,23,24,
        60,11,12,13,14,15,16,17,18,19,41,42,
        44,45,46,47
    ],
    'bnd' : {
        'L5': ['B1','B2','B3','B4','B5','B7','pixel_qa'],
        'L7': ['B1','B2','B3','B4','B5','B7','pixel_qa'],
        'L8': ['B2','B3','B4','B5','B6','B7','pixel_qa']
    }, 
    'indexProc': {
        'L5': 'LT05',
        'L7': 'LE07',
        'L8': 'LC08'
    },   
    'list_biomes': ['AMAZONIA', 'CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'], # 'CAATINGA',
    'bnd_LG': ['blue','green','red','nir','swir1','swir2','pixel_qa'],
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'CC': 70,
    'initYear': 1985,
    'endYear': 2023,
    'dependent': 'NDFIa',
    'harmonics': 2,
    'dateInit': '2018-01-01',
    'numeroTask': 3,
    'numeroLimit': 45,
    'conta' : {
        '0': 'caatinga01',
        '8': 'caatinga02',
        '16': 'caatinga03',
        '24': 'caatinga04',
        '32': 'caatinga05',        
        '40': 'solkan1201'      
    },
}

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

mapsBiomas = ee.Image(params['assets']['mapbiomas'])
anoInicial = params['initYear']
dictRegions = {
    '51': "PAMPA",
    '52': "PAMPA",
    '53': "PAMPA",
    '31': 'CERRADO',
    '32': 'CERRADO',
    '35': 'CERRADO',
    '34': 'CERRADO',
    '33': 'CERRADO',
    '21': 'CAATINGA',
    '22': 'CAATINGA',
    '23': 'CAATINGA',
    '24': 'CAATINGA',
    '60': 'PANTANAL',
    '11': 'AMAZONIA',
    '12': 'AMAZONIA',
    '13': 'AMAZONIA',
    '14': 'AMAZONIA',
    '15': 'AMAZONIA',
    '16': 'AMAZONIA',
    '17': 'AMAZONIA',
    '18': 'AMAZONIA',
    '19': 'AMAZONIA',
    '41': 'MATA_ATLANTICA',
    '42': 'MATA_ATLANTICA',
    '44': 'MATA_ATLANTICA',
    '45': 'MATA_ATLANTICA',
    '46': 'MATA_ATLANTICA',
    '47': 'MATA_ATLANTICA'
};

coletaSoil = True
imgColmosaic = ee.ImageCollection(params['assets']['inputAsset'])
dictPath = {}
lstBnd = ['min','max','stdDev','amp']
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'

lst_Biome = ['AMAZONIA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'] # 
biome_act = 'PANTANAL'
# cont = gerenciador(0, params)
cont = 0
lstFeatCols = getPolygonsfromFolder()
print(f"readed {len(lstFeatCols)} featCols in the folder Assets ")
yyear = 0

# sys.exit()
featColRegs = ee.FeatureCollection(params['assets']['regiones'])
# lst_Biome = ['MATA_ATLANTICA','PAMPA','PANTANAL'] # 
lstsChange = [
    "shp_AMAZONIA_1990_13", "shp_AMAZONIA_2000_13",
    "shp_AMAZONIA_1995_13", "shp_AMAZONIA_1990_13",
    "shp_AMAZONIA_1985_13", "shp_AMAZONIA_2020_13",
    "shp_AMAZONIA_2018_12", "shp_AMAZONIA_2014_12",
    "shp_AMAZONIA_2010_14", "shp_AMAZONIA_2009_12",
    "shp_AMAZONIA_2005_14", "shp_AMAZONIA_2000_14"
]

def agregateBandsTexturasGLCM (image):

    print("processing agregateBandsTexturasGLCM")        
    img = ee.Image(image).toInt32();                

    texturaNir = img.select('min').glcmTexture(3)  
    savgMin = texturaNir.select('min_savg').divide(10).toInt16()  # promedio
    dissMin = texturaNir.select('min_diss').toInt16()  # dissimilarity
    contrastMin = texturaNir.select('min_contrast').divide(100).toInt16() # contrast
    
    # print("know all bands ", texturaNir.bandNames().getInfo());  
    return  image.addBands(savgMin).addBands(dissMin
                    ).addBands(contrastMin)


def reduzer_images_to_statics(images):

    bandsImages = ['median','mean','min','max','stdDev','amp']
    imgMedian = images.reduce(ee.Reducer.median()).rename('median')
    imgMean = images.reduce(ee.Reducer.mean()).rename('mean')
    imgMin = images.reduce(ee.Reducer.min()).rename('min')
    imgMax = images.reduce(ee.Reducer.max()).rename('max')
    imgstdDev = images.reduce(ee.Reducer.stdDev()).rename('stdDev')
    imgAmp = imgMax.subtract(imgMin).rename('amp')  

    return images.addBands(imgMin).addBands(imgMax).addBands(
                                imgstdDev).addBands(imgAmp).addBands(imgMean
                                    ).addBands(imgMedian).select(bandsImages) 

def getPointsfromFolderManual():
    dict_path = params['assets']['inputROIs']
    print("featureCollection manual => \n === ", dict_path['id'])
    getlistPtos = ee.data.getList(dict_path);   
    lstfeatCols = []
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        # name = path_.split('/')[-1]
        lstfeatCols.append(path_)
        
    return  lstfeatCols

lstFeatCols = getPointsfromFolderManual()

lst_imgFails = []
for cc, idfeat  in  enumerate(lstFeatCols):
    print(cc, " loading ", idfeat)
    # get parameter from name feat
    nameROIs = idfeat.split('/')[-1]
    nameROIs = nameROIs.replace("polygons_coleta_reg", "")
    parte = nameROIs.split("_")
    idreg = parte[0]
    yyear = parte[1]
    biome_act = dictRegions[idreg]
    # loading feat 
    featColeta = ee.FeatureCollection(idfeat)
    sizeFeat = featColeta.size().getInfo()
    dict_cc =  featColeta.aggregate_histogram('classe').getInfo()
    
    print("distribuição de Classes  ", dict_cc)        
    print("size of SHPs ", sizeFeat)

    try:                 
        
        nameROIs = 'rois_shp_' + biome_act + '_' + str(yyear) + '_' + idreg + '_manual'

        imgSelectYY =  imgColmosaic.filter(ee.Filter.eq('biome', biome_act)).filter(
                            ee.Filter.eq('year', int(yyear)))
        sizeImg = imgSelectYY.size().getInfo()        
        print(f"filter by {sizeImg} images ")

        try:               
            bandsIm = imgSelectYY.first().bandNames().getInfo()
            print("bandas iniciais ", bandsIm)
        except:
            bandsIm = []

        if sizeImg > 0:                                          
            imgSelectYY = imgSelectYY.map(lambda img: reduzer_images_to_statics(img))
            imgSelectYY = imgSelectYY.mosaic()
            imgSelectYY = agregateBandsTexturasGLCM(imgSelectYY)
            pmtSampleRegs = {
                'collection': featColeta,     
                'properties': ['classe'],                       
                'scale': 30,                       
                'projection': 'EPSG:3665',  
                'geometries': True
            }
            pointsFeats = imgSelectYY.sampleRegions(**pmtSampleRegs)     
            featPoints = pointsFeats.map(lambda nfeat: nfeat.set( 
                                                'biome', biome_act, 
                                                'region', int(idreg), 
                                                'year', int(yyear)
                                            ))               
            processoExportar(pointsFeats, nameROIs, coletaSoil)
    except:
        print("this polygon don´t will be exportyed ")