#-*- coding utf-8 -*-
import ee
import os
import gee 
import sys
import json
from tqdm import tqdm
import random
from datetime import date
import pandas as pd
import collections
collections.Callable = collections.abc.Callable
from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= projAccount)
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
    
    assetOutput = assetSoil + '/' + nameB  

    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetOutput          
        }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")

# get list of all files featuresCollection in the folder ROIs
def getPolygonsfromFolder(assetFolderROIs, nclass):
    
    getlistPtos = ee.data.getList(assetFolderROIs);   
    lstFeatsPtos = [];
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        name = path_.split('/')[-1]
        lstFeatsPtos.append(name)
        # "rois_fitted_image_PANTANAL_1995_227_74_Soil"           
        
    return  lstFeatsPtos

params = {
    'assets':{
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",   
        'mapbiomas': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
        'inputROIsSoil': {'id':'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilB'},
        'inputROIsVeg': {'id':'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2'}
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
    'lsGrade' : {
        'AMAZONIA' :{
            '1' : ['57','58','59','60','61','62','63','64','65','66','67'],
            '2' : ['57','59','60','61','62','63','64','65','66','67','68'],								
            '3' : ['58','59','60','61','62','63','64','65','66','67','68'],								
            '4' : ['59','60','61','62','63','64','65','66','67'],	# 											
            '5' : ['59','60','63','64','65','66','67'],																
            '6' : ['63','64','65','66'],																					
            '220' : ['62','63'],																										
            '221' : ['61','62','63','64'],																						
            '222' : ['61','62','63','64','65','66'],																		
            '223' : ['60','61','62','63','64','65','66','67'],														
            '224' : ['60','61','62','63','64','65','66','67','68','69'],										
            '225' : ['58','59','60','61','62','63','64','65','66','67','68','69','70'],				
            '226' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],			
            '227' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71','72'],
            '228' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'],		
            '229' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'],		
            '230' : ['59','60','61','62','63','64','65','66','67','68','69'],								
            '231' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],			
            '232' : ['56','57','58','59','60','61','62','63','64','65','66','67','68','69'],		
            '233' : ['57','58','59','60','61','62','63','64','65','66','67','68']		#				
        },          
        'CAATINGA' : {
            '214' : ['64', '65', '66', '67'],
            '215' : ['63', '64', '65', '66', '67', '68'],
            '216' : ['63', '64', '65', '66', '67', '68', '69', '70'],
            '217' : ['62', '63', '64', '65', '66', '67', '68', '69', '70', '71'],
            '218' : ['62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72'],
            '219' : ['62', '63', '64', '65', '66', '67', '68', '69', '70', '71'],
            '220' : ['65', '66', '67', '68'],
        },        
        'CERRADO' : {
           '217' : ['70','71','72','73','74'], #																						
           '218' : ['63','64','65','69','70','71','72','73','74'],														
           '219' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76'],		
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '221' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '222' : ['64','65','66','67','68','69','70','71','72','73','74','75','76'],						
           '223' : ['64','65','66','67','68','69','70','71','72','73','74','75'],								
           '224' : ['65','67','68','69','70','71','72','73','74','75','76'],										
           '225' : ['69','70','71','72','73','74','75','76','77'],														
           '226' : ['70','71','72','74','75'],	# '69',																			
           '227' : ['68','69','70','71','72'],																						
           '228' : ['68','69','70','71'],																								
           '229' : ['68','69','70'],																										
           '230' : ['68','69']																												
        },          
        'MATA_ATLANTICA' : {
            '214':['64','65','66','67'],												
            '215':['72','73','74'], # 	'66','67','68','69','70','71',	
            '216':['68','69','70','71','72','73','74','75','76'],		
            '217':['69','70','71','72','73','74','75','76'],				
            '218':['72','73','74','75','76','77'],#							
            '219':['73','74','75','76','77','79'],								
            '220':['74','75','76','77','78','79','80','81'],				
            '221':['72','73','74','75','76','77','78','79','80','81'],
            '222':['73','74','75','76','77','78','79','80','81'],		
            '223':['73','74','75','76','77','78','79','80','81'],		
            '224':['75','76','77','78','79','80'],								
            '225':['75','76','77']														
        },          
        'PAMPA':{
            '220':['81','82'],
            '221':['81','82','83'],
            '222':['82','83'], # '79','80','81',
            '223':['79','80','81','82'],
            '224':['79','80','81','82'],
            '225':['80','81']
        },          
        'PANTANAL': {
            '225' : ['71','72','73','74'],		
            '226' : ['71','72','73','74','75'],
            '227' : ['71','72','73','74','75'],
            '228' : ['71','72']             
        }
    }, # 
    'lsPath' : {
        'AMAZONIA' : ['4','5','6','220','221','222','223','224','225','226','227','228','229','230','231','232','233'], # '1','2','3',
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'], # 
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], # 
        'PAMPA':['220','221','222','223','224','225'], #
        'PANTANAL':['225','226','227','228']
    },  #
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
    'numeroLimit': 100,
    'conta' : {        
        '0': 'caatinga01',
        '8': 'caatinga02',
        '16': 'caatinga03',
        '24': 'caatinga04',
        '32': 'caatinga05',        
        '40': 'solkan1201',
        '60': 'superconta',      
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
        projAccount = get_project_from_account(paramet['conta'][str(cont)])
        try:
            ee.Initialize(project= projAccount) # project='ee-cartassol'
            print('The Earth Engine package initialized successfully!')
        except ee.EEException as e:
            print('The Earth Engine package failed to initialize!')       
        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    elif cont > paramet['numeroLimit']:
        cont = 0    
    cont += 1    
    return cont

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

def getBandFeatures(imgMosaicYY):
    bandas_select = ['min','max','stdDev','amp','median','mean', 'min_contrast', 'min_diss', 'min_savg']
    imgMedian = imgMosaicYY.reduce(ee.Reducer.median()).rename('median')
    imgMean = imgMosaicYY.reduce(ee.Reducer.mean()).rename('mean')
    imgMin = imgMosaicYY.reduce(ee.Reducer.min()).rename('min')
    imgTextura = agregateBandsTexturasGLCM(imgMin)
    imgMax = imgMosaicYY.reduce(ee.Reducer.max()).rename('max')
    imgstdDev = imgMosaicYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
    imgAmp = imgMax.subtract(imgMin).rename('amp')                   
        
    imgMosaicYY = imgMosaicYY.addBands(imgMin).addBands(imgMax).addBands(
                    imgstdDev).addBands(imgAmp).addBands(imgMean
                        ).addBands(imgMedian).addBands(imgTextura)

    return imgMosaicYY.select(bandas_select)

mapsBiomas = ee.Image(params['assets']['mapbiomas'])
anoInicial = params['initYear']
lsAnos = [k for k in range(params['initYear'], params['endYear'])]
print(lsAnos)
gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
coletaSoil = False
# imgColmosaic = ee.ImageCollection(params['assets']['inputAsset'])
dictPath = {}
lstBnd = ['min','max','stdDev','amp','median','mean','class']
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
lstAllBiomas = ['AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL']
# lst_Biome = ['MATA_ATLANTICA'] # ,'CERRADO'
lst_Biome = ['PAMPA','PANTANAL'] #
biome_act = 'CAATINGA'
cont = 0
cont = gerenciador(cont, params)

if coletaSoil:
    folderAssetROIs = params['assets']['inputROIsSoil']
    classAct = 1
else:
    folderAssetROIs = params['assets']['inputROIsVeg']
    classAct = 0

lstFeatCols = getPolygonsfromFolder(folderAssetROIs, classAct)
yyear = 0
print(f"readed {len(lstFeatCols)} featCols in the folder Assets ")
print(lstFeatCols[:2])
dictFeitos = {}
for biome_act in lstAllBiomas:
    dictFeitos[biome_act] = []

for cc, nname in enumerate(lstFeatCols):
    nbioma = nname.split("_")[3]
    if nbioma == 'MATA':
        nbioma = nname.split("_")[3] + "_" +nname.split("_")[4]    
    lstrois = dictFeitos[nbioma]
    lstrois.append(nname)
    dictFeitos[nbioma] = lstrois
    if cc < 1:
        print("   => ", nname)

for kkey, lstroi in dictFeitos.items():
    print(f"Bioma => {kkey} wiht {len(lstroi)}")

# sys.exit()
biome_act = 'CAATINGA'
lst_imgFails = []
for biome_act in ['CAATINGA']: #lst_Biome
    for wrsP in params['lsPath'][biome_act][:]:   #        
        print( 'WRS_PATH # ' + str(wrsP))
        print(params['lsGrade'][biome_act][wrsP][:])
        # sys.exit()
        for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #            
            
            print('WRS_ROW # ' + str(wrsR))
            fPathRow = 'T' + wrsP + '0' + wrsR

            geomsBounds = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                    ee.Filter.eq('ROW', int(wrsR)))
            print("file geometry ", geomsBounds.size().getInfo())
            geomsBounds = geomsBounds.geometry() 

            # recMapbiomas = mapsBiomas.clip(geoms)
            for index, ano in enumerate(lsAnos):

                nameROIs = 'rois_fitted_image_' + biome_act + '_' + str(ano) + '_' + wrsP + '_' + wrsR
                nameImg = 'fitted_image_' + biome_act + '_' + str(ano) + '_' + wrsP + '_' + wrsR

                if nameROIs not in lstFeatCols:
                    print(f" === loading {nameImg} ====" )
                    imgMosYY = ee.Image(params['assets']['inputAsset'] + "/" + nameImg)     
                    
                    try:               
                        bandsIm = imgMosYY.bandNames().getInfo()
                        print("bandas iniciais ", bandsIm)
                    except:
                        bandsIm = []
                    sys.exit()
                    if len(bandsIm) > 1:                        
                        reMapbiomasYY = mapsBiomas.select('classification_' + str(ano)
                                                ).remap(params['classMapB'], params['classNew'])    
                        
                        # selecionar as áreas com classes 1 e 2 
                                      
                        if coletaSoil:
                            maskMapbiomas  = reMapbiomasYY.eq(1).focalMin(3).selfMask()
                            imgMosYY = imgMosYY.updateMask(maskMapbiomas)
                            imgMosYY =  getBandFeatures(imgMosYY)
                            
                            maskSoil = imgMin.lte(6000)# .multiply(imgMax.lte(9000)).multiply(imgAmp.lte(4000))                            
                            imgMosYY = imgMosYY.addBands(reMapbiomasYY.rename('class')).addBands(
                                                            ee.Image.constant(ano).rename('year'))
                        
                        # else:
                        #     maskMapbiomas  = reMapbiomasYY.eq(0).focalMin(6).selfMask()
                        #     print("******-----****--- REDUCING ---****-----******") 
                        #     imgMedian = imgMosYY.reduce(ee.Reducer.median()).rename('median')
                        #     imgMean = imgMosYY.reduce(ee.Reducer.mean()).rename('mean')                       
                        #     imgMin = imgMosYY.reduce(ee.Reducer.min()).rename('min')
                        #     imgMax = imgMosYY.reduce(ee.Reducer.max()).rename('max')
                        #     imgstdDev = imgMosYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
                        #     imgAmp = imgMax.subtract(imgMin).rename('amp') 

                        #     imgMosYY = imgMosYY.addBands(imgMin).addBands(imgMax).addBands(
                        #                         imgstdDev).addBands(imgAmp).addBands(imgMean
                        #                             ).addBands(imgMedian).addBands(
                        #                                 reMapbiomasYY.rename('class')).addBands(
                        #                                     ee.Image.constant(ano).rename('year'))

                        # print("list of bands ", imgMosYY.bandNames().getInfo())
                        # seleciona as áreas de coleta de solo e depois inverte a mask ==> maskMapbiomas.eq(1).eq(0)
                        # imgMosYY = imgMosYY.select(lstBnd).updateMask(maskMapbiomas)
                        pmtSample= {
                            'numPoints': 100,
                            'classBand': 'class',
                            'region': geomsBounds,                            
                            'scale': 30,                            
                            'projection': 'EPSG:3665',                        
                            'dropNulls': True,
                            'tileScale': 4,
                            'geometries': True
                        }
                        points = imgMosYY.stratifiedSample(**pmtSample)                    
                        processoExportar(points, 'rois_' + nameImg, folderAssetROIs['id'])
                        # sys.exit()
                    # except:
                    #     print("failed loading ", nameImg)
                    #     lst_imgFails.append(nameImg)
            cont = gerenciador(cont, params)

dictFail = {'lstImgs' : lst_imgFails}
df = pd.DataFrame.from_dict(dictFail)
df.to_csv(biome_act + '_lstImgsFails.csv')