#-*- coding utf-8 -*-
import ee
import os
from tqdm import tqdm
import gee #as gee
import sys
import json
import random
import math
import copy
import time
from datetime import date

from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
currentAc, projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= projAccount)
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


def getDictROIsPointsfromFolder(dict_path, bioma_searched):
    print("featureCollections in folder  => " + dict_path['id'].split("/")[-1])
    getlistPtos = ee.data.getList(dict_path);     
    dictPathRow = {}
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        # print(path_)
        if bioma_searched in path_:
            name = path_.split('/')[-1]
            myKeys = name[-11:]
            # print("adding ",  myKeys)
            dictPathRow[myKeys] = path_
        
    return  dictPathRow



def gerenciador(cont, paramet):    
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numSec = 60
    numberofChange = [kk for kk in paramet['conta'].keys()]    
    if str(cont) in numberofChange:
        if paramet['conta'][str(cont)] != currentAc:
            print("conta ativa >> {} <<".format(paramet['conta'][str(cont)]))        
            gee.switch_user(paramet['conta'][str(cont)])
            # print("esperando 0,1,2.... ")
            # time.sleep(30)
            print("inicializando Init() ... ")
            gee.init()  
            print("estamos em outra conta  ...  esperando mais 1:30 minutos ....")
            for ii in range(numSec):
                print(ii, end='\r')  
            time.sleep(numSec)               
            print("listando as tarefas ") 
            # gee.tasks(n= paramet['numeroTask'], return_list= True)       
        else:
            print(" --- ⚠️ Init in the same accounts before ---") 
    
    elif cont > paramet['numeroLimit']:
        cont = 0
    
    cont += 1    
    return cont



#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB):
    optExpD = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'folder': 'SHP_ptosSoilHarmIndexv2'          
        }
    taskD = ee.batch.Export.table.toDrive(**optExpD)
    taskD.start() 
    print("salvando ... on drive " + nameB + "..!")

param = {
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',   
    'asset_ndfia_harmonic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'asset_ndfia': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-ndfia',
    'folder_rois': {'id' : 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilA'},   
    'folder_roiVeg': {'id' : 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2A'},
    'foldernotSoil': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsnotSoilRev',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
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
            '226' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],	# 		
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
           '218' : ['63','64','65','69','70','71','72','73','74'], # 													
           '219' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76'], #  		
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'], # 
           '221' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'], # 
           '222' : ['64','65','66','67','68','69','70','71','72','73','74','75','76'],	# 
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
            '216':['68','69','70','71','72','73','74','75','76'], #		
            '217':['69','70','71','72','73','74','75','76'],				
            '218':['72','73','74','75','76','77'],								
            '219':['73','74','75','76','77','79'], # 						
            '220':['74','75','76','77','78','79','80','81'],				
            '221':['72','73','74','75','76','77','78','79','80','81'],
            '222':['73','74','75','76','77','78','79','80','81'], #		
            '223':['73','74','75','76',	'77','78','79','80','81'], # 	
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
            '227','228','229','230', '231','232','233' 
        ], # 
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': [
            '224','225',
            '226','227', '228','229','230'
        ],# '217', '218', '219','220','221','222','223',
        'MATA_ATLANTICA':[
            '214','215','216','217','218','219','220',
            '221','222','223','224','225'
        ], #    
        'PAMPA':[
            '220','221','222', '223','224','225'], # 
        'PANTANAL':['225','226','227','228']  # 
    },
    'list_biomes': [
        'AMAZONIA', 'CAATINGA','CERRADO',
        'MATA_ATLANTICA','PAMPA','PANTANAL'
    ],
    'initYear': 1985,
    'endYear': 2023,
    'numeroTask': 3,
    'numeroLimit': 24,
    'conta' : {
        '0': 'caatinga01',
        '8': 'caatinga02',
        '16': 'caatinga03'            
    },
};

mosaicHarms = ee.ImageCollection(param['asset_ndfia_harmonic'])
# print("show the first properties image in IC harmonicos ", mosaicHarms.first().getInfo());
print(mosaicHarms.aggregate_histogram('biome').getInfo());
# print(mosaicHarms.aggregate_histogram('year').getInfo());

mosaicNDFIa = ee.ImageCollection(param['asset_ndfia']);
# print("show the first properties in the NDFIa index  Collection ", mosaicNDFIa.first().getInfo());
print(mosaicNDFIa.aggregate_histogram('biome').getInfo());
# print(mosaicNDFIa.aggregate_histogram('year').getInfo());

biome_act = 'CERRADO'
dictROISpathSoil = getDictROIsPointsfromFolder(param['folder_rois'], biome_act)
dictROISpathVeg = getDictROIsPointsfromFolder(param['folder_roiVeg'], biome_act)
print(' Soil tamanho do dict ', len(list(dictROISpathSoil.keys())))
print(' Veg tamanho do dict ', len(list(dictROISpathVeg.keys())))

lstKeysSoil = list(dictROISpathSoil.keys())
lstKeysVeg = list(dictROISpathVeg.keys())
lsAnos = [k for k in range(param['initYear'], param['endYear'] + 1)]
print("anos a serem coletados ", lsAnos)

# sys.exit()
cont = gerenciador(0, param) 
gradeLandsat = ee.FeatureCollection(param['gradeLandsat'])

for wrsP in param['lsPath'][biome_act][:]:   #    
    print( '🏁 WRS_PATH # 🏁' + str(wrsP))
    for wrsR in param['lsGrade'][biome_act][wrsP][:]:   #
        print('🏁 WRS_ROW # 🏁 ' + str(wrsR))       
        
        geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                    ee.Filter.eq('ROW', int(wrsR))).geometry()

        lstBandasHarm = []
        lstBandasInd = []
        imgRowPathHarm = ee.Image().toInt16()    
        imgRowPathInd = ee.Image().toInt16()                          

        for cc, myear in enumerate(lsAnos[:]):
            print(f" {cc} ▶️ processing year ➡️ {myear}")
            keyPathRow = f"{myear}_{wrsP}_{wrsR}"    
            mosaicHarms = (
                    ee.ImageCollection(param['asset_ndfia_harmonic'])
                        .filter(ee.Filter.eq('WRS_PATH', wrsP))    
                        .filter(ee.Filter.eq('WRS_ROW', wrsR)) 
                        .filter(ee.Filter.eq('year', myear)) 
                )
            mosaicHarms = mosaicHarms.first()
            # imgRowPathHarm = imgRowPathHarm.addBands(mosaicHarms)            
            # bandasAdd = mosaicHarms.bandNames().getInfo()
            # lstBandasHarm += bandasAdd
            # print("banda a serem addicionadas => ", bandasAdd)

            mosaicNDFIaIndex = (
                    ee.ImageCollection(param['asset_ndfia'])
                        .filter(ee.Filter.eq('WRS_PATH', wrsP))    
                        .filter(ee.Filter.eq('WRS_ROW', wrsR)) 
                        .filter(ee.Filter.eq('year', myear)) 
                )
            mosaicNDFIaIndex = mosaicNDFIaIndex.first()
            # imgRowPathInd = imgRowPathInd.addBands(mosaicNDFIaIndex)
            # bandasAdd = mosaicNDFIaIndex.bandNames().getInfo()
            # lstBandasInd += bandasAdd
            # print("banda a serem addicionadas NDFIa index \n  ========> ", bandasAdd)


            # imgRowPathHarm = imgRowPathHarm.select(lstBandasHarm)
            # imgRowPathInd = imgRowPathInd.select(lstBandasInd)
            
            for cc, yyear in enumerate(lsAnos):
                print(f" {cc} ▶️ processing year ➡️ {yyear}")
                keyPathRow = f"{yyear}_{wrsP}_{wrsR}"            
                size_featROIsSoil = 0
                size_featROIsVeg = 0
                roisPathRowHarm = ee.FeatureCollection([])
                roisPathRowInd = ee.FeatureCollection([])
                try: 
                    if keyPathRow in lstKeysSoil:
                        path_asset_soil = dictROISpathSoil[keyPathRow]
                        print(" colect Ptos in == ", path_asset_soil)
                        featROIsSoil = ee.FeatureCollection(path_asset_soil)#.select(['class'])
                        print(featROIsSoil.first().getInfo())
                        size_featROIsSoil  = featROIsSoil.size().getInfo()
                        print("size_featROIsSoil = ", size_featROIsSoil)
                    else:
                        featROIsSoil = ee.FeatureCollection([])
                except:
                    print('fails in Soil  ', keyPathRow)

                try:
                    if keyPathRow in lstKeysVeg:
                        path_asset_veg = dictROISpathVeg[keyPathRow]
                        print(" colect Ptos in == ", path_asset_veg.replace("projects/earthengine-legacy/assets/", ""))
                        featROIsVeg = ee.FeatureCollection(path_asset_veg)#.select(['class'])
                        print(featROIsVeg.first().getInfo())
                        size_featROIsVeg = featROIsVeg.size().getInfo()
                        print("size_featROIsVeg = ", size_featROIsVeg)
                    else:
                        featROIsVeg = ee.FeatureCollection([])
                except:
                    print('fails  in Vegetação ', keyPathRow)
                
                if size_featROIsSoil > 0 and size_featROIsVeg > 0:
                    featROIs = featROIsSoil.merge(featROIsVeg)
                elif size_featROIsSoil > 0:
                    featROIs = featROIsSoil
                elif size_featROIsVeg > 0:
                    featROIs = featROIsVeg
                else:
                    featROIs = ee.FeatureCollection([])

                    continue

                

                if size_featROIsSoil > 0 or size_featROIsVeg > 0:

                    pmtSample= {
                                'collection': featROIs,
                                'properties': ['class', 'year'],                                         
                                'scale': 30,                            
                                # 'projection': 'EPSG:3665',                        
                                'geometries': True
                            }
                    points = mosaicHarms.sampleRegions(**pmtSample)   
                    # roisPathRowHarm = roisPathRow.merge(points)  
                    roisPathRowHarm = points      

                    #  addiding the same ptos in the other mosaic 
                    pointsNDFIa = mosaicNDFIaIndex.sampleRegions(**pmtSample)
                    # roisPathRowInd = roisPathRowInd.merge(pointsNDFIa)
                    roisPathRowInd = pointsNDFIa
                    
                nameROIsExp = f"rois_harm_{biome_act}_{myear}_{wrsP}_{wrsR}_{yyear}"
                processoExportar(roisPathRowHarm, nameROIsExp)
                nameROIsExp = f"rois_Index_{biome_act}_{myear}_{wrsP}_{wrsR}_{yyear}"
                processoExportar(roisPathRowInd, nameROIsExp)
                # using sleep() to hault the code execution
            time.sleep(10)  # import time
        
        cont = gerenciador(cont, param) 
        sys.exit()