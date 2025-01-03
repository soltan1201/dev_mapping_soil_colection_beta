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
            'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',     
            'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas"   
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
    coefficients = {
        'itcps': ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]).multiply(10000),
        'slopes': ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949])
    }
    coefficientsL9 = {
        'itcps': ee.Image.constant([0.0000275, 0.0000275, 0.0000275, 0.0000275, 0.0000275, 0.0000275]),
        'slopes': ee.Image.constant([-0.2, -0.2, -0.2, -0.2, -0.2, -0.2])
    }

    itcpsL9 = float(0.0000275)
    slopeL9 = float(-0.2)
    area_grade = 0

    def __init__(self, biomeActivo, wrsPath, wrsRow, lstYYearsFails):
        self.lstYYearsFails = lstYYearsFails
        self.options["WRS_PATH"] = wrsPath
        self.options["WRS_ROW"] = wrsRow
        self.biomeActivo = biomeActivo ## .buffer(buffer)
        # building list of dependents and independent variables
        self.bluidingVariabel()        
        print(f"\n================ BIOMA ACTIVO {biomeActivo} ===========================")
        self.geomet = ee.FeatureCollection(self.options['assets']['gradeLandsat']).filter(
                                ee.Filter.eq('PATH', int(wrsPath))).filter(
                                    ee.Filter.eq('ROW', int(wrsRow))).geometry()
        self.area_grade = self.geomet.area().getInfo()
        print("area da grade ", self.area_grade)
        # sys.exit()
        # anoInicial = self.options['initYear']        
        self.serieLandsat = self.getAllImagePath_Row()
        print("band Names of the first images  ", self.serieLandsat.first().bandNames().getInfo())

        self.serieNDFIa = self.serieLandsat.map(lambda img: self.spectral_mixture_analysis(img))

        print("numero de imagens da serie ", self.serieNDFIa.size().getInfo())
        print("band Names of the first images NDFIa  ", self.serieNDFIa.first().bandNames().getInfo())
        # sys.exit()
        # add variavals constant, time (t), sine and cosine
        self.harmonicLandsat = self.serieNDFIa.map(lambda img: self.addHarmonics(img))
        # print(self.harmonicLandsat.first().getInfo())
                


    def bluidingVariabel(self):

        self.harmonicFrequencies = [i for i in range(1, self.options['harmonics'] + 1)]

        # Construct lists of names for the harmonic terms.
        self.cosNames = ['cos_' + str(i) for i in self.harmonicFrequencies]
        self.sinNames = ['sin_' + str(i) for i in self.harmonicFrequencies]
        print('cosNames', self.cosNames)
        print('sinNames', self.sinNames)

        # Independent variables.
        self.independents = ['constant', 't'] + self.cosNames + self.sinNames
        print("bandas independientes: ", self.independents)        

        # List of bands to regression
        self.bandasRegresion = [xx for xx in self.independents]
        self.bandasRegresion.append(self.options['dependent'])
        print("bandas da regressao : ", self.bandasRegresion)
        
        self.newBandasIndependentes = self.independents[2: len(self.independents)]
        print("new bandas da independientes : ", self.newBandasIndependentes)

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

    def clip_cena(self, img):     
        
        return img.clip(self.geomet)
    
    def cloudMaskL8(self, image):

        cfmask_conf = ee.Image(image.select('pixel_qa')).lte(324)
        image = image.updateMask(cfmask_conf)

        image = self.clip_cena(image)
        image = image.select(self.options['bnd_L'])
        image = self.OliToEtmRMA(image)

        return image
    # https://code.earthengine.google.com/8f738cdf510e475ab685e3a85e366aec
    def cloudMask_QA_pixel(self, image):
        img = copy.deepcopy(image)
        qaMask = image.select('QA_PIXEL').eq(21824).rename("qaMask"); # 6 "1s" to account for snow
        saturationMask = image.select('QA_RADSAT').eq(0);
        image = image.updateMask(qaMask).updateMask(saturationMask)
        
        image = self.clip_cena(image)
        # 'bnd_L': ['blue','green','red','nir','swir1','swir2'],
        image = image.select(self.options['bnd_L'])
        image = self.applyScaleFactors(image)

        return image.copyProperties(img)
    # https://code.earthengine.google.com/3a3dc6a3e35411ec85eb62eaebecbb05
    def cloudMaskL57_QA_pixel(self, image):
        img = copy.deepcopy(image)
        qaMask = image.select('QA_PIXEL').eq(21824).rename("qaMask"); # 6 "1s" to account for snow
        saturationMask = image.select('QA_RADSAT').eq(0);
        image = image.updateMask(qaMask).updateMask(saturationMask).multiply(10000)
        
        image = self.clip_cena(image)
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
            # if year in [2022]:
            #     ss = "L9"
            # else:
            ss = 'L8'
        elif year in [2000,2001,2002, 2012]:
            ss = "L7"        
        else :
            ss = 'L5'  
        
        print("SS " + ss)
        return ss

    def janelasAnos (self, lsAnos, printar):

        lsJanAnos = []

        for index, ano in enumerate(lsAnos):
            
            
            if ano - params['initYear'] < 2:
                janela = lsAnos[0 : 5]
            
            elif params['endYear'] - ano < 3:
                janela = lsAnos[len(lsAnos) - 5: len(lsAnos)]

            else:
                janela = lsAnos[index - 2: index + 3]
            
            if printar == True:
                print(' ==> ', janela)
            
            lsJanAnos.append(janela)
        
        return lsJanAnos

    def getCollectionCru(self, ano):

        ss = self.defineSensor(ano)

        date0 = str(ano) + self.options['dates']['0']
        date1 = str(ano) + self.options['dates']['1']
        # print(params['sensorIds'][ss])
        print(date0, date1)
        # print(params['bnd'][ss]) 
        # print(params['bnd_LG'])
        
        if ss == 'L8':        
            imgColLandsat = ee.ImageCollection(self.options['sensorIdsToa'][ss])\
                                .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))\
                                .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))\
                                .filterDate(date0, date1)\
                                .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))\
                                .select(self.options['bnd'][ss], self.options['bnd_QA'])
            # incluindo o processamento OliToEtmRMA 
            # imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL8(img))
            imgColLandsat = imgColLandsat.map(lambda img: self.cloudMask_QA_pixel(img))
        elif ss == 'L9':
            print(" processing L9 and L8 ")
            imgColLandsat = ee.ImageCollection(self.options['sensorIdsToa']['L8']).merge(
                                ee.ImageCollection(self.options['sensorIdsToa'][ss])).filter(
                                    ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))\
                                .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))\
                                .filterDate(date0, date1)\
                                .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))\
                                .select(self.options['bnd'][ss], self.options['bnd_QA'])
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
                imgColLandsat = ee.ImageCollection(self.options['sensorIdsToa']['L5'])\
                                    .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))\
                                    .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))\
                                    .filterDate(date0, date1)\
                                    .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))\
                                    .select(self.options['bnd']['L5'], self.options['bnd_QA'])  
            else:
                print("==> L5 <== " + self.options['sensorIdsToa']['L5'])
                imgColLandsat = ee.ImageCollection(self.options['sensorIdsToa']['L5'])\
                                    .filter(ee.Filter.eq('WRS_PATH', int(self.options["WRS_PATH"])))\
                                    .filter(ee.Filter.eq('WRS_ROW', int(self.options["WRS_ROW"])))\
                                    .filterDate(date0, date1)\
                                    .filter(ee.Filter.lt("CLOUD_COVER", self.options['CC']))\
                                    .select(self.options['bnd']['L5'], self.options['bnd_QA'])

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
            
            # if ano != 2012:
            #     # ss = 'L5'
            #     print("== L5 == " + params['sensorIds']['L5'])
            #     imgColLandsatL5 = ee.ImageCollection(params['sensorIds']['L5'])\
            #                         .filter(ee.Filter.eq('WRS_PATH', wrs_path))\
            #                         .filter(ee.Filter.eq('WRS_ROW', wrs_row))\
            #                         .filterDate(date0, date1)\
            #                         .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))\
            #                         .select(params['bnd']['L5'], params['bnd_LG'])
                
                
                # imgColLandsat = imgColLandsat.merge(imgColLandsatL5)           
        
        return imgColLandsat

   
    # def getVariavelHarmonicTrendCoeff(self, img):
    #     self.harmonicTrendCoefficients = img

    # def getvalMean(self, img):
    #     self.valMean = img

    
    def addHarmonics (self, image):

        # Make an image of frequencies.
        frequencies = ee.Image.constant(self.harmonicFrequencies)
        constant = ee.Image.constant(1)
        # Compute time in fractional years since the epoch.
        years = image.date().difference(self.options['dateInit'], 'day')
        timeRadians = ee.Image(years.multiply(2 * math.pi)).rename('t')
        
        # get year from images 
        yearIm = ee.Date(image.date()).get('year')
        # Get the cosine terms.
        cosines = timeRadians.multiply(frequencies).divide(365.25).cos().rename(self.cosNames)

        # Get the sin terms.
        sines = timeRadians.multiply(frequencies).divide(365.25).sin().rename(self.sinNames)

        return image.addBands(constant).addBands(timeRadians.float()
                        ).addBands(cosines).addBands(sines).set('year', ee.Number(yearIm).toInt8())
    
    def compute_fitted_values (self, image):
        # print("vermos as bandas  ", image.bandNames().getInfo())
        # print(" self.newBandasIndependentes = ", self.newBandasIndependentes)
        # ids = image.id()
        varfitted = image.select(self.newBandasIndependentes).multiply(
                        self.harmonicTrendCoefficients.select(self.newBandasIndependentes))\
                        .reduce(ee.Reducer.sum())\
                        .add(self.valMean).rename('fitted')
        # print("name ", varfitted.bandNames().getInfo())
        # erro = image.select('NDFIa').subtract(varfitted).rename('erro')

        return image.addBands(varfitted).select('fitted')# .addBands(erro)
                        
    def setImgfittedNDFIAonWindows5(self, year_min):

        lsAnos = [k for k in range(self.options['initYear'], self.options['endYear'] + 1)]
        print(lsAnos)
        # sys.exit()
        print("sabendo todas as janelas : ")
        lsWindowYear = self.janelasAnos(lsAnos, False)
        print(self.harmonicLandsat.size().getInfo())
        # print("|||||||||||||||",  lsAnos)
        
        for cc, yyear in enumerate(lsAnos):

            # if str(yyear) in self.lstYYearsFails:
            if int(yyear) > year_min:
                print("   AQUIIII    ")    

                # Get mean of time series
                janelaYear = lsWindowYear[cc]
                print(f"YEAR = {yyear}  and Windows => {janelaYear}")
                date0 = str(janelaYear[0]) + self.options['dates']['0']
                date1 = str(janelaYear[4]) + self.options['dates']['1']

                print(self.harmonicLandsat.size().getInfo())
                imgColLandsatJanela = self.harmonicLandsat.filterDate(date0, date1)
                print("Date 0 = {}   date 1 = {}".format(date0, date1))
                sizeImgC = imgColLandsatJanela.size().getInfo()
                print('number of images in this windows ', sizeImgC)

                # sys.exit()
                if sizeImgC > 1:
                    self.valMean = imgColLandsatJanela.select(self.options['dependent']).reduce('mean').rename('mean')

                    # print("reduzing means")
                    # print(" self.independents ==> ", self.independents)
                    # print("self.bandasRegresion ==> ",self.bandasRegresion)
                    # The output of the regression reduction is a 4x1 array image ou 6x1
                    harmonicTrend = imgColLandsatJanela.select(self.bandasRegresion)\
                                        .reduce(ee.Reducer.linearRegression(len(self.independents), 1))
                    
                    # Turn the array image into a multi-band image of coefficients.
                    self.harmonicTrendCoefficients = harmonicTrend.select('coefficients')\
                                                .arrayProject([0]).arrayFlatten([self.independents])
                                                
                    residuals = harmonicTrend.select('residuals')\
                                    .arrayProject([0]).arrayFlatten([self.independents])

                    
                    date0 = str(yyear) + self.options['dates']['0']
                    date1 = str(yyear) + self.options['dates']['1']
                    print("Date YY in 0 = {}   date YY in 1 = {}".format(date0, date1))
                    ndfiaColYY = imgColLandsatJanela.filterDate(date0, date1)
                    sizeImgYY = ndfiaColYY.size().getInfo()                  
                    print(f"year == > {yyear} => {sizeImgYY} imagens ")               
                    if sizeImgYY > 0:
                        # Compute fitted values.
                        colfittedHarmonic = ndfiaColYY.map(lambda img: self.compute_fitted_values(img))                        
                        # colfittedHarmonic = self.compute_fitted_values(ndfiaColYY.first())              
                        
                        lstIds = colfittedHarmonic.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
                        # corregir bandas 
                        tempFittedImage = None
                        ss = self.defineSensor(yyear)
                        # newlstIds = []
                        for index, nameSys in enumerate(lstIds):
                            pos = nameSys.find(self.options['indexProc'][ss])
                            print(f"{ss} nome inicial {pos} ==> {nameSys}")
                            if pos == -1:
                                pos = nameSys.find(self.options['indexProc']['L8'])
                                if pos == -1:
                                    pos = nameSys.find('LO09')
                            
                            
                            print(f"nome colocado na {pos} imagem  {nameSys[pos:]} ")
                            
                            # newlstIds.append(nameSys[pos:])
                            imgTemp = colfittedHarmonic.filter(ee.Filter.eq('system:index', nameSys)).first()
                            if index == 0:
                                tempFittedImage = ee.Image(imgTemp).add(1).multiply(10000).toUint16().rename(nameSys[pos:])
                            else:
                                tempFittedImage = tempFittedImage.addBands(imgTemp.add(1).multiply(10000).toUint16().rename(nameSys[pos:]))
                        
                        # print("   \n ", newlstIds)
                        # colfittedHarmonic = ee.List(colfittedHarmonic.toList(sizeImgYY))                    
                        
                        tempFittedImage = ee.Image.cat(tempFittedImage)#.rename(newlstIds) 
                        # print("name bands ", tempFittedImage.bandNames().getInfo())
                        nameSaved = 'fitted_image_' + self.biomeActivo + "_" + str(yyear) + '_' 
                        nameSaved += self.options["WRS_PATH"] + '_' + self.options["WRS_ROW"]

                        tempFittedImage = tempFittedImage.set('year', yyear)
                        tempFittedImage = tempFittedImage.set('WRS_PATH', self.options["WRS_PATH"])
                        tempFittedImage = tempFittedImage.set('WRS_ROW', self.options["WRS_ROW"])                    
                        tempFittedImage = tempFittedImage.set('id', nameSaved)
                        tempFittedImage = tempFittedImage.set('method', 'harmonic')
                        tempFittedImage = tempFittedImage.set('noImgs_serie', sizeImgYY)
                        tempFittedImage = tempFittedImage.set('source', 'geodatin')
                        tempFittedImage = tempFittedImage.set('biome', self.biomeActivo)
                        tempFittedImage = tempFittedImage.set('system:footprint', self.geomet)
                        
                        self.exportImage(tempFittedImage, nameSaved)

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


    def calculoSpectralIndex(self, image):

        ndvi = image.normalizedDifference(['nir', 'red']).rename('NDVI')

        ndwi = image.normalizedDifference(['nir', 'swir1']).rename('NDWI')

        savi = image.expression(
            "float((1 + 0.5) * float(b('nir') - b('red')) ) / (b('nir') + b('red') + 0.5)")
        savi = savi.rename('SAVI')

        pri = image.normalizedDifference(['blue', 'green']).rename('PRI')

        cai = image.expression("float(b('swir2') / b('swir1'))").rename('CAI')

        evi2 = image.expression(
            "float(2.5 * (b('nir') - b('red')) / (b('nir') + 2.4 * b('red') + 1))")
        evi2 = evi2.rename('EVI2')

        HallHeigth = image.expression(
            "float(-0.039 * b('red')  -0.011 * b('nir') -0.026 * b('swir1') + 4.13)").exp()
        HallHeigth = HallHeigth.rename('HALL_HEIGHT')

        HallCover = image.expression(
            "float(-0.017 * b('red')  -0.007 * b('nir') -0.079 * b('swir2') + 5.22)").exp()
        HallCover = HallHeigth.rename('HALL_COVER')

        gcvi = image.expression(
            "float( b('nir')  -0.007 * b('nir') -0.079 * b('swir2') + 5.22)").exp()
        gcvi = gcvi.rename('GCVI')

        return image.addBands(ndvi)\
                    .addBands(ndwi)\
                    .addBands(savi)\
                    .addBands(pri)\
                    .addBands(cai)\
                    .addBands(evi2)\
                    .addBands(HallHeigth)\
                    .addBands(HallCover)\
                    .addBands(gcvi)


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
            '229' : ['68','69','70','71'], # '58','59','60','61','62','63','64','65','66','67',
            '230' : ['59','60','61','62','63','64','65','66','67','68','69'],								
            '231' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],			
            '232' : ['57','58','59','60','61','62','63','64','65','66','67','68','69'],	# '56',	
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
            '219':['73','74','75','76','77'], 						
            '220':['75','76','77','78','79','80','81'],				# '74',
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
        'AMAZONIA' : ['229','230','231','232','233'],  # '1','2','3','4','5','6','220','221','222','223','224','225','226','227','228',
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'], # 
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
        '10': 'caatinga03',
        '15': 'caatinga04',
        '20': 'caatinga05',        
        '25': 'solkan1201',
        '30': 'superconta',      
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



# arqFeitos = open("registros/orbtilesAnos.txt", 'r')

# tilesAnosFeitos = [] 
arqFeitos = open("registros/orbtilesAnosNew.txt", 'w+')

# gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
# The dependent variable we are modeling.
# The number of cycles per year to model.
# Make a list of harmonic frequencies to model.
# These also serve as band name suffixes.  //[1]

arqtoSaved = 0
cont = 0
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
biome_act = 'CAATINGA'
dictYYFaits = {}
# Opening JSON file
with open('list_imageMosaic_failTosave.json') as json_file:
    dictitemFails = json.load(json_file)
    for kkey, vvalue in dictitemFails.items():
        print("list imagens fails in Bioma = ", kkey)
        dict_tmp = {}
        for vv in vvalue:
            print("      ", vv)
            partes = vv.split('_')
            lstKkeys = [kk for kk in dict_tmp.keys()]
            kkeyJ = partes[-2] + '_' + partes[-1]
            # print("keyss ", kkeyJ)
            if kkeyJ in lstKkeys:
                lsttmp = dict_tmp[kkeyJ]
                lsttmp.append(partes[-3])
                dict_tmp[kkeyJ] = lsttmp
            else:
                dict_tmp[kkeyJ] = [partes[-3]]
        
        dictYYFaits[kkey] = dict_tmp

# sys.exit()
apartirYear = 2019
dictAnosFalt = dictYYFaits[biome_act]
lstkeysPathRow = [kk for kk in dictAnosFalt.keys()]
for wrsP in params['lsPath'][biome_act][:]:   #    
    print( 'WRS_PATH # ' + str(wrsP))
    for wrsR in params['lsGrade'][biome_act][wrsP]:   #    
        cont = gerenciador(cont, params)    
        print('WRS_ROW # ' + str(wrsR))
        keyPathRow =  wrsP + '_' + wrsR
        # if keyPathRow in lstkeysPathRow:
        # print("lista de anos que faltam ", dictAnosFalt[keyPathRow])        
        # print(geoms.getInfo())

        myclassMosaico = ClassMosaics(biome_act, wrsP, wrsR, []) # dictAnosFalt[keyPathRow]
        myclassMosaico.setImgfittedNDFIAonWindows5(apartirYear)
        # sys.exit()
            # janFeita = False     
            # 
        arqFeitos.write(keyPathRow + '\n')   
        

arqFeitos.close()
