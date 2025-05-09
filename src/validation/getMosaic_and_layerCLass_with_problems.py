#-*- coding utf-8 -*-
import ee
import gee
import sys
import random
import json
import collections
collections.Callable = collections.abc.Callable
from tqdm import tqdm

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
def calculateArea (imageMap, ngeometry):
    pixelArea = ee.Image.pixelArea().divide(10000)
    pixelArea = pixelArea.multiply(imageMap.eq(1).selfMask()).clip(ngeometry).rename('area')    
    optRed = {
        'reducer': ee.Reducer.sum(),
        'geometry': ee.Geometry(ngeometry),
        'scale': 30,
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = areas.values().getInfo()       
    return areas


params = {
    'assets': {
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84 
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",
        'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2'
    },
    'folder_rois': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil',   
    'folder_roiVeg': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2',
    'folder_rois_manual': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoilPtos'},
    'lsGrade' : {
        'AMAZONIA' :{
            '1' : ['57','58','59','60','61','62','63','64','65','66','67'],
            '2' : ['57','59','60','61','62','63','64','65','66','67','68'],								
            '3' : ['58','59','60','61','62','63','64','65','66','67','68'],	# 							
            '4' : ['59','60','61','62','63','64','65','66','67'],												
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
            '228' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'], # 	
            '229' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'], # 
            '230' : ['59','60','61','62','63','64','65','66','67','68','69'],								
            '231' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],			
            '232' : ['56','57','58','59','60','61','62','63','64','65','66','67','68','69'],	# 	
            '233' : ['57','58','59','60','61','62','63','64','65','66','67','68']	# 					
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
           '217' : ['70','71','72','73','74'],																						
           '218' : ['63','64','65','69','70','71','72','73','74'],														
           '219' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76'],		
           '220' : ['64','65','66','67','68','69','70','71','72','73','74','75','76','77'], # '62','63',
           '221' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '222' : ['64','65','66','67','68','69','70','71','72','73','74','75','76'],						
           '223' : ['64','65','66','67','68','69','70','71','72','73','74','75'],								
           '224' : ['65','67','68','69','70','71','72','73','74','75','76'],										
           '225' : ['69','70','71','72','73','74','75','76','77'],														
           '226' : ['69','70','71','72','74','75'],																				
           '227' : ['68','69','70','71','72'],																						
           '228' : ['68','69','70','71'],																								
           '229' : ['68','69','70'],																										
           '230' : ['68','69']																												
        },          
        'MATA_ATLANTICA' : {
            '214':['64','65','66','67'],												
            '215':['66','67','68','69','70','71','72','73','74'],		
            '216':['68','69','70','71','72','73','74','75','76'],		
            '217':['69','70','71','72','73','74','75','76'],				
            '218':['72','73','74','75','76','77'],								
            '219':['73','74','75','76','77','79'],	  # 						
            '220':['74','75','76','77','78','79','80','81'],				
            '221':['72','73','74','75','76','77','78','79','80','81'],
            '222':['73','74','75','76','77','78','79','80','81'], #		
            '223':['73','74','75','76','77','78','79','80','81'], # 		
            '224':['75','76','77','78','79','80'],								
            '225':['75','76','77']														
        },          
        'PAMPA':{
            '220':['81','82'],
            '221':['81','82','83'],
            '222':['79','80','81','82','83'],
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
        'AMAZONIA' : [
            '1','2','3','4','5','6','220','221','222','223','224','225','226',
            '227','228','229','230','231',
            '232','233' 
        ], # 
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': [
            '217','218','219',
            '220','221','222','223','224','225',
            '226','227', '228','229','230'
        ],#   
        'MATA_ATLANTICA':[
            '214','215','216','217','218','219','220','221','222','223','224',
            '225'], #    
        'PAMPA':['220','221','222','223','224','225'], # 
        'PANTANAL':['225','226','227','228']
    },  #    
    'list_biomes': [
        'AMAZONIA', 'CAATINGA','CERRADO',
        'MATA_ATLANTICA','PAMPA','PANTANAL'
    ],
    'initYear': 1985,
    'endYear': 2023,
    'numeroTask': 3,
    'numeroLimit': 70,
    'version': '1',
    'pmtGTB': {
        'numberOfTrees': 10, 
        'shrinkage': 0.1,         
        'samplingRate': 0.8, 
        'loss': "LeastSquares",#'Huber',#'LeastAbsoluteDeviation', 
        'seed': 0
    },
    'conta' : {
        # '0': 'caatinga01',
        '0': 'superconta',
        '40': 'caatinga02',
        # '50': 'caatinga03',
        # '60': 'caatinga04',
        '50': 'caatinga05',        
        '60': 'solkan1201',
        # '90': 'diegoGmail',      
    },
}
dictNameBiome = {
    'AMAZONIA': 'Amazônia', 
    'CERRADO': 'Cerrado',
    'CAATINGA': 'Caatinga',
    'MATA_ATLANTICA': 'Mata Atlântica', 
    'PAMPA': 'Pampa',
    'PANTANAL': 'Pantanal'
}


lsAnos = [k for k in range(params['initYear'], params['endYear'])]
print(lsAnos)
gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
coletaSoil = True

dictPath = {}
lstBnd = ['min','max','stdDev','amp','median','mean','class']
bandas_imports = ['min','max','stdDev','amp','median','mean']


for biome_act in params['list_biomes']:
    dict_tiles = {}
    for wrsP in params['lsPath'][biome_act][:]:   #    
        print( 'WRS_PATH # ' + str(wrsP))
        for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #            
            print('WRS_ROW # ' + str(wrsR))
            fPathRow = 'T' + wrsP + '0' + wrsR             
            geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                        ee.Filter.eq('ROW', int(wrsR))).geometry()
            
            keyPathRow = str(wrsP) + "_" + str(wrsR)
            for index, yyear in enumerate(lsAnos):            
                print("==== ano {} : {} ====".format(index, yyear))
                nameSaved = 'fitted_image_' + biome_act + "_" + str(yyear) + '_' + wrsP + '_' + wrsR
                
                keysdict = str(yyear) + '_' + wrsP + '_' + wrsR
                dict_Im = {}
                try:
                    mosaic = ee.Image(params['assets']['inputAsset'] + '/' + nameSaved)
                    numberBands = len(mosaic.bandNames().getInfo())
                    dict_Im['mosaic_band'] = numberBands
                except:
                    dict_Im['mosaic_band'] = 0

                nameExport = 'classSoil_' + biome_act + "_" + str(yyear) + '_' + wrsP + '_' + wrsR + 'V' + params['version'] 
                try:                
                    # projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2/classSoil_AMAZONIA_1985_1_57V1
                    mapSoils = ee.Image(params['assets']['outputAsset'] + '/' + nameExport)
                    areaTemp = calculateArea(mapSoils, geoms) 
                    dict_Im['area_soil'] = areaTemp[0]
                
                except:
                    dict_Im['area_soil'] = 0

                dict_tiles[keyPathRow] = dict_Im

                print("dict ", dict_Im)

    with open(f"dict_PathRow_{biome_act}.json", "w") as file:
            json.dump(dict_tiles, file)