#-*- coding utf-8 -*-
import ee
import gee
import sys
import random
import json
import collections
collections.Callable = collections.abc.Callable
from tqdm import tqdm_notebook, tqdm

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


params = {
    'assets': {
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84 
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",
        'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsInt'
    },
    'folder_rois': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil/',
    'folder_roisVeg': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg/',
    'lsGrade' : {
        'AMAZONIA' :{
            '1' : ['57','58','59','60','61','62','63','64','65','66','67'],
            '2' : ['57','59','60','61','62','63','64','65','66','67','68'],								
            '3' : ['58','59','60','61','62','63','64','65','66','67','68'],								
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
            '228' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'],		
            '229' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'], # 
            '230' : ['59','60','61','62','63','64','65','66','67','68','69'],								
            '231' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],			
            '232' : ['56','57','58','59','60','61','62','63','64','65','66','67','68','69'],		
            '233' : ['57','58','59','60','61','62','63','64','65','66','67','68']						
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
           '219' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76'],#		
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '221' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '222' : ['64','65','66','67','68','69','70','71','72','73','74','75','76'],						
           '223' : ['64','65','66','67','68','69','70','71','72','73','74','75'],	# 							
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
        'AMAZONIA' : ['1','2','3','4','5','6','220','221','222','223','224','225','226','227','228','229','230','231','232','233'],
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'],# 
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], # 
        'PAMPA':['220','221','222','223','224','225'],
        'PANTANAL':['225','226','227','228']
    },  #    
    'list_biomes': ['AMAZONIA', 'CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'], # 'CAATINGA',
    'initYear': 1985,
    'endYear': 2023,
    'numeroTask': 3,
    'numeroLimit': 35,
    'version': '1',
    'pmtGTB': {
        'numberOfTrees': 7, 
        'shrinkage': 0.1,         
        'samplingRate': 0.8, 
        'loss': "LeastSquares",#'Huber',#'LeastAbsoluteDeviation', 
        'seed': 0
    },
    'conta' : {
        '0': 'caatinga01',
        '5': 'caatinga02',
        '10': 'caatinga03',
        '15': 'caatinga04',
        '20': 'caatinga05',        
        '25': 'solkan1201',
        '30': 'diegoGmail',      
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
#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB):
    assetId = params['assets']['outputAsset'] + '/' + nameB
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetId         
        }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")



gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
lsAnos = [k for k in range(params['initYear'], params['endYear'])]
lstROIsSave = []
arqFeitos = open("registros/ROIS_Path_Rows_Anos.txt", 'w+')
lst_ROIsFailsSoil = []
lst_ROIsFailsVeg = []
lst_ROIsFails = []
for biome_act in params['list_biomes']:
    for wrsP in params['lsPath'][biome_act][:]:   #    
        print( 'WRS_PATH # ' + str(wrsP))
        for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #
            # cont = gerenciador(cont, params)
            print('WRS_ROW # ' + str(wrsR))

            geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                    ee.Filter.eq('ROW', int(wrsR))).geometry() 
            
            for index, ano in enumerate(lsAnos):                
                print("==== ano {} : {} ====".format(index, ano))
                myreg = biome_act + '_' + wrsP + '_' + wrsR + '_' + str(ano)
                nameSaved = 'rois_fitted_image_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR
                # "rois_fitted_image_PANTANAL_1995_227_74_Soil"
                roisSoils = ee.FeatureCollection(params['folder_rois'] + nameSaved)
                roisVegs = ee.FeatureCollection(params['folder_roisVeg'] + nameSaved)   
                
                try: 
                    roisSoils = roisSoils.filter(ee.Filter.eq('class', 1))
                    sizeROIsSoil = roisSoils.size().getInfo() 
                except:
                    sizeROIsSoil = 0
                try:
                    sizeROIsVeg = roisVegs.size().getInfo() 
                except:
                    sizeROIsVeg = 0                
                
                if sizeROIsSoil > 0 and sizeROIsVeg > 0:
                    roisSoils = roisSoils.merge(roisVegs)
                    lstROIsSave.append(nameSaved)
                    processoExportar(roisSoils, nameSaved)
                    arqFeitos.write(nameSaved + '\n')
                else:
                    if sizeROIsSoil > 0:
                        lst_ROIsFailsVeg.append(nameSaved)
                    elif sizeROIsVeg > 0:
                        lst_ROIsFailsSoil.append(nameSaved)
                    else:
                        lst_ROIsFails.append(nameSaved)



arqSoil = open("registros/ROIS_Path_Rows_AnosFailsSoil.txt", 'w+')
for soil in lst_ROIsFailsSoil:
    arqSoil.write(soil + '\n')

arqVeg = open("registros/ROIS_Path_Rows_AnosFailsVeg.txt", 'w+')
for veg in lst_ROIsFailsVeg:
    arqVeg.write(veg + '\n')

arqFails = open("registros/ROIS_Path_Rows_AnosFails.txt", 'w+')
for fails in lst_ROIsFails:
    arqFails.write(fails + '\n')