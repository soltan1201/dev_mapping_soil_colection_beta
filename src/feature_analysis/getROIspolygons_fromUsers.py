#-*- coding utf-8 -*-
import ee
import gee 
import os 
import sys
import json
from tqdm import TMonitor, tqdm
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

def gerenciador(conta):    
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    print("activando conta de >> {} <<".format(conta))        
    gee.switch_user(conta)
    gee.init()        
    gee.tasks(n= 2, return_list= True)        


def getPolygonsfromFolder(inputROIs):
    
    getlistPtos = ee.data.getList(inputROIs);   
    lstFeatsPtos = [];
    # print("getlistPtos ", getlistPtos);
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        name = path_.split('/')[-1]
        lstFeatsPtos.append(name)                
        
    return  lstFeatsPtos

#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB, isEndmember):
    # assetOutput = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIs/' + nameB
    # assetOutput = 'projects/mapbiomas-arida/ROIsManual/' + nameB
    if isEndmember:
        assetOutput = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualEndmember/' + nameB
    else:
        assetOutput = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoil/' + nameB
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetOutput          
        }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")

param ={
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
ispermission = False
shpEndmember = False
dict_assets = {
    'bruno': {'id' : 'users/blobo170/Degradacao'},
    'daniela': {'id' : 'users/trabalhodani/degradacao'},
    'francielle': {'id' : 'users/trabalhofran/degradacao'},
    'lazaro': {'id' : 'users/lazarobritoagro/degradacao'}
}
dict_assetsEndmember = {
    'bruno': {'id' : 'users/blobo170/shpEndmembers'},
    'daniela': {'id' : 'users/trabalhodani/shpEndmembers'},
    'francielle': {'id' : 'users/trabalhofran/shpEndmembers'},
    'lazaro': {'id' : 'users/lazarobritoagro/shpEndmembers'}
}
dictReg = {
    'bruno': {},
    'daniela': {},
    'francielle': {},
    'lazaro': {}
}
# Set permissão in the file Asset 

lstAnalistas = ['lazaro']  #   'daniela', 'francielle', 'lazaro', 'bruno', 'daniela', 
if ispermission:
    for analista in lstAnalistas:
        if shpEndmember:
            assetFolder = dict_assetsEndmember[analista]
        else:     
            assetFolder = dict_assets[analista]
        print("reading from => ", assetFolder)
        dictAnalista = {}
        # gerenciador(analista)
        lstAssets = getPolygonsfromFolder(assetFolder)

        for cc, nameFeat in enumerate(lstAssets):
            idAssetSHP = assetFolder['id'] + '/' + nameFeat
            # set permissão in the file Asset
            comando = 'earthengine acl ch -u solkan1201@gmail.com:R ' + idAssetSHP
            os.system(comando)
            print(f" # {cc} acessando a ==> {idAssetSHP}")


else:
    gerenciador('solkan1201')
    folderManual = {"id": "projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoil"}
    lstAssetsNG = getPolygonsfromFolder(folderManual)
    for assetFeat in lstAssetsNG:
        print(" => ", assetFeat)
    # lstAssetsNG +=  ['shp_AMAZONIA_2020_14', 'shp_AMAZONIA_2005_13']

    
    allSHPs = ee.FeatureCollection([])
    lstAnalistas = ['lazaro', 'bruno', 'daniela', 'francielle']  #  , 'bruno', 'daniela' 'daniela', 'francielle',
    for analista in lstAnalistas:
        if shpEndmember:
            assetFolder = dict_assetsEndmember[analista]
        else:     
            assetFolder = dict_assets[analista]
        print("reading from => ", assetFolder)
        dictAnalista = {}
        
        lstAssets = getPolygonsfromFolder(assetFolder)
        # lstAssets = [
        #     "shp_CERRADO_1985_31","shp_CERRADO_1985_35","shp_CERRADO_1990_35","shp_CERRADO_1991_32",
        #     "shp_CERRADO_1992_33","shp_CERRADO_1995_35","shp_CERRADO_1996_32","shp_CERRADO_1997_33",
        #     "shp_CERRADO_2000_34","shp_CERRADO_2005_34","shp_CERRADO_2007_33","shp_CERRADO_2010_34",
        #     "shp_CERRADO_2012_33","shp_CERRADO_2014_31","shp_CERRADO_2016_32","shp_CERRADO_2021_32"
        # ]

        for nameFeat in lstAssets:
            if nameFeat not in lstAssetsNG:
                idAssetSHP = assetFolder['id'] + '/' + nameFeat
                # idAssetSHP = nameFeat
                # 
                featCol = ee.FeatureCollection(idAssetSHP)
                print("nome ==> ", nameFeat ) # , " size ", featCol.size().getInfo()
                dictAnalista[nameFeat] = int(featCol.size().getInfo())
                # print(featCol.first().getInfo())
                partes = nameFeat.split('_')
                biome = partes[1]
                if biome == 'MATA':
                    biome = partes[1] + '_' + partes[2]
                    yyear = partes[3]
                    region = partes[4]
                else:
                    yyear = partes[2]
                    region = partes[3]
                featCol = featCol.map(lambda feat: feat.set('biome', biome, 'year', yyear, 'region', region, 'analista', analista))
                # allSHPs = allSHPs.merge(featCol)
                processoExportar(featCol, nameFeat, shpEndmember)
        # sys.exit()

        dictReg[analista] = dictAnalista

    with open("registroAnalistas_p1.json", "w") as outfile:
        json.dump(dictReg, outfile)

    # gerenciador('solkan1201')
    # processoExportar(allSHPs, 'shp_polygons_coletado_manual_p1')