#-*- coding utf-8 -*-
import ee
import gee
import sys
import random
import json
import collections
collections.Callable = collections.abc.Callable
import pandas as pd
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
        'inputAssetMapSoilV3': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3',
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4'
    },
    'folder_rois': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilB',   
    'folder_roiVeg': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVegB',
    'foldernotSoil': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsnotSoilRev',
    # projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoilPtos
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
            '217','218','219','220','221','222','223','224','225',
            '226','227', '228','229','230'
        ],#   
        'MATA_ATLANTICA':[
            '214','215','216','217','218','219','220',
            '221','222','223','224','225'
        ], #    
        'PAMPA':[
            '220','221','222', '223','224','225'], # 
        'PANTANAL':['225','226','227','228']  # 
    },  #    
    'list_biomes': [
        'AMAZONIA', 'CAATINGA','CERRADO',
        'MATA_ATLANTICA','PAMPA','PANTANAL'
    ],
    'initYear': 1985,
    'endYear': 2023,
    'numeroTask': 3,
    'numeroLimit': 40,
    'version': '5',
    'pmtGTB': {
        'numberOfTrees': 16, 
        'shrinkage': 0.1,  
        'maxNodes': 3,
        'samplingRate': 0.8, 
        'loss': "LeastSquares",#'Huber',#'LeastAbsoluteDeviation', 
        'seed': 0
    },
    'conta' : {
        '0': 'caatinga01',
        '5': 'superconta',
        '10': 'caatinga02',
        # '15': 'caatinga03',
        '20': 'caatinga04',
        '30': 'caatinga05',        
        # '35': 'solkan1201',
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
dictHypePmtro = {
    'region_31': {'learning_rate': 1, 'max_features': 4, 'n_estimators': 35},
    'region_32': {'learning_rate': 1, 'max_features': 5, 'n_estimators': 35},
    'region_33': {'learning_rate': 1, 'max_features': 3, 'n_estimators': 35},
    'region_35': {'learning_rate': 1, 'max_features': 4, 'n_estimators': 35},
    'region_34': {'learning_rate': 1, 'max_features': 4, 'n_estimators': 35}
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

    # pathDictCoord = f"coordenates/dictCoordROIsPathRow_{nameBioma}.json"
    # with open(pathDictCoord) as json_file:
    #     dictCoordPathRow = json.load(json_file)

    ColectionPtos = ee.FeatureCollection([]);
    for idpathRow in tqdm(vizinhosName):         
        nameROIs = "rois_fitted_image_" + nameBioma + "_" + str(mYear) + "_" + idpathRow
        print("nome ==> " + nameROIs)
        # print(params['folder_rois'] + "/" + nameROIs)
        # "rois_fitted_image_PANTANAL_1995_227_74_Soil"
        # "rois_fitted_image_AMAZONIA_1985_220_63"

        try:
            FeatTemp = ee.FeatureCollection(params['folder_rois'] + "/" + nameROIs)# 
            FeatTemp = FeatTemp.remap([0,1,2], [0,1,0], 'class')
            # FeatTemp = FeatTemp.filter(ee.Filter.eq('class', 1)) 
            sizeFeat =  FeatTemp.size().getInfo()
        except:
            sizeFeat = 0

        # try:
        #     # print("esta lindo estes dados " + nameROIs)
        #     FeatTempSoil = ee.FeatureCollection(params['folder_rois'] + "/" + nameROIs)#  
        #     FeatTempSoil = FeatTempSoil.filter(ee.Filter.eq('class', 2))
        #     FeatTempSoil = FeatTempSoil.remap([2], [0], 'class')
        #     # sizeFeatnotSoil =  FeatTempSoil.size().getInfo()
        #     # print("aqui size Feat Soil ", sizeFeatnotSoil)

        #     fTempnotSoil = ee.FeatureCollection(params['foldernotSoil'] + "/" + nameROIs)#             
        #     # sizefNotSoil =  fTempnotSoil.size().getInfo()
        #     # print("só coordenadas ", sizefNotSoil)
        #     fTempnotSoil = fTempnotSoil.map(lambda feat: feat.buffer(30))
            
        #     # lstCoordPoints = dictCoordPathRow[nameROIs]
        #     # https://code.earthengine.google.com/8809aa0b3277f00b2b234d1fecc12765
        #     def compareCoord(feat):
        #         nfeatC = fTempnotSoil.filterBounds(feat.geometry())
        #         sizeFeat =  nfeatC.size()
        #         featRet = ee.Algorithms.If(
        #                         ee.Algorithms.IsEqual(ee.Number(sizeFeat).gt(0), 1), 
        #                         feat.set("stay", True), 
        #                         feat.set("stay", False))
        #         return featRet
        #     # print("processing filterBounds")
        #     FeatTempCruzSoil = FeatTempSoil.map(lambda feat : compareCoord(feat))
        #     # print("cruzado ", FeatTempCruzSoil.size().getInfo())
        #     featTempnotSoil = FeatTempCruzSoil.filter(ee.Filter.eq('stay', True))
        #     sizeFeatnotSoil =  featTempnotSoil.size().getInfo()
        #     # print("tamanho filtrado ", sizeFeatnotSoil)

        # except:
        #     sizeFeatnotSoil = 0

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
            # if sizeFeatnotSoil > 0:
            #     ColectionPtos = ColectionPtos.merge(featTempnotSoil)
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
            print("adding ", name )
            feat_tmp = ee.FeatureCollection(path_)
            featColsPtos = featColsPtos.merge(feat_tmp)    
        
    return  featColsPtos

def getRegion_fromCena(dictReg, idCena):
    lstReg = [kk for kk in dictReg.keys()]
    for kreg, lstCenas in dictReg.items():
        if idCena in lstCenas:
            return kreg

    return lstReg[0]

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


def getBandFeatures(imgMosYY):
    bandas_select = ['min','max','stdDev','amp','median','mean', 'min_contrast', 'min_diss', 'min_savg']
    imgMedian = imgMosYY.reduce(ee.Reducer.median()).rename('median')
    imgMean = imgMosYY.reduce(ee.Reducer.mean()).rename('mean')
    imgMin = imgMosYY.reduce(ee.Reducer.min()).rename('min')
    imgTextura = agregateBandsTexturasGLCM(imgMin)
    imgMax = imgMosYY.reduce(ee.Reducer.max()).rename('max')
    imgstdDev = imgMosYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
    imgAmp = imgMax.subtract(imgMin).rename('amp')                   
        
    imgMosYY = imgMosYY.addBands(imgMin).addBands(imgMax).addBands(
                    imgstdDev).addBands(imgAmp).addBands(imgMean
                        ).addBands(imgMedian).addBands(imgTextura)

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


def get_theBest_hyperparameter_tuning(nameRegion):
    npath = f"ROIs/rois_shp_CERRADO_{nameRegion}_fineTuring.csv"
    print("reading " + npath)
    tableHP_CSV = pd.read_csv(npath)
    nrow = tableHP_CSV.iloc[0]
    learning_rate = nrow["learning_rate"]
    n_estimators = nrow["n_estimators"]
    max_features = nrow["max_features"]

    return learning_rate, n_estimators, max_features


def export_classification_soilMap(nkeyPathRow):
    print("processing " + nkeyPathRow)
    lstimgMapeadas = []
    arqFeitos = open('registros/classificacion_version4.txt', 'r')
    for linha in arqFeitos:
        linha = linha[:-1]
        lstimgMapeadas.append(linha)

    arqFeitos.close()

    dict_tiles = {}
    mapsSoilsV3 = ee.ImageCollection(params['assets']['inputAssetMapSoilV3']);
    biomeAct = nkeyPathRow.split('_')[0]
    nWrsP = nkeyPathRow.split('_')[1]
    nWrsR = nkeyPathRow.split('_')[2]
    nnReg = nkeyPathRow.split('_')[3]

    if nWrsP == 'ATLANTICA':
        biomeAct = nkeyPathRow.split('_')[0] + '_' + nkeyPathRow.split('_')[1]
        nWrsP = nkeyPathRow.split('_')[2]
        nWrsR = nkeyPathRow.split('_')[3]
        nnReg = nkeyPathRow.split('_')[4]

    geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(nWrsP))).filter(            
                            ee.Filter.eq('ROW', int(nWrsR))).geometry()   

    keyPathRowReg = str(nWrsP) + "_" + str(nWrsR) + "_" + str(nnReg)

    # lstOrbViz = dictPathRowVis[keyPathRow]
    # print("list de orbita de Vizinhos ", lstOrbViz)
    arqFeitos = open('registros/classificacion_version4.txt', '+a')

    lstBandsImport = []
    for kkey, vval in dict_bandImps[nnReg].items():
        if vval > 0.2:
            lstBandsImport.append(kkey)

    print("the bands more importance are ", lstBandsImport)

    learn_rate, n_est, max_feat = get_theBest_hyperparameter_tuning(nnReg)
    params['pmtGTB']['numberOfTrees'] = n_est
    params['pmtGTB']['shrinkage'] = learn_rate
    params['pmtGTB']['maxNodes'] = max_feat

    ROIsManual = getPointsfromFolderManual(nnReg)
    sizeROIsM = ROIsManual.size().getInfo()
    print(f"size ROIS manual by region {nnReg} from all Years = {sizeROIsM}")

    # sys.exit()
    lsAnos = [k for k in range(params['initYear'], params['endYear'])]  #
    for index, yyear in enumerate(lsAnos):            
        # # print("==== ano {} : {} ====".format(index, yyear))
        # nameSaved = 'fitted_image_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR        
        nameExport = 'classSoil_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR + 'V' + params['version'] 

        # keysdict = str(yyear) + '_' + nWrsP + '_' + nWrsR
        # dict_Im = {}
        if nameExport not in lstimgMapeadas:
            print("==== ano {} : {} ====".format(index, yyear))
            nameROIsManual = biomeAct + "_" + str(yyear) + '_' + nnReg          

            if sizeROIsM > 0:
                # print("  =>  ", ROIs_Viz.aggregate_histogram('class').getInfo())              
                nameSaved = 'fitted_image_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR 
                
                mosaico = ee.ImageCollection(params['assets']['inputAsset']).filter(
                                        ee.Filter.eq('WRS_PATH', str(nWrsP))).filter(            
                                            ee.Filter.eq('WRS_ROW', str(nWrsR))).filter(
                                                ee.Filter.eq('year', yyear))
                numeroIm = mosaico.size().getInfo()
                if numeroIm > 0:
                    # get the first image 
                    mosaico = mosaico.first()
                    numberBands = mosaico.bandNames().getInfo()
                    if len(numberBands) > 1:
                        mosaico = getBandFeatures(mosaico)
                        # print("bandas carregadas ", mosaico.bandNames().getInfo());
                        mapsSoilsV3YY = mapsSoilsV3.filter(ee.Filter.eq('WRS_PATH', nWrsP)).filter(
                                                ee.Filter.eq('WRS_ROW', nWrsR)).filter(
                                                    ee.Filter.eq('year', yyear)).max().eq(1) 
                        ptroConvMin = {
                            'radius': 1,
                            'units': "pixels",
                            'normalize': False
                        };
                        pmtrosfocalMin = {
                            'units': "pixels", 
                            'iterations': 1,
                            'kernel': ee.Kernel.square(**ptroConvMin)
                        };
                        ptroConvMax = {
                            'radius': 1.5,
                            'units': "pixels",
                            'normalize': False
                        };
                        pmtrosfocalMax = {
                            'units': "pixels", 
                            'iterations': 1,
                            'kernel': ee.Kernel.square(**ptroConvMin)
                        };
                        # mapsSoilsV3YY = mapsSoilsV3YY.focalMin(**pmtrosfocalMin).focalMin(**pmtrosfocalMax)
                        mapsSoilsV3YY = mapsSoilsV3YY.focalMin(**pmtrosfocalMax)
                        classifierGTB = ee.Classifier.smileGradientTreeBoost(**params['pmtGTB']).setOutputMode(
                                                    'PROBABILITY').train(ROIsManual, 'classe', lstBandsImport)
                        
                        classifiedGTB = mosaico.updateMask(mapsSoilsV3YY).classify(classifierGTB, 'classification_' + str(yyear))                    
                    else:
                        classifiedGTB = ee.Image.constant(0).clip(geoms)
                else:
                    classifiedGTB = ee.Image.constant(0).clip(geoms)

                mydict = {                        
                    'version': '5',
                    'year': yyear,
                    'WRS_PATH': nWrsP,
                    'WRS_ROW': nWrsR,
                    'biome': biomeAct,
                    'region': nnReg,
                    'layer': 'soil',
                    'sensor': 'Landsat',
                    'source': 'geodatin'                
                }         
                classifiedGTB = classifiedGTB.set(mydict)
                # sys.exit()
                exportImage(classifiedGTB, nameExport, geoms)
                arqFeitos.write(nameExport + '\n')
                # except:                    
                #     print('FAILS TO PROCESSING CLASS => ', )
                #     arqFeitos.write(nameExport + '\n')
            else:                
                
                print('FAILS BY SIZE ROIs 0 => ', )
                arqFeitos.write(nameExport + '\n')
        else:
            print("======== {nameExport}   done ========= ")


def export_classification_soilMap_by_Year(nkeyPathRow_YY):
    lstimgMapeadas = []
    dict_tiles = {}
    mapsSoilsV3 = ee.ImageCollection(params['assets']['inputAssetMapSoilV3']);
    ## nameExport = 'classSoil_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR + 'V' + params['version'] 
    partes = nkeyPathRow_YY.split('_')
    print("partes ", partes)
    biomeAct = partes[1]
    yyear = partes[2]
    nWrsP = partes[3]
    nWrsR = partes[4]
    if biomeAct == 'MATA':
        print("bioma ", biomeAct)
        biomeAct = partes[1] + '_' + partes[2]
        yyear = partes[3]
        nWrsP = partes[4]
        nWrsR = partes[5]    
    yyear = int(yyear)

    nWrsR = nWrsR.replace('V' + params['version'], "")
    geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(nWrsP))).filter(            
                            ee.Filter.eq('ROW', int(nWrsR))).geometry()   

    keyPathRow = str(nWrsP) + "_" + str(nWrsR)
    regpath = getRegion_fromCena(dict_biomeReg[biomeAct], keyPathRow)
    print(f" Cena {keyPathRow} is in region {regpath}")

    lstOrbViz = dictPathRowVis[keyPathRow]
    print("list de orbita de Vizinhos ", lstOrbViz)
   
    nameExport = 'classSoil_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR + 'V' + params['version']         
    print("==== ano {} ====".format(yyear))
    ROIs_Viz = GetSHPsfromVizinhos(lstOrbViz, geoms, yyear, biomeAct)
    sizeROIs = ee.FeatureCollection(ROIs_Viz).size().getInfo()
    print("==============first size conditions = ", sizeROIs)

    if sizeROIs == 0:
        lst_Viz = []
        for cc,nviz in enumerate(lstOrbViz):
            lstOrbV = dictPathRowVis[nviz]                    
            for odViz in lstOrbV:
                if odViz not in lstOrbViz:
                    lst_Viz.append(odViz)

        print(f" novos vizinhos   {lst_Viz}")
        ROIs_Viz = GetSHPsfromVizinhos(lst_Viz, geoms, yyear, biomeAct)  
        ROIs_Viz = ee.FeatureCollection(ROIs_Viz)             
        sizeROIs = ROIs_Viz.size().getInfo()
        print("sizeROIs ", sizeROIs)

    nameROIsManual = biomeAct + "_" + str(yyear) + '_' + regpath
    ROIsManual = getPointsfromFolderManual(nameROIsManual)
    sizeROIsM = ROIsManual.size().getInfo()
    print("size ROIS manual = ", sizeROIsM)
    print("and sizeROIs ", sizeROIs)

    if sizeROIs > 0:
        print("  =>  ", ROIs_Viz.aggregate_histogram('class').getInfo())              
        nameSaved = 'fitted_image_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR        

        if sizeROIsM > 0:
            ROIs_Viz = ROIs_Viz.merge(ROIsManual)               

        try:
            mosaico = ee.ImageCollection(params['assets']['inputAsset']).filter(
                ee.Filter.eq('WRS_PATH', str(nWrsP))).filter(            
                    ee.Filter.eq('WRS_ROW', str(nWrsR))).filter(
                        ee.Filter.eq('year', yyear))
            numeroIm = mosaic.size().getInfo()

            if numeroIm > 0:
                # get the first image 
                mosaico = mosaico.first()
                numberBands = mosaico.bandNames().getInfo()                
                if len(numberBands) > 1:
                    mosaico = getBandFeatures(mosaico)
                    print("bandas carregadas ", mosaico.bandNames().getInfo());
                    sys.exit()
                    mapsSoilsV3YY = mapsSoilsV3.filter(ee.Filter.eq('WRS_PATH', nWrsP)).filter(
                                            ee.Filter.eq('WRS_ROW', nWrsR)).filter(
                                                ee.Filter.eq('year', yyear)).first().eq(1) 
                    ptroConvMin = {
                        'radius': 3,
                        'units': "pixels",
                        'normalize': False
                    };
                    pmtrosfocalMin = {
                        'units': "pixels", 
                        'iterations': 1,
                        'kernel': ee.Kernel.square(**ptroConvMin)
                    };
                    mapsSoilsV3YY = mapsSoilsV3YY.focalMin(**pmtrosfocalMin)
                    classifierGTB = ee.Classifier.smileGradientTreeBoost(**params['pmtGTB']).setOutputMode(
                                                'PROBABILITY').train(ROIs_Viz, 'class', bandas_imports)
                    classifiedGTB = mosaico.updateMask(mapsSoilsV3YY).classify(classifierGTB, 'classification_' + str(yyear))                    
                else:
                    classifiedGTB = ee.Image.constant(0).clip(geoms)
            else:
                classifiedGTB = ee.Image.constant(0).clip(geoms)

            mydict = {                        
                'version': params['version'],
                'year': yyear,
                'WRS_PATH': nWrsP,
                'WRS_ROW': nWrsR,
                'biome': biomeAct,
                'layer': 'soil',
                'sensor': 'Landsat',
                'source': 'geodatin'                
            }         
            classifiedGTB = classifiedGTB.set(mydict)
            # sys.exit()
            exportImage(classifiedGTB, nameExport, geoms)
            arqFeitos.write(nameExport + '\n')
        except:                    
            print('FAILS TO PROCESSING CLASS => ', )
            arqFeitos.write(nameExport + '\n')
    else:                
        
        print('FAILS BY SIZE ROIs 0 => ', )
        arqFeitos.write(nameExport + '\n')


      

dictPathRowVis = {}
dict_bandImps = {}
# Opening JSON file
with open('list_PathRow_Vizinhos.json') as json_file:
    dictPathRowVis = json.load(json_file)

lstParPathRowViz = []
for kk, vvals in dictPathRowVis.items():
    lstParPathRowViz.append(kk)
    if kk == '1_57':    # '220_64', '220_69'
        print(kk, " ", vvals)

# Opening JSON file
with open('dict_PathRowRegions_toBiome.json') as json_file:
    dict_biomeReg = json.load(json_file)

# Opening JSON file
with open('dict_bands_importance_regions.json') as json_file:
    dict_bandImps = json.load(json_file)

exportROIs = True
numfeat = 5
poolClassifyRows = True
lsAnos = [k for k in range(params['initYear'], params['endYear'])]
print(lsAnos)
gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
coletaSoil = True
# imgColmosaic = ee.ImageCollection(params['assets']['inputAsset'])
dictPath = {}
lstBnd = ['min','max','stdDev','amp','median','mean','class']
bandas_imports = [
    'amp', 'max', 'mean', 'median', 'min', 'min_contrast',
    'min_diss', 'min_savg', 'stdDev'
]
dictNameBiome = {
    'AMAZONIA': 'Amazônia', 
    'CERRADO': 'Cerrado',
    'CAATINGA': 'Caatinga',
    'MATA_ATLANTICA': 'Mata Atlântica', 
    'PAMPA': 'Pampa',
    'PANTANAL': 'Pantanal'
}
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
biome_act = 'CERRADO'
cont = 0
cont = gerenciador(cont, params)

regProcess = [12,13,14]
# ROIsManual = getPointsfromFolderManual(biome_act)
# sizeROIsM = ROIsManual.size().getInfo()
# print("size ROIS manual = ", sizeROIsM)
# print("rois aggregate ", ROIsManual.aggregate_histogram('class').getInfo())
# sys.exit()

# projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3
imgColmapsSoils = ee.ImageCollection(params['assets']['outputAsset']).filter(
                                ee.Filter.eq('version', params['version'])
)
lstIdsImgMap = imgColmapsSoils.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
lstIdssaved = []
listaIdsImgMap = []
if poolClassifyRows:
    for idsmap in tqdm(lstIdsImgMap):
        partes = idsmap.split('_')        
        indicador =  partes[1] + "_" + partes[-2] + "_" + partes[-1].replace('V' + params['version'], '')
        if partes[1] == 'MATA':
            indicador =  partes[1] + "_" + partes[2] + "_" + partes[-2] + "_" + partes[-1].replace('V3', '')
        print(" ====> ", idsmap, " <==> ", indicador)
        lstIdssaved.append(indicador)

    print(f"was saved {len(lstIdssaved)} images maps Soils")
    ccc = 0
    for val in lstIdssaved:
        if 'MATA_ATLANTICA' in val:
            ccc += 1
            print(ccc, " ==> ", val)
            
    print("total ", ccc)
else:
    lstIdsmapsSaved = [idsmap for idsmap in tqdm(lstIdsImgMap)]


# sys.exit()


arqFeitos = open("registros/orbitas_tiles_AnosV5.txt", 'w+')
lst_imgFails = [] 
for nreg, listaCenas in dict_biomeReg[biome_act].items():   #  
    print(f"Processing Bioma {biome_act} e Region {nreg}")
    if poolClassifyRows:
        lstRows = []
        for nCena in listaCenas:   #            
            # print('WRS_PATH  _ WRS_ROW # ' + str(nCena))            
            keyPathRow = biome_act + "_" + str(nCena) 
            if keyPathRow not in lstIdssaved:
                print(keyPathRow)
                keyPathRow += "_" + str(nreg) 
                # print("adding keyNames ", keyPathRow)
                lstRows.append(keyPathRow)
        # sys.exit()
        if len(lstRows) > 0:
            # create the pool with the default number of workers
            with ThreadPool() as pool:
                # issue one task for each call to the function
                print("enviando para processamento ", lstRows)
                for result in pool.map(export_classification_soilMap, lstRows):
                    # handle the result
                    print(f'>got {result}')            
        #     # report that all tasks are completed
        #     print('WRS_PATH # ' + str(wrsP) + ' Done')
        # else:
        #     print('WRS_PATH # ' + str(wrsP) + ' nothing to DOING')
        cont = gerenciador(cont, params)

    else:

        lstImgtoProc = []
        for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #
            cont = gerenciador(cont, params)
            print('WRS_ROW # ' + str(wrsR))
            print("listando images processing ")
            for yyear in lsAnos:
                # nameExport = 'classSoil_' + biomeAct + "_" + str(yyear) + '_' + nWrsP + '_' + nWrsR + 'V' + params['version'] 
                nameMapSoilIm = 'classSoil_' + biome_act + "_" + str(yyear) + '_' + wrsP + '_' + wrsR + 'V' + params['version']

                if nameMapSoilIm not in lstIdsmapsSaved:
                    # print(nameMapSoilIm)
                    lstImgtoProc.append(nameMapSoilIm)
        print("len ", len(lstImgtoProc))
        # print(lstImgtoProc)
        
        if len(lstImgtoProc) > 0:
            # create the pool with the default number of workers
            with ThreadPool() as pool:
                # issue one task for each call to the function
                for result in pool.map(export_classification_soilMap_by_Year, lstImgtoProc):
                    # handle the result
                    print(f'>got {result}')
            
            # report that all tasks are completed
            print('images to WRS_PATH # ' + str(wrsP) + ' go doing to process')
        else:
            print('All images to WRS_PATH # ' + str(wrsP) + ' was to DOING')