#-*- coding utf-8 -*-
import ee
import gee
import sys
import random
import json
import collections
collections.Callable = collections.abc.Callable
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
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
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3',
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4'
    },
    'folder_rois': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil',   
    'folder_roiVeg': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2',
    'folder_rois_manual': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoilPtos'},
    'folder_output_rois': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsnotSoilRev',     
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
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'], # 
           '221' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'], # 
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
            '219':['73','74','75','76','77','79'],  # 						
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
            '1','2','3','4','5','6','220','221','222','223','224',
            '225','226','227','228','229','230','231','232','233' 
        ], # 
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': [
            '217','218','219','220','221','222','223','224','225',
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
    'numeroLimit': 110,
    'version': '3',
    'pmtGTB': {
        'numberOfTrees': 10, 
        'shrinkage': 0.1,         
        'samplingRate': 0.8, 
        'loss': "LeastSquares",#'Huber',#'LeastAbsoluteDeviation', 
        'seed': 0
    },
    'conta' : {
        '0': 'superconta',
        '50': 'caatinga01',
        '60': 'caatinga02',
        '70': 'caatinga03',
        '80': 'caatinga04',
        '90': 'caatinga05',        
        '100': 'solkan1201',
        # '90': 'diegoGmail',      
    },
}
#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB):
    
    assetOutput = params['folder_output_rois'] + '/' + nameB     
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetOutput          
        }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")

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

def re_exportROIs_notSoil(nkeyPathRow):
    lstBnd = ['min','max','stdDev','amp','median','mean']
    # dict_tiles = {}
    biomeAct = nkeyPathRow.split('_')[0]
    nWrsP = nkeyPathRow.split('_')[1]
    nWrsR = nkeyPathRow.split('_')[2]
    if nWrsP == 'ATLANTICA':
        biomeAct = nkeyPathRow.split('_')[0] + '_' + nkeyPathRow.split('_')[1]
        nWrsP = nkeyPathRow.split('_')[2]
        nWrsR = nkeyPathRow.split('_')[3]

    lsAnos = [k for k in range(params['initYear'], params['endYear'])]
    for index, mYear in enumerate(lsAnos):            
        print("==== ano {} : {} ====".format(index, mYear))
        nameROIs = "rois_fitted_image_" + biome_act + "_" + str(mYear) + "_" + str(nWrsP) + "_" + str(nWrsR)
        print("nome ==> " + nameROIs)
        assetROIs = params['folder_rois'] + "/" + nameROIs

        try:                    
            mapsSoil = ee.ImageCollection(params['assets']['inputAsset']).filter(
                                ee.Filter.eq('WRS_PATH', nWrsP)).filter(
                                    ee.Filter.eq('WRS_ROW', nWrsR)).filter(
                                        ee.Filter.eq('year', mYear))# .first();
            print("mapsSoil ", mapsSoil.size().getInfo());
            mapsSoil = mapsSoil.first()
            FeatTemp = ee.FeatureCollection(assetROIs)#  
            newROIs = mapsSoil.eq(1).selfMask().rename('class').sampleRegions(
                                    collection= FeatTemp.filter(ee.Filter.eq('class', 2)),
                                    properties= lstBnd,
                                    scale= 30,                                     
                                    dropNulls= True, 
                                    geometries= True
            )
            newROIs = newROIs.filter(ee.Filter.notNull('class'))
            newROIs = newROIs.remap([1], [0], 'class')
            processoExportar(newROIs, nameROIs)
        except:
            print("fail == " + nameROIs)


dictNameBiome = {
    'AMAZONIA': 'Amazônia', 
    'CERRADO': 'Cerrado',
    'CAATINGA': 'Caatinga',
    'MATA_ATLANTICA': 'Mata Atlântica', 
    'PAMPA': 'Pampa',
    'PANTANAL': 'Pantanal'
}
cont = 1
# cont = gerenciador(cont, params)

for biome_act in params['list_biomes']:
    for wrsP in params['lsPath'][biome_act][:]:   #    
        print( 'WRS_PATH # ' + str(wrsP))
        lstRows = []
        for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #
            cont = gerenciador(cont, params)
            print('WRS_ROW # ' + str(wrsR))
            keyPathRow = biome_act + "_" + str(wrsP) + "_" + str(wrsR)
            lstRows.append(keyPathRow)


        # create the pool with the default number of workers
        with ThreadPool() as pool:
            # issue one task for each call to the function
            for result in pool.map(re_exportROIs_notSoil, lstRows[:]):
                # handle the result
                print(f'>got {result}')
        
        # report that all tasks are completed
        print('WRS_PATH # ' + str(wrsP) + ' Done')

            
