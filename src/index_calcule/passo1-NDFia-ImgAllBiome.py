#-*- coding utf-8 -*-
import ee
import gee #as gee
import sys
import json
import random
import math
from datetime import date

# import arqParametros as aparam
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

class ClassMosaics(object):

    # default options

    options = { 
        'bnd_LG': ['blue','green','red','nir','swir1','temp','swir2','pixel_qa'],
        'bnd_L': ['blue','green','red','nir','swir1','swir2'], 
        'dependent': 'NDFIa',
        'harmonics': 2         
    }  
    harmonicFrequencies = []
    cosNames = []
    sinNames = []
    independents = []
    bandasRegresion = []
    newBandasIndependentes = []
    harmonicTrendCoefficients = None
    valMean = None

    coefficients = {
        'itcps': ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]).multiply(10000),
        'slopes': ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949])
    }

    def __init__(self, geom, paramet):

        self.options["bnd_LG"] = paramet["bnd_LG"]
        self.options["bnd_L"] = paramet["bnd_L"]
        self.options['harmonics'] = paramet['harmonics']
        self.geomet = geom ## .buffer(buffer)

        self.bluidingVariabel()
    

    def clip_cena(self, img):

        return img.clip(self.geomet)
    
    
    def cloudMaskL8(self, image):

        cfmask_conf = ee.Image(image.select('pixel_qa')).lte(324)
        image = image.updateMask(cfmask_conf)

        image = self.clip_cena(image)

        return image.select(self.options['bnd_L'])
    
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
        
        newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']
        newimg = newimg.rename(newBND)

        img = img.addBands(newimg)
        newBND = ['bluen','greenn','redn','nirn','swir1n','swir2n']  #,'pixel_qa'
        img = img.select(newBND) 
        # newimg = newimg.copyProperties(img)     
        newBND = ['blue','green','red','nir','swir1','swir2']   #,'pixel_qa'
        return img.rename(newBND).copyProperties(img, ['system:time_start'])
                    
    
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

    
    def getVariavelHarmonicTrendCoeff(self, img):

        self.harmonicTrendCoefficients = img

    def getvalMean(self, img):

        self.valMean = img
    
    # Function to add a time band.
    def addDependents (self, image):

        # Compute time in fractional years since the epoch.
        years = image.date().difference(params['dateInit'], 'day')
        timeRadians = ee.Image(years.multiply(2 * math.pi)).rename('t')

        constant = ee.Image(1)

        return image.addBands(constant).addBands(timeRadians.float())

    
    def addHarmonics (self, image):

        # Make an image of frequencies.
        frequencies = ee.Image.constant(self.harmonicFrequencies)

        # This band should represent time in radians.
        time = ee.Image(image).select('t')

        # Get the cosine terms.
        cosines = time.multiply(frequencies).divide(365.25).cos().rename(self.cosNames)

        # Get the sin terms.
        sines = time.multiply(frequencies).divide(365.25).sin().rename(self.sinNames)

        return image.addBands(cosines).addBands(sines)

    
    def compute_fitted_values (self, image):

        varfitted = image.select(self.newBandasIndependentes).multiply(
                        self.harmonicTrendCoefficients.select(self.newBandasIndependentes))\
                        .reduce(ee.Reducer.sum())\
                        .add(self.valMean).rename('fitted')
        
        erro = image.select('NDFIa').subtract(varfitted).rename('erro')

        return image.addBands(varfitted).addBands(erro)
                        

    
    def spectral_mixture_analysis(self, img):
    
        # endmembers = [
        #     [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0], #/*gv*/
        #     [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0], #/*npv*/
        #     [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0], #/*soil*/
        #     [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0] #/*cloud*/
        # ]

        # outBandNames = ['gv', 'npv', 'soil', 'cloud']
        endmembers = [            
            [ 500,  900,  400, 6100, 3000, 1000],  # 'gv': 
            [ 190,  100,   50,   70,   30,   20],  #'shade':
            [1400, 1700, 2200, 3000, 5500, 3000],  # 'npv': 
            [2000, 3000, 3400, 5800, 6000, 5800],   # 'soil':
            [9000, 9600, 8000, 7800, 7200, 6500]  # 'cloud': 
        ]

        outBandNames = ['gv','shade','npv','soil','cloud']

        fractions = ee.Image(img).select(self.options["bnd_L"]).unmix(endmembers, True, True)
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
           '220' : ['62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77'],
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
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'],
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], # 
        'PAMPA':['220','221','222','223','224','225'],
        'PANTANAL':['225','226','227','228']
    },  #
    'bnd' : {
        'L5': ['B1','B2','B3','B4','B5','B7','pixel_qa'],
        'L7': ['B1','B2','B3','B4','B5','B7','pixel_qa'],
        'L8': ['B2','B3','B4','B5','B6','B7','pixel_qa']
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
    'numeroLimit': 35,
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


def getCollectionCru(ano, wrs_path, wrs_row, ss):

    date0 = str(ano) + params['dates']['0']
    date1 = str(ano) + params['dates']['1']
    # print(params['sensorIds'][ss])
    print(date0, date1)
    # print(params['bnd'][ss])
    # print(params['bnd_LG'])
    
    if ss == 'L8':        
        imgColLandsat = ee.ImageCollection(params['sensorIds'][ss])\
                            .filter(ee.Filter.eq('WRS_PATH', wrs_path))\
                            .filter(ee.Filter.eq('WRS_ROW', wrs_row))\
                            .filterDate(date0, date1)\
                            .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))\
                            .select(params['bnd'][ss], params['bnd_LG'])
    elif ss == 'L5':
        if params['zeroT1_SR'] == False:        
            print("==> L5 <== " + params['sensorIds']['L5'])
            imgColLandsat = ee.ImageCollection(params['sensorIds']['L5'])\
                                .filter(ee.Filter.eq('WRS_PATH', wrs_path))\
                                .filter(ee.Filter.eq('WRS_ROW', wrs_row))\
                                .filterDate(date0, date1)\
                                .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))\
                                .select(params['bnd']['L5'], params['bnd_LG'])  
        else:
            print("==> L5 <== " + params['sensorIdsToa']['L5'])
            imgColLandsat = ee.ImageCollection(params['sensorIdsToa']['L5'])\
                                .filter(ee.Filter.eq('WRS_PATH', wrs_path))\
                                .filter(ee.Filter.eq('WRS_ROW', wrs_row))\
                                .filterDate(date0, date1)\
                                .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))\
                                .select(params['bnd']['L5'], params['bnd_LG'])
    else:
        # ss = 'L7'
        print("== L7 == " + params['sensorIds']['L7'])
        imgColLandsat = ee.ImageCollection(params['sensorIds']['L7'])\
                            .filter(ee.Filter.eq('WRS_PATH', wrs_path))\
                            .filter(ee.Filter.eq('WRS_ROW', wrs_row))\
                            .filterDate(date0, date1)\
                            .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))\
                            .select(params['bnd']['L7'], params['bnd_LG'])
        
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
    
    # aplicando uma mascara simples 
    # if ss == 'L8':
    #     imgColLandsat = imgColLandsat.map(lambda img: cloudMaskL8sr(img))
    # else:
    #     imgColLandsat = imgColLandsat.map(lambda img: cloudMaskL457(img))
    
    return imgColLandsat


def defineSensor(year):

    ss = 'L8'

    if year > 2012:
        ss = 'L8'   

    elif year in [2000,2001,2002, 2012]:
        ss = "L7"

    else :
        ss = 'L5'  
    
    print("SS " + ss)

    return ss


def janelasAnos (lsAnos, printar):

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

arqFeitos = open("registros/orbtilesAnos.txt", 'r')

# tilesAnosFeitos = [] 
arqFeitos = open("registros/orbtilesAnos.txt", 'a+')

gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
# The dependent variable we are modeling.
# The number of cycles per year to model.
# Make a list of harmonic frequencies to model.
# These also serve as band name suffixes.  //[1]

anoInicial = params['initYear']
lsAnos = [k for k in range(params['initYear'], params['endYear'])]
print(lsAnos)

print("sabendo todas as janelas : ")
lsWindowYear = janelasAnos(lsAnos, False)
print(lsWindowYear)
sys.exit()
imgColLandsatJanela = None
arqtoSaved = 0
cont = 0
# 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'
biome_act = 'AMAZONIA'

# Opening JSON file
with open('list_imageMosaic_failTosave.json') as json_file:
    dictitemFails = json.load(json_file)
    for kkey, vvalue in dictitemFails.items():
        print("list imagens fails in Bioma = ", kkey)
        for vv in vvalue:
            print("      ", vv)

tilesAnosFeitos = dictitemFails[biome_act]
for wrsP in params['lsPath'][biome_act][:]:   #
    cont = gerenciador(cont, params)
    print( 'WRS_PATH # ' + str(wrsP))
    for wrsR in params['lsGrade'][biome_act][wrsP]:   #
        
        print('WRS_ROW # ' + str(wrsR))
        fPathRow = 'T' + wrsP + '0' + wrsR
        
        geoms = gradeLandsat.filter(ee.Filter.eq('PATH', int(wrsP))).filter(
                                    ee.Filter.eq('ROW', int(wrsP))).geometry()
        # print(geoms.getInfo())

        myclassMosaico = ClassMosaics(geoms, params)
        janFeita = False        
        for index, ano in enumerate(lsAnos):
            
            print("==== ano {} : {} ====".format(index, ano))
            myreg = biome_act + '_' + wrsP + '_' + wrsR + '_' + str(ano)
            nameSaved = 'fitted_image_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR

            if nameSaved in tilesAnosFeitos:  # or ano > 2017
                ss = 'L8'
                if index < 3 or janFeita == False:
                
                    for oAno in lsWindowYear[index]:                                    
                        ss = defineSensor(oAno)
                        colSize = 0
                        ####################################################################
                        ############ construção imagecolections carregadas    ##############
                        ####################################################################
                        colecaoLandsat =  getCollectionCru(oAno, int(wrsP), int(wrsR), ss)
                        try:
                            colSize = colecaoLandsat.size().getInfo()
                        except:
                            colSize = 0
                        
                        print("||==> ano : {}  size of imgCol = {} ||".format(oAno, colSize))
                        if colSize > 0:

                            colecaoLandsat = colecaoLandsat.map(lambda img: img.set('year', oAno))                            
                            if ss == 'L8':
                                colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.cloudMaskL8(img))
                                colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.OliToEtmRMA(img))
                            # else:
                                # correção da imagens de L5 e L7 para OLI 
                                # print("corrigindo ETM por OLI")
                                
                                # colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.etmToOli(img))                                
                                # colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.OliToEtmRMA(img)) 
                            else:
                                # correção da imagens de L5 e L7 para OLI 
                                # print("corrigindo ETM por OLI")                                
                                                               
                                colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.cloudMaskL57(img))
                                # lsNames = colecaoLandsat.reduceColumns(ee.Reducer.toList(2), ['system:index', 'system:time_start']).get('list').getInfo()
                                # print("is de nomes e image \n", lsNames)
                                
                            
                            colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.spectral_mixture_analysis(img))
                            #colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.calculoSpectralIndex(img))
                    
                            harmonicLandsat = colecaoLandsat.map(lambda img: myclassMosaico.addDependents(img))
                            harmonicLandsat = harmonicLandsat.map(lambda img: myclassMosaico.addHarmonics(img))
                            # print(harmonicLandsat.first().bandNames().getInfo())
                            
                            if oAno ==  anoInicial or janFeita == False:
                                imgColLandsatJanela = harmonicLandsat
                            
                            else:
                                imgColLandsatJanela = imgColLandsatJanela.merge(harmonicLandsat)
                            
                            janFeita = True
                            print(" == {} imagens na Col 🚀".format(imgColLandsatJanela.size().getInfo()))
                
                elif (len(lsAnos) - index) > 2:

                    oAno = lsWindowYear[index][-1]
                    ss = defineSensor(oAno)                    

                    colecaoLandsat = getCollectionCru(oAno, int(wrsP), int(wrsR), ss)
                    try:
                        colSize = colecaoLandsat.size().getInfo()
                    except:
                        colSize = 0
                    
                    print("||==> YEAR : {}  SIZE of ImgCol = {} ||".format(oAno, colSize))
                    
                    if colSize > 0:                        
                        colecaoLandsat = colecaoLandsat.map(lambda img: img.set('year', oAno))
                        # print("COMPROVANDO AS BANDAS ", colecaoLandsat.first().bandNames().getInfo())
                        if ss == 'L8':
                            colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.cloudMaskL8(img))
                            colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.OliToEtmRMA(img))
                            
                        else:
                            # colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.etmToOli(img))
                            colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.cloudMaskL57(img))
                            
                        colecaoLandsat = colecaoLandsat.map(lambda img: myclassMosaico.spectral_mixture_analysis(img))

                        harmonicLandsat = colecaoLandsat.map(lambda img: myclassMosaico.addDependents(img))
                        harmonicLandsat = harmonicLandsat.map(lambda img: myclassMosaico.addHarmonics(img))
                        # print(harmonicLandsat.first().bandNames().getInfo())
                        
                        print(" ========= year {} ===============".format(ano))
                        print(lsWindowYear[index])
                        # print(" == {} imagens na Col ".format(colecaoLandsat.size().getInfo()))

                        imgColLandsatJanela = imgColLandsatJanela.filter(ee.Filter.inList('year', lsWindowYear[index]))
                        # print(" == {} imagens na ColGeral filtrada".format(imgColLandsatJanela.size().getInfo()))
                        imgColLandsatJanela = imgColLandsatJanela.merge(harmonicLandsat)

                colecaoLandsat = None
                sizeCol = imgColLandsatJanela.size().getInfo()
                print(" == {} imagens na ColGeral 🚀".format(sizeCol))

                ss = defineSensor(ano)
                sizeColAtual = 0  

                sys.exit()


                ####################################################################
                ############ construção de bandas necesarias na serie 🚀 ###########
                ####################################################################
                # Get mean of time series
                valMean = imgColLandsatJanela.select('NDFIa').reduce('mean').rename('mean')

                print("bandas independientes ", myclassMosaico.independents)
                print("all bandas da regresao ", myclassMosaico.bandasRegresion)
                # The output of the regression reduction is a 4x1 array image ou 6x1
                harmonicTrend = imgColLandsatJanela.select(myclassMosaico.bandasRegresion)\
                                    .reduce(ee.Reducer.linearRegression(len(myclassMosaico.independents), 1))
                try: 
                    print("bandas da harmonic Trend", harmonicTrend.bandNames().getInfo() )
                    # Turn the array image into a multi-band image of coefficients.
                    harmonicTrendCoefficients = harmonicTrend.select('coefficients')\
                                                .arrayProject([0]).arrayFlatten([myclassMosaico.independents])
                                            
                    residuals = harmonicTrend.select('residuals')\
                                    .arrayProject([0]).arrayFlatten([myclassMosaico.independents])
                    
                    
                    # transmitir os dados para a classe Mosaico
                    myclassMosaico.getVariavelHarmonicTrendCoeff(harmonicTrendCoefficients)
                    myclassMosaico.getvalMean(valMean)

                    
                    # Compute fitted values.
                    fittedHarmonic = imgColLandsatJanela.map(lambda img: myclassMosaico.compute_fitted_values(img))
                    
                    # To get annul ImageCollection
                    tempFitted = fittedHarmonic.select(['fitted'])
                    date0 = str(ano) + params['dates']['0']
                    date1 = str(ano) + params['dates']['1']
                    tempFitted = tempFitted.filterDate(date0, date1)  
                    #                   
                    sizeColAtual = tempFitted.size().getInfo()             
                except:
                    sizeColAtual = 0

                print(" == {} imagens na ColGeral Reducida 🚀".format(sizeColAtual))
                try:                    
                    if sizeColAtual > 0:

                        lsidsNames = tempFitted.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
                        tempFittedImage = None

                        for index, idname in enumerate(lsidsNames):                            
                            
                            imgTemp = tempFitted.filter(ee.Filter.eq('system:index', idname)).first()
                            if ss != 'LX':
                                loca = idname.find(params['indexProc'][ss])
                            else:
                                loca = idname.find(params['indexProc']['L5'])
                                if loca < 0:
                                    loca = idname.find(params['indexProc']['L7'])

                            idnameNew = idname[loca:]
                            # print(" o system index ", idnameNew)

                            if index == 0:
                                tempFittedImage = ee.Image(imgTemp).add(1).multiply(10000).toUint16().rename(idnameNew)
                            else:
                                tempFittedImage = tempFittedImage.addBands(imgTemp.add(1).multiply(10000).toUint16().rename(idnameNew))
                        
                        
                        # print("lista de bandas finais ", tempFittedImage.bandNames().getInfo())

                        name = 'fitted_image_' + biome_act + "_" + str(ano) + '_' + wrsP + '_' + wrsR

                        tempFittedImage = tempFittedImage.set('year', ano)
                        tempFittedImage = tempFittedImage.set('WRS_PATH', wrsP)
                        tempFittedImage = tempFittedImage.set('WRS_ROW', wrsR)                    
                        tempFittedImage = tempFittedImage.set('id', name)
                        tempFittedImage = tempFittedImage.set('method', 'harmonic')
                        tempFittedImage = tempFittedImage.set('noImgs_serie', sizeCol)
                        tempFittedImage = tempFittedImage.set('source', 'geodatin')
                        tempFittedImage = tempFittedImage.set('biome', biome_act)

                        
                        exportImage(tempFittedImage, name, geoms)
                except :
                    print("##################### NAO SALVOU ESSA CENA ##########################")
                arqFeitos.write(myreg + '\n')
            
            else:
                
                if janFeita == False:
                    anoInicial = ano
                    print("======  YEAR THAT BEGIN NOW IS : {}  ======= by rejection".format(anoInicial))

arqFeitos.close()
