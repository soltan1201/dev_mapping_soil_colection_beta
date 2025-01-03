#-*- coding utf-8 -*-
import ee
import os
import gee #as gee
import sys
import json
import random
import math
import copy
from datetime import date

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
        'assets':{
            'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84
            # 'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',    
            'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-ndfia',
            'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas" ,
            'asset_raster_biomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41' 
        },
        'dependent': 'NDFIa',
        'harmonics': 2,  
        'dates':{
            '0': '-01-01',
            '1': '-12-31'
        },      
        'sensorIds': {        
            'L5': 'LANDSAT/LT05/C01/T1_SR',
            'L7': 'LANDSAT/LE07/C01/T1_SR',
            'L8': 'LANDSAT/LC08/C01/T1_SR',
            'L9': 'LANDSAT/LC09/C02/T1_L2'
        }, 
        'zeroT1_SR' : False,
        'sensorIdsToa': {        
            'L5': 'LANDSAT/LT05/C02/T1_TOA',
            'L7': 'LANDSAT/LE07/C02/T1_TOA',
            'L8': 'LANDSAT/LC08/C02/T1_TOA',
            'L9': 'LANDSAT/LC09/C02/T1_TOA'
        },
        'bnd' : {
            'L5': ['B1','B2','B3','B4','B5','B7','QA_PIXEL','QA_RADSAT'],
            'L7': ['B1','B2','B3','B4','B5','B7','QA_PIXEL','QA_RADSAT'],
            'L8': ['B2','B3','B4','B5','B6','B7','QA_PIXEL','QA_RADSAT'],
            'L9': ['B2','B3','B4','B5','B6','B7','QA_PIXEL','QA_RADSAT']
        }, 
        'indexProc': {
            'L5': 'LT05',
            'L7': 'LE07',
            'L8': 'LC08',
            'L9': 'LC09'
        },   
        'bnd_LG': ['blue','green','red','nir','swir1','swir2','pixel_qa'],
        'bnd_QA': ['blue','green','red','nir','swir1','swir2','QA_PIXEL', 'QA_RADSAT'],
        'bnd_L': ['blue','green','red','nir','swir1','swir2'],
        'CC': 70,   
        'WRS_PATH': None,
        'WRS_ROW' : None,
        'initYear': 1985,
        'endYear': 2023,
        'dependent': 'NDFIa',
        'harmonics': 2,
        'dateInit': '1987-01-01',
    }  
    harmonicFrequencies = []
    cosNames = []
    sinNames = []
    independents = []
    bandasRegresion = []
    newBandasIndependentes = []
    harmonicTrendCoefficients = None
    valMean = None
    janelaYear = None
    # coefficients = {
    #     'itcps': ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]),  #.multiply(10000)
    #     'slopes': ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949])
    # }
    # coefficientsL9 = {
    #     'itcps': ee.Image.constant([0.0000275, 0.0000275, 0.0000275, 0.0000275, 0.0000275, 0.0000275]),
    #     'slopes': ee.Image.constant([-0.2, -0.2, -0.2, -0.2, -0.2, -0.2])
    # }

    itcpsL9 = float(0.0000275)
    slopeL9 = float(-0.2)
    area_grade = 0

    def __init__(self, biomeActivo, wrsPath, wrsRow, lstYYearsFails):
        self.lstYYearsFails = lstYYearsFails
        self.options["WRS_PATH"] = wrsPath
        self.options["WRS_ROW"] = wrsRow
        self.biomeActivo = biomeActivo ## .buffer(buffer)
        # building list of dependents and independent variables
        # self.bluidingVariabel()        
        print(f"================ BIOMA ACTIVO {biomeActivo} ===========================")
        self.geomet = ee.FeatureCollection(self.options['assets']['gradeLandsat']).filter(
                                ee.Filter.eq('PATH', int(wrsPath))).filter(
                                    ee.Filter.eq('ROW', int(wrsRow))).geometry()
        self.area_grade = self.geomet.area().getInfo()
        print("area da grade ", self.area_grade)
        # sys.exit()
        # anoInicial = self.options['initYear']        
        self.serieLandsat = self.getAllImagePath_Row()
        print("band Names of the first images  ", self.serieLandsat.first().bandNames().getInfo())
        self.base_biomas = ee.Image(self.options['assets']['asset_raster_biomas']).gt(0)
        self.serieNDFIa = self.serieLandsat.map(lambda img: self.spectral_mixture_analysis(img))

        print("numero de imagens da serie ", self.serieNDFIa.size().getInfo())
        print("band Names of the first images NDFIa  ", self.serieNDFIa.first().bandNames().getInfo())
        print(" WRS_PATH :", self.serieNDFIa.first().get('WRS_PATH').getInfo())
        print(" WRS_ROW :", self.serieNDFIa.first().get('WRS_ROW').getInfo())
        # self.serieNDFIa = self.serieNDFIa.map(lambda img: )
        # print(self.serieNDFIa.first().getInfo())
        lstIDs = self.serieNDFIa.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
        self.dict_Ids = self.set_data_index_start(lstIDs)
        self.lstKeyYYmonth = list(self.dict_Ids.keys())
        # for nkey, lstVal in self.dict_Ids.items():
        #     print(f"  {nkey}: {lstVal}") 
        # sys.exit()

    def set_data_index_start(self, lstIDs):
        dict_Ids = {}
        for nId in lstIDs:
            date_str = nId.split('_')[-1]
            date_mes = date_str[:6]
            lstKey = list(dict_Ids.keys())
            # print("  >>>>   ", date_mes)
            if date_mes not in lstKey:
                # print(f"  >>>>   {date_mes} - {nId}")    
                dict_Ids[date_mes] = [nId]
            else:
                dict_Ids[date_mes].append(nId)            
        return dict_Ids

                
    def getAllImagePath_Row (self):

        lsAnos = [k for k in range(self.options['initYear'], self.options['endYear'] + 1)]
        serieNDFIa = None
        
        for cc, yyear in enumerate(lsAnos):
            imgCol = self.getCollectionCru(yyear)
            if cc == 0:                
                serieNDFIa = copy.deepcopy(imgCol)
            else:                
                serieNDFIa = serieNDFIa.merge(imgCol)

        # print("carregadas todas as imagens da serie ", serieNDFIa.size().getInfo()) 
        return serieNDFIa
    
    def cloudMaskL8(self, image):

        cfmask_conf = ee.Image(image.select('pixel_qa')).lte(324)
        image = image.updateMask(cfmask_conf)
        image = image.select(self.options['bnd_L'])
        # image = self.OliToEtmRMA(image)

        return image
    # https://code.earthengine.google.com/8f738cdf510e475ab685e3a85e366aec
    def cloudMask_QA_pixel(self, image):
        img = copy.deepcopy(image)
        qaMask = image.select('QA_PIXEL').eq(21824).rename("qaMask"); # 6 "1s" to account for snow
        saturationMask = image.select('QA_RADSAT').eq(0);
        image = image.updateMask(qaMask).updateMask(saturationMask).multiply(10000)
        # 'bnd_L': ['blue','green','red','nir','swir1','swir2'],
        image = image.select(self.options['bnd_L'])
        # image = self.applyScaleFactors(image)

        return image.copyProperties(img)
    # https://code.earthengine.google.com/3a3dc6a3e35411ec85eb62eaebecbb05
    def cloudMaskL57_QA_pixel(self, image):
        img = copy.deepcopy(image)
        qaMask = image.select('QA_PIXEL').eq(5440).rename("qaMask"); # 6 "1s" to account for snow
        saturationMask = image.select('QA_RADSAT').eq(0);
        image = image.updateMask(qaMask).updateMask(saturationMask).multiply(10000)
        # 'bnd_L': ['blue','green','red','nir','swir1','swir2'],
        image = image.select(self.options['bnd_L'])  
        return image.copyProperties(img)

    def cloudMaskL57(self, image):

        qa = ee.Image(image.select('pixel_qa')).lte(68)        
        image = image.updateMask(qa)
        image = self.clip_cena(image)
        return image.select(self.options['bnd_L'])
    
    # esta função pode ser revisada em 
    # https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization#references
    def etmToOli (self, img):

        newimg = img.select(self.options["bnd_L"]).multiply(self.coefficients['slopes'])\
                    .add(self.coefficients['itcps'])\
                    .round().toShort()
                    #.addBands(img.select('pixel_qa'))           
        newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']
        newimg = newimg.rename(newBND)

        img = img.addBands(newimg)
        newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n','pixel_qa']
        img = img.select(newBND) 
        # newimg = newimg.copyProperties(img)     
        newBND = ['blue','green','red','nir','swir1','swir2','pixel_qa']   
        return img.rename(newBND)

    def OliToEtmRMA (self, img):

        newimg = img.select(self.options["bnd_L"])\
                    .subtract(self.coefficients['itcps'])\
                    .divide(self.coefficients['slopes'])\
                    .round()\
                    .toShort()

        # 'bnd_L': ['blue','green','red','nir','swir1','swir2'],
        newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']
        newimg = newimg.rename(newBND)

        img = img.addBands(newimg)
        # newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']  #,'pixel_qa'
        img = img.select(newBND) 
        # newimg = newimg.copyProperties(img)     
        afterBND = ['blue','green','red','nir','swir1','swir2']   #,'pixel_qa'
        return img.rename(afterBND).copyProperties(img, ['system:time_start'])

    def applyScaleFactors (self, img):

        newimg = img.select(self.options["bnd_L"])\
                    .multiply(self.coefficientsL9['itcps'])\
                    .add(self.coefficientsL9['slopes'])\
                    .multiply(10000).round()\
                    .toShort()
        
        newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']
        newimg = newimg.rename(newBND)

        img = img.addBands(newimg)
        # newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']  #,'pixel_qa'
        img = img.select(newBND) 
        # newimg = newimg.copyProperties(img)     
        afterBND = ['blue','green','red','nir','swir1','swir2']   #,'pixel_qa'
        return img.rename(afterBND).copyProperties(img, ['system:time_start'])
                    
    def defineSensor(self, year):
        ss = 'L8'
        if year > 2012:
            ss = 'L8'
        elif year in [2000, 2001, 2002, 2012]:
            ss = "L7"        
        else :
            ss = 'L5'  
        
        print("SS " + ss)
        return ss

    def getCollectionCru(self, ano):

        ss = self.defineSensor(ano)

        date0 = str(ano) + self.options['dates']['0']
        date1 = str(ano) + self.options['dates']['1']
        # print(params['sensorIds'][ss])
        print(date0, date1)
        # print(params['bnd'][ss]) 
        # print(params['bnd_LG'])
        
        if ss == 'L8':        
            imgColLandsat = (ee.ImageCollection(self.options['sensorIdsToa'][ss])
                                .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))
                                .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))
                                .filterDate(date0, date1)
                                .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))
                                .select(self.options['bnd'][ss], self.options['bnd_QA'])
                        )
            # incluindo o processamento OliToEtmRMA 
            # imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL8(img))
            imgColLandsat = imgColLandsat.map(lambda img: self.cloudMask_QA_pixel(img))
        elif ss == 'L9':
            print(" processing L9 and L8 ")
            imgColLandsat = (ee.ImageCollection(self.options['sensorIdsToa']['L8']).merge(
                                ee.ImageCollection(self.options['sensorIdsToa'][ss]))
                                    .filter( ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))
                                    .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))
                                    .filterDate(date0, date1)
                                    .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))
                                    .select(self.options['bnd'][ss], self.options['bnd_QA'])
            )
            # if self.area_grade == 0:            
            #     geom = imgColLandsat.first().geometry()
            #     self.geomet = geom.buffer(-1000)
            # print("aqui ver bandas ", imgColLandsat.first().bandNames().getInfo())
            # print("aqui size() ", imgColLandsat.size().getInfo())
            # incluindo o processamento OliToEtmRMA 
            imgColLandsat = imgColLandsat.map(lambda img: self.cloudMask_QA_pixel(img))

        elif ss == 'L5':
            if self.options['zeroT1_SR'] == False:        
                print("==> L5 <== " + self.options['sensorIdsToa']['L5'])
                imgColLandsat = ( ee.ImageCollection(self.options['sensorIdsToa']['L5'])
                                    .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))
                                    .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))
                                    .filterDate(date0, date1)
                                    .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))
                                    .select(self.options['bnd']['L5'], self.options['bnd_QA'])  
                )
            else:
                print("==> L5 <== " + self.options['sensorIdsToa']['L5'])
                imgColLandsat = (ee.ImageCollection(self.options['sensorIdsToa']['L5'])
                                    .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))
                                    .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))
                                    .filterDate(date0, date1)
                                    .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))
                                    .select(self.options['bnd']['L5'], self.options['bnd_QA'])
                )

            # imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL57(img))  #cloudMaskL57_QA_pixel
            imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL57_QA_pixel(img))
        else:
            # ss = 'L7'
            print("== L7 == " + self.options['sensorIdsToa']['L7'])
            imgColLandsat = ee.ImageCollection(self.options['sensorIdsToa']['L7'])\
                                .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))\
                                .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))\
                                .filterDate(date0, date1)\
                                .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))\
                                .select(self.options['bnd']['L7'], self.options['bnd_QA'])
            # imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL57(img))
            imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL57_QA_pixel(img))
            
        return imgColLandsat

    def get_dates_inic_end(self, yyear, ymonth, parDatass):        
        if ymonth < 10:            
            if ymonth == 9:
                if parDatass:
                    return f"{yyear}-0{ymonth}-01", f"{yyear}-{ymonth + 1}-01"
                else:
                    return f"{yyear}0{ymonth}", " "
            if parDatass:
                return f"{yyear}-0{ymonth}-01", f"{yyear}-0{ymonth + 1}-01"
            else:
                return f"{yyear}0{ymonth}", " "
        elif ymonth == 12:
            if parDatass:
                return f"{yyear}-{ymonth}-01", f"{yyear + 1}-01-01"
            else:
                return f"{yyear}{ymonth}", " "
        else:
            if parDatass:
                return f"{yyear}-{ymonth}-01", f"{yyear}-{ymonth + 1}-01"
            else:
                return f"{yyear}{ymonth}", " "

    # https://code.earthengine.google.com/42a983e144022e527370463bf9346e18      
    def setImgindexNDFIAbyMonth(self):
        lsAnos = [k for k in range(self.options['initYear'], self.options['endYear'] + 1)]
        print(lsAnos)
        sizeImgYY = 0
        parDate = False
        nameSys = ""
        
        for cc, yyear in enumerate(lsAnos):
            lstBandas = []
            serieNDFIaYY = ee.Image().toUint16()
            for nmonth in range(1, 13): 
                sizeImgC = 0              
                print(f"YEAR = {yyear}  and month => {nmonth}")
                if parDate:
                    date0, date1 = self.get_dates_inic_end(yyear, nmonth, parDate)
                    print("Date 0 = {}  | date 1 = {}".format(date0, date1))
                    serieNDFIamonth = self.serieNDFIa.filterDate(date0, date1)
                    sizeImgC = serieNDFIamonth.size().getInfo()
                    date_month = str(yyear) + date0.split("-")[1] 
                    if sizeImgC >= 1:                        
                        nameSys = serieNDFIamonth.first().get('system:index').getInfo()
                else:
                    date_month, _ = self.get_dates_inic_end(yyear, nmonth, parDate)
                    if date_month in self.lstKeyYYmonth:
                        print(f"adding images from {date_month} >>>> {self.dict_Ids[date_month]}")
                        serieNDFIamonth = self.serieNDFIa.filter(ee.Filter.inList('system:index', self.dict_Ids[date_month]))      
                        sizeImgC = len(self.dict_Ids[date_month])
                        nameSys = self.dict_Ids[date_month][0]
                        
                    else:
                        sizeImgC = 0
                
                print('number of images in this months ', sizeImgC)
                # serieNDFIa.size().getInfo()
                # sys.exit()
                if sizeImgC >= 1:    
                    pos =  nameSys.find('L')               
                    serieNDFIamonth = serieNDFIamonth.mean().clip(self.geomet)
                    serieNDFIamonth = serieNDFIamonth.updateMask(self.base_biomas)
                    # report as bandas 
                    serieNDFIamonth = serieNDFIamonth.add(1).multiply(10000).toUint16().rename("bnd_" + date_month)
                    lstBandas.append("bnd_" + date_month)
                    if nmonth == 1:                            
                        serieNDFIaYY = copy.deepcopy(serieNDFIamonth)
                    else:
                        serieNDFIaYY = serieNDFIaYY.addBands(serieNDFIamonth)
                    sizeImgYY +=  sizeImgC
                
            # print("   \n ", newlstIds)
            # colfittedHarmonic = ee.List(colfittedHarmonic.toList(sizeImgYY))                    
            
            serieNDFIaYY = ee.Image.cat(serieNDFIaYY).select(lstBandas)#.rename(newlstIds) 
            print("lista de bandas NDFIaYY ", lstBandas)
            # print("name bands ", serieNDFIaYY.bandNames().getInfo())
            nameSaved = 'index_ndfia_' + self.biomeActivo + "_" + date_month + "_"
            nameSaved += self.options["WRS_PATH"] + '_' + self.options["WRS_ROW"]

            serieNDFIaYY = serieNDFIaYY.set('year', yyear)
            serieNDFIaYY = serieNDFIaYY.set('WRS_PATH', self.options["WRS_PATH"])
            serieNDFIaYY = serieNDFIaYY.set('WRS_ROW', self.options["WRS_ROW"])                    
            serieNDFIaYY = serieNDFIaYY.set('id', nameSaved)
            serieNDFIaYY = serieNDFIaYY.set('method', 'harmonic')
            serieNDFIaYY = serieNDFIaYY.set('noImgs_serie', sizeImgYY)
            serieNDFIaYY = serieNDFIaYY.set('source', 'geodatin')
            serieNDFIaYY = serieNDFIaYY.set('biome', self.biomeActivo)
            serieNDFIaYY = serieNDFIaYY.set('system:footprint', self.geomet)            
            self.exportImage(serieNDFIaYY, nameSaved)

            # sys.exit()
    
    def exportImage(self, imgYear, name):    
    
        idasset =  params['assets']['outputAsset'] + '/' + name
        optExp = {   
            'image': imgYear, 
            'description': name, 
            'assetId': idasset, 
            'region': self.geomet.getInfo()['coordinates'],  #getInfo(), #
            'scale': 30, 
            'maxPixels': 1e13,
            "pyramidingPolicy": {".default": "mode"}
        }

        task = ee.batch.Export.image.toAsset(**optExp)
        task.start() 
        print("salvando ... " + name + "..!")
    
    def spectral_mixture_analysis(self, img):
    
        # endmembers = [
        #     [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0], #/*gv*/
        #     [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0], #/*npv*/
        #     [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0], #/*soil*/
        #     [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0] #/*cloud*/
        # ]

        # outBandNames = ['gv', 'npv', 'soil', 'cloud']
        #    Blue, Green, Red, NIR, SWIR1, SWIR2
        endmembers = [            
            [ 500,  900,  400, 6100, 3000, 1000],  # 'gv': 
            [ 190,  100,   50,   70,   30,   20],  #'shade':
            [1400, 1700, 2200, 3000, 5500, 3000],  # 'npv': 
            [2000, 3000, 3400, 5800, 6000, 5800],   # 'soil':
            [9000, 9600, 8000, 7800, 7200, 6500]  # 'cloud': 
        ]

        outBandNames = ['gv','shade','npv','soil','cloud']

        fractions = ee.Image(img).unmix(endmembers, True, True)  #.select(self.options["bnd_L"])
        fractions = fractions.rename(outBandNames)

        # ndfi = ee.Image.cat(
        #         fractions.select('gv'), 
        #         fractions.select('npv').add(fractions.select('soil'))
        #     ).normalizeDifference()
        
        ndfia = fractions.expression(
            "float((b('gv')-b('soil'))/(b('gv') + b('npv') +b('soil')))")

        ndfia = ndfia.rename('NDFIa')        
        img = img.addBands(ndfia) # .addBands(fractions)
        
        return img.select('NDFIa')



params = {
    'assets':{
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas"   
    },
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
            '4' : ['59','60','61','62','63','64','65','66','67'],												
            '5' : ['65','66','67'], # 															
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
            '232' : ['56','57','58','59','60','61','62','63','64','65','66','67','68','69'],	# 
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
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '221' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
           '222' : ['64','65','66','67','68','69','70','71','72','73','74','75','76'],	 # 					
           '223' : ['64','65','66','67','68','69','70','71','72','73','74','75'],								
           '224' : ['65','67','68','69','70','71','72','73','74','75','76'],	# 									
           '225' : ['72','73','74','75','76','77'], #'69','70',	'71',													
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
            '219':['73','74','75','76','77'], 						
            '220':['74','75','76','77','78','79','80','81'],				# 
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
            '226' : ['71','72','73','74','75'], #
            '227' : ['71','72','73','74','75'], #
            '228' : ['71','72']             
        }
    }, # 
    'lsPath' : {
        'AMAZONIA' : ['1','2','3','4','5','6','220','221','222','223','224','225','226','227','228','229','230','231','232','233'],  # 
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': [,'224','225','226','227','228','229','230'], # '217','218','219','220','221','222','223'
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], # 
        'PAMPA':['220','221','222','223','224','225'],
        'PANTANAL':['225','226','227','228']  #    
    },  #
    'bnd' : {
        'L5': ['B1','B2','B3','B4','B5','B7','pixel_qa'],
        'L7': ['B1','B2','B3','B4','B5','B7','pixel_qa'],
        'L8': ['B2','B3','B4','B5','B6','B7','pixel_qa'],
        'L9': ['B2','B3','B4','B5','B6','B7','pixel_qa']
    }, 
    'indexProc': {
        'L5': 'LT05',
        'L7': 'LE07',
        'L8': 'LC08'
    },   
    'bnd_LG': ['blue','green','red','nir','swir1','swir2','pixel_qa'],
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'CC': 70,
    'initYear': 1985,
    'endYear': 2023,
    'dependent': 'NDFIa',
    'harmonics': 2,
    'dateInit': '1987-01-01',
    'numeroTask': 3,
    'numeroLimit': 60,
    'conta' : {
        '0': 'caatinga01',
        '5': 'caatinga02',
        '7': 'caatinga03',
        '9': 'caatinga04',
        '12': 'caatinga05',        
        '15': 'solkan1201',
        '20': 'superconta',      
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


try:
    arqFeitos = open("registros/orbTilesAnosNDFIa.txt", 'r')
    print("know type arquive ", type(arqFeitos))
except:
    arqFeitos = open("registros/orbTilesAnosNDFIa.txt", 'a+')

# gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
# The dependent variable we are modeling.
# The number of cycles per year to model.
# Make a list of harmonic frequencies to model.
# These also serve as band name suffixes.  //[1]
lstMosaicSaved = []
for line in arqFeitos:
    line = line.strip()
    print(" line ", line )
    lstMosaicSaved.append(line)

arqFeitos.close()

arqtoSaved = 0
cont = 0
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
biome_act = 'CERRADO'
dictYYFaits = {'CERRADO': []}
# Opening JSON file
# with open('list_imageMosaic_failTosave.json') as json_file:
#     dictitemFails = json.load(json_file)
#     for kkey, vvalue in dictitemFails.items():
#         print("list imagens fails in Bioma = ", kkey)
#         dict_tmp = {}
#         for vv in vvalue:
#             print("      ", vv)
#             partes = vv.split('_')
#             lstKkeys = [kk for kk in dict_tmp.keys()]
#             kkeyJ = partes[-2] + '_' + partes[-1]
#             # print("keyss ", kkeyJ)
#             if kkeyJ in lstKkeys:
#                 lsttmp = dict_tmp[kkeyJ]
#                 lsttmp.append(partes[-3])
#                 dict_tmp[kkeyJ] = lsttmp
#             else:
#                 dict_tmp[kkeyJ] = [partes[-3]]
        
#         dictYYFaits[kkey] = dict_tmp

# sys.exit()
apartirYear = 2019
dictAnosFalt = dictYYFaits[biome_act]
try:
    lstkeysPathRow = [kk for kk in dictAnosFalt.keys()]
except:
    lstkeysPathRow = []
arqFeitos = open("registros/orbTilesAnosNDFIa.txt", 'w+')

for wrsP in params['lsPath'][biome_act][:]:   #    
    print( 'WRS_PATH # ' + str(wrsP))
    for wrsR in params['lsGrade'][biome_act][wrsP][:]:   #    
        cont = gerenciador(cont, params)    
        print('WRS_ROW # ' + str(wrsR))
        keyPathRow =  wrsP + '_' + wrsR
        if keyPathRow not in lstMosaicSaved:
            # print("lista de anos que faltam ", dictAnosFalt[keyPathRow])        
            # print(geoms.getInfo())

            myclassMosaico = ClassMosaics(biome_act, wrsP, wrsR, []) # dictAnosFalt[keyPathRow]
            myclassMosaico.setImgindexNDFIAbyMonth()
            # sys.exit()
                # janFeita = False     
                # 
        arqFeitos.write(keyPathRow + '\n')   
        

arqFeitos.close()
