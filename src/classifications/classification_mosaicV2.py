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


params = {
    'assets': {
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84 
        'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",
        'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOIL'
    },
    'folder_rois': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsInt',    
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
           '219' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76'],		
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'], # 
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
            '222':['73','74','75','76','77','78','79','80','81'],		
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
        'AMAZONIA' : ['226','227','228','229','230','231','232','233'], # '1','2','3','4','5','6','220','221','222','223','224','225',
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230' ],#   
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], #    
        'PAMPA':['220','221','222','223','224','225'], # 
        'PANTANAL':['225','226','227','228']
    },  #    
    'list_biomes': ['AMAZONIA', 'CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'],
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

def GetSHPsfromVizinhos(vizinhosName, myGeom, mYear, nameBioma):

    ColectionPtos = ee.FeatureCollection([]);

    for idpathRow in tqdm(vizinhosName):         
        nameROIs = "rois_fitted_image_" + nameBioma + "_" + str(mYear) + "_" + idpathRow
        # "rois_fitted_image_PANTANAL_1995_227_74_Soil"
        try:
            FeatTemp = ee.FeatureCollection(params['folder_rois'] + "/" + nameROIs)#   
            sizeFeat =  FeatTemp.size().getInfo()
            if sizeFeat > 0:
                ColectionPtos = ColectionPtos.merge(FeatTemp);    
            # ColectionPtos = ee.Algorithms.If(ee.Algorithms.IsEqual(ee.Number(sizeFeat).gt(0), 1), 
            #                                     ColectionPtos.merge(FeatTemp), ColectionPtos)    
        # lst_asset.append(name)
        except:
            print("fails ", nameROIs)
    
    ColectionPtos = ee.FeatureCollection(ColectionPtos).filterBounds(myGeom);
    return  ColectionPtos


def getBandFeatures(imgMosYY):
    bandas_select = ['min','max','stdDev','amp']
    imgMin = imgMosYY.reduce(ee.Reducer.min()).rename('min')
    imgMax = imgMosYY.reduce(ee.Reducer.max()).rename('max')
    imgstdDev = imgMosYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
    imgAmp = imgMax.subtract(imgMin).rename('amp')                   
        
    imgMosYY = imgMosYY.addBands(imgMin).addBands(imgMax).addBands(
                        imgstdDev).addBands(imgAmp)

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


for kk, vvals in dictPathRowVis.items():
    if kk == '1_57':
        print(kk, " ", vvals)
   
exportROIs = True
numfeat = 5
 
lsAnos = [k for k in range(params['initYear'], params['endYear'])]
print(lsAnos)
gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
coletaSoil = True
# imgColmosaic = ee.ImageCollection(params['assets']['inputAsset'])
dictPath = {}
lstBnd = ['min','max','stdDev','amp','class']
bandas_imports = ['min','max','stdDev','amp']
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
biome_act = 'AMAZONIA'
cont = 0
# cont = gerenciador(0, params)

arqFeitos = open("registros/orbitas_tiles_Anos.txt", 'w+')
lst_imgFails = []
for wrsP in params['lsPath'][biome_act][:]:   #    
    print( 'WRS_PATH # ' + str(wrsP))
    for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #
        # cont = gerenciador(cont, params)
        print('WRS_ROW # ' + str(wrsR))
        fPathRow = 'T' + wrsP + '0' + wrsR
        
        geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                    ee.Filter.eq('ROW', int(wrsR))).geometry()
        keyPathRow = str(wrsP) + "_" + str(wrsR)
        
        for index, ano in enumerate(lsAnos):            
            print("==== ano {} : {} ====".format(index, ano))
            myreg = biome_act + '_' + wrsP + '_' + wrsR + '_' + str(ano)
            
            roisSoils = GetSHPsfromVizinhos(dictPathRowVis[keyPathRow], geoms.buffer(3500), ano, biome_act)      
            sizeROIs = roisSoils.size().getInfo() 
            print("SIZE ROIs =", sizeROIs)
            nameSaved = 'fitted_image_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR
            nameExport = 'classSoil_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR + 'V' + params['version']
            if sizeROIs > 0:            
                # print("rois aggregate ", roisSoils.aggregate_histogram('class').getInfo())
                try:
                    mosaic = ee.Image(params['assets']['inputAsset'] + '/' + nameSaved)
                    mosaic = getBandFeatures(mosaic)
                    classifierGTB = ee.Classifier.smileGradientTreeBoost(**params['pmtGTB'])\
                                        .train(roisSoils, 'class', bandas_imports)
                    classifiedGTB = mosaic.classify(classifierGTB, 'classification_' + str(ano))                
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
                    
                    exportImage(classifiedGTB, nameExport, geoms)
            
                except:                    
                    print('FAILS TO PROCESSING CLASS => ', )
                    arqFeitos.write(nameExport + '\n')
            else:                
                print('FAILS BY SIZE ROIs 0 => ', )
                arqFeitos.write(nameExport + '\n')
           
        
