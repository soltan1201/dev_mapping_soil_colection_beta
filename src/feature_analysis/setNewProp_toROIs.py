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
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84 
    'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
    'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'inputAssetMapSoilV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2A',
    'folder_roiKnow': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilA'},
    'folder_roiVeg': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2'},
    'folder_roiSoil': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil'},
    'folder_rois_manual': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoilPtos'},
    'numeroTask': 3,
    'numeroLimit': 70,
    'conta' : {
        '0': 'superconta',
        '50': 'caatinga01',
        '53': 'caatinga02',
        '56': 'caatinga03',
        '59': 'caatinga04',
        '62': 'caatinga05',        
        '65': 'solkan1201'      
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
dictLimiarBiome = {
    'AMAZONIA': 0.84, 
    'CERRADO': 0.84,
    'CAATINGA': 0.84,
    'MATA_ATLANTICA': 0.85, 
    'PAMPA': 0.84,
    'PANTANAL': 0.84
}


#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB):    
    assetOutput = params['outputAsset'] + '/' + nameB  
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetOutput          
        }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")

def colect_ROIsSetprop(idAssets):
    IdName = idAssets.split("/")[-1]
    partes = IdName.split("_")
    mybioma = partes[3]
    yyear = partes[-3]
    WrsP = partes[-2]
    WrsR = partes[-1]
    lstBnd = ['min','max','stdDev','amp','median','mean','class']
    if partes[3] == 'MATA':
        mybioma += '_' + partes[4] 

    limiarBioma = dictLimiarBiome[mybioma]
    featROIs = ee.FeatureCollection(idAssets)
    # sizeROIs = featROIs.size().getInfo()
    masksSOIL = ee.ImageCollection(params['inputAssetMapSoilV4']).filter(
                            ee.Filter.eq('year', int(yyear))).filter(
                                    ee.Filter.eq('WRS_PATH', str(WrsP))).filter(
                                            ee.Filter.eq('WRS_ROW', str(WrsR)))
    sizeImg = masksSOIL.size().getInfo()
    print(IdName, "numero de mask Soil", sizeImg)

    if sizeImg  > 0:
        # print(masksSOIL.getInfo())
        # levando de continmuo a binario
        masksSOIL = ee.Image(masksSOIL.first()).gt(limiarBioma)
        pmtroROIs = {
            'collection': featROIs, 
            'properties': lstBnd, 
            'scale': 30,
            'geometries': True
        }
        newROIsFeat = masksSOIL.rename('classeV4').unmask(0).sampleRegions(**pmtroROIs)
        newROIsFeat = newROIsFeat.filter(ee.Filter.eq('classeV4', 1))
        processoExportar(newROIsFeat, IdName)


def getPointsfromFolderManual(nameSearched):
    lstBiomas = ['AMAZONIA','CERRADO','MATA_ATLANTICA']
    dictCountsBiome = {
        'AMAZONIA': 0, 
        'CERRADO': 0,
        'CAATINGA': 0,
        'MATA_ATLANTICA': 0, 
        'PAMPA': 0,
        'PANTANAL': 0
    }

    dictSaida = {'id': params['outputAsset']}
    getlistFeat = ee.data.getList(dictSaida);
    lstFeatFeitos = []
    for idAsset in tqdm(getlistFeat):         
        path_ = idAsset.get('id')    
        lstFeatFeitos.append(path_.split("/")[-1])

    print("featureCollection  => " + params[nameSearched]['id'])
    getlistPtos = ee.data.getList(params[nameSearched]);   
    featColsPtos = []
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')   
        nameFeat =   path_.split("/")[-1]   
        partes = nameFeat.split('_')
        mybioma = partes[3]
        # print(path_, "  > ", mybioma)
        if partes[3] == 'MATA':
            mybioma += '_' + partes[4] 
        if mybioma in lstBiomas and nameFeat not in lstFeatFeitos:
            featColsPtos.append(path_) 
        
        val = dictCountsBiome[mybioma]
        val += 1
        dictCountsBiome[mybioma] = val
        
    return  featColsPtos, dictCountsBiome


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

cont = 0
# cont = gerenciador(cont, params)
# nameFolder = 'folder_roiVeg'
# nameFolder = 'folder_roiSoil'
nameFolder = 'folder_roiVeg'
lstAssetROIs, dictAssetROIs = getPointsfromFolderManual(nameFolder)
print('numero de assets ', len(lstAssetROIs))
for kkey, valCount in dictAssetROIs.items():
    print(kkey, " ", valCount)

# sys.exit()
inic= 10500
step = 100
for cc in range(0, len(lstAssetROIs[:]), step):    
    lstIdsPath = lstAssetROIs[cc: cc + step]
    print(cc, " < > : ",  len(lstIdsPath))
    # create the pool with the default number of workers
    with ThreadPool() as pool:
        # issue one task for each call to the function
        for result in pool.map(colect_ROIsSetprop, lstIdsPath):
            # handle the result
            print(f'>got {result}')
    # if cc > 200:
    #     sys.exit()

    cont = gerenciador(cont, params)

print(lstIdsPath[0])