#-*- coding utf-8 -*-
import ee
import os
import gee
import sys
import random
import json
import collections
collections.Callable = collections.abc.Callable
from tqdm import tqdm
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


params = {
    'assets': {
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84 
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",
        'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3'
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
    'numeroLimit': 70,
    'version': '3',
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
        '60': 'caatinga04',
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

def GetSHPsfromVizinhos(vizinhosName, myGeom, mYear, nameBioma):

    ColectionPtos = ee.FeatureCollection([]);
    print(params['folder_rois'])
    for idpathRow in tqdm(vizinhosName):         
        nameROIs = "rois_fitted_image_" + nameBioma + "_" + str(mYear) + "_" + idpathRow
        print("nome ==> " + nameROIs)
        # print(params['folder_rois'] + "/" + nameROIs)
        # "rois_fitted_image_PANTANAL_1995_227_74_Soil"

        try:
            FeatTemp = ee.FeatureCollection(params['folder_rois'] + "/" + nameROIs)#  
            sizeFeat =  FeatTemp.size().getInfo()
        except:
            sizeFeat = 0

        try:
            print("load feat Veg")
            feat_tmpV = ee.FeatureCollection(params['folder_roiVeg'] + "/" + nameROIs)
            sizeFeatV = feat_tmpV.size().getInfo()
        except:
            sizeFeatV = 0
        
        # print(" size ", sizeFeat)
        if sizeFeat > 0 and sizeFeatV > 0:
            ColectionPtos = ColectionPtos.merge(FeatTemp).merge(feat_tmpV);    
        elif sizeFeat > 0:
            ColectionPtos = ColectionPtos.merge(FeatTemp)
        elif sizeFeatV > 0:
            ColectionPtos = ColectionPtos.merge(feat_tmpV); 
            
        else:
            pass
        # ColectionPtos = ee.Algorithms.If(ee.Algorithms.IsEqual(ee.Number(sizeFeat).gt(0), 1), 
        #                                     ColectionPtos.merge(FeatTemp), ColectionPtos)    

        
    
    ColectionPtos = ee.FeatureCollection(ColectionPtos)# .filterBounds(myGeom);
    return  ColectionPtos


def getPointsfromFolderManual(nameSearched):
    print("featureCollection manual => " + nameSearched)
    getlistPtos = ee.data.getList(params['folder_rois_manual']);   
    featColsPtos = ee.FeatureCollection([])
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        name = path_.split('/')[-1]
        if nameSearched in name:
            feat_tmp = ee.FeatureCollection(path_)
            featColsPtos = featColsPtos.merge(feat_tmp)    
        
    return  featColsPtos


def getRegion_fromCena(dictReg, idCena):
    lstReg = [kk for kk in dictReg.keys()]
    for kreg, lstCenas in dictReg.items():
        if idCena in lstCenas:
            return kreg

    return lstReg[0]

def getBandFeatures(imgMosYY):
    bandas_select = ['min','max','stdDev','amp','median','mean']
    imgMedian = imgMosYY.reduce(ee.Reducer.median()).rename('median')
    imgMean = imgMosYY.reduce(ee.Reducer.mean()).rename('mean')
    imgMin = imgMosYY.reduce(ee.Reducer.min()).rename('min')
    imgMax = imgMosYY.reduce(ee.Reducer.max()).rename('max')
    imgstdDev = imgMosYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
    imgAmp = imgMax.subtract(imgMin).rename('amp')                   
        
    imgMosYY = imgMosYY.addBands(imgMin).addBands(imgMax).addBands(
                    imgstdDev).addBands(imgAmp).addBands(imgMean
                        ).addBands(imgMedian)

    return imgMosYY.select(bandas_select)

def exportImage(imgYear, name, geom):        
    idasset =  params['assets']['outputAsset'] + '/' + name
    optExp = {   
        'image': imgYear, 
        'description': name, 
        'assetId': idasset, 
        'region': geom.getInfo()['coordinates'],  #getInfo(), #
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy": {".default": "mode"}
    }

    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + name + "..!")

dictPathRowVis = {}
# Opening JSON file
with open('list_PathRow_Vizinhos.json') as json_file:
    dictPathRowVis = json.load(json_file)

lstParPathRowViz = []
for kk, vvals in dictPathRowVis.items():
    lstParPathRowViz.append(kk)
    if kk == '1_57':    # '220_64', '220_69'
        print(kk, " ", vvals)

# Opening JSON file
with open('dict_PathRow_toReviewer.json') as json_file:
    dict_biomeReg = json.load(json_file)


exportROIs = True
numfeat = 5

lsAnos = [k for k in range(params['initYear'], params['endYear'] + 1)]
lsAnos = [2023]
print(lsAnos)
gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
coletaSoil = True
# imgColmosaic = ee.ImageCollection(params['assets']['inputAsset'])
dictPath = {}
lstBnd = ['min','max','stdDev','amp','median','mean','class']
bandas_imports = ['min','max','stdDev','amp','median','mean']
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
biome_act = 'CAATINGA'
cont = 0
cont = gerenciador(cont, params)

regProcess = [12,13,14]
# ROIsManual = getPointsfromFolderManual(biome_act)
# sizeROIsM = ROIsManual.size().getInfo()
# print("size ROIS manual = ", sizeROIsM)
# print("rois aggregate ", ROIsManual.aggregate_histogram('class').getInfo())
# sys.exit()

arqFeitos = open("registros/orbitas_tiles_AnosV4.txt", 'w+')
lst_imgFails = [] 
for wrsP in params['lsPath'][biome_act][:]:   #    
    print( 'WRS_PATH # ' + str(wrsP))
    for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #
        cont = gerenciador(cont, params)
        print('WRS_ROW # ' + str(wrsR))
        fPathRow = 'T' + wrsP + '0' + wrsR
        
        geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                    ee.Filter.eq('ROW', int(wrsR))).geometry()
        keyPathRow = str(wrsP) + "_" + str(wrsR)

        regpath = getRegion_fromCena(dict_biomeReg[biome_act], keyPathRow)
        print(f" Cena {keyPathRow} is in region {regpath}")

        lstOrbViz = dictPathRowVis[keyPathRow]
        print("list de orbita de Vizinhos ", lstOrbViz)

        for index, ano in enumerate(lsAnos):            
            print("==== ano {} : {} ====".format(index, ano))
            if ano < params['endYear']:
                ROIs_Viz = GetSHPsfromVizinhos(lstOrbViz, geoms, ano, biome_act)
            else:
                ROIs_Viz = GetSHPsfromVizinhos(lstOrbViz, geoms, 2022, biome_act)
            sizeROIs = ee.FeatureCollection(ROIs_Viz).size().getInfo()
            print("==============first size conditions = ", sizeROIs)
            exit()
            if sizeROIs == 0:
                lst_Viz = []
                for cc,nviz in enumerate(lstOrbViz):
                    lstOrbV = dictPathRowVis[nviz]                    
                    for odViz in lstOrbV:
                        if odViz not in lstOrbViz:
                            lst_Viz.append(odViz)

                print(f" novos vizinhos   {lst_Viz}")
                ROIs_Viz = GetSHPsfromVizinhos(lst_Viz, geoms, ano, biome_act)  
                ROIs_Viz = ee.FeatureCollection(ROIs_Viz)             
                sizeROIs = ROIs_Viz.size().getInfo()
                print("sizeROIs ", sizeROIs)

            nameROIsManual = biome_act + "_" + str(ano) + '_' + regpath
            ROIsManual = getPointsfromFolderManual(nameROIsManual)
            sizeROIsM = ROIsManual.size().getInfo()
            print("size ROIS manual = ", sizeROIsM)
            nameExport = 'classSoil_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR + 'V' + params['version'] 
            if sizeROIs > 0:
                print("  =>  ", ROIs_Viz.aggregate_histogram('class').getInfo())  
                
                nameSaved = 'fitted_image_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR
                

                if sizeROIsM > 0:
                    ROIs_Viz = ROIs_Viz.merge(ROIsManual)               

                try:
                    mosaic = ee.Image(params['assets']['inputAsset'] + '/' + nameSaved)
                    numberBands = mosaic.bandNames().getInfo()

                    if len(numberBands) > 1:
                        mosaic = getBandFeatures(mosaic)

                        classifierGTB = ee.Classifier.smileGradientTreeBoost(**params['pmtGTB'])\
                                            .train(ROIs_Viz, 'class', bandas_imports)
                        classifiedGTB = mosaic.classify(classifierGTB, 'classification_' + str(ano))                
                        
                    else:
                        classifiedGTB = ee.Image.constant(0).clip(geoms)

                    mydict = {                        
                        'version': params['version'],
                        'year': ano,
                        'WRS_PATH': wrsP,
                        'WRS_ROW': wrsR,
                        'biome': biome_act,
                        'layer': 'soil',
                        'sensor': 'Landsat',
                        'source': 'geodatin'                
                    }         
                    classifiedGTB = classifiedGTB.set(mydict)
                    # sys.exit()
                    exportImage(classifiedGTB, nameExport, geoms)
            
                except:                    
                    print('FAILS TO PROCESSING CLASS => ', )
                    arqFeitos.write(nameExport + '\n')
            else:                
                
                print('FAILS BY SIZE ROIs 0 => ', )
                arqFeitos.write(nameExport + '\n')
        
    
