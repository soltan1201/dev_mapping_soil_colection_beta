#-*- coding utf-8 -*-
import ee
#import gee #as gee
import sys
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


class  principalComponentAnalysis(object):

    # default options

    options = { 
        'bandNames': [],
        'dependent': 'NDFIa',         
        'scale': 30            
    }  

    geom = None

    def __init__(self, scale):

        self.options['scale'] = scale          


    def getNewBandNames(self, prefix):        

        # this we get the list of new band names.
        seq = [ prefix + str(b)   for b in range(1, len(self.options['bandNames']) + 1)]
        
        return seq
    
    def mean_centered_data(self, image, geomet):

        
        self.options['bandNames'] = image.bandNames().getInfo()
        print("nomes de bandas ", self.options['bandNames'])

        pmsReducer = {
            'reducer': ee.Reducer.mean(),
            'geometry': geomet,
            'scale': self.options['scale'],
            'maxPixels': 1e13
        }  

        processo = False

        if len(self.options['bandNames']) > 1:

            # Mean center the data to enable a faster covariance reducer
            # and an SD stretch of the principal components.
            meanDict = image.reduceRegion(**pmsReducer)
            valores = []
            
            print(meanDict.getInfo())
            
            for ky, vv in meanDict.getInfo().items():
                print("banda: {}  == valor: {}".format(ky, vv))
                valores.append(vv)
            
            means = ee.Image.constant(valores)

            centered = image.subtract(means)
            # print("restou ")
            processo = True

            return centered, processo
        
        return image, processo

    #########################################################################
    ###    This function accepts mean centered imagery, a scale and      ####      
    ###     a region in which to perform the analysis.  It returns the   ####
    ###     Principal Components (PC) in the region as a new image.      ####
    #########################################################################

    def get_principalComponentAnalysis(self, img, geom):

        # self.geom = geom        

        centered, processou = self.mean_centered_data(img, geom)

        if processou:
        
            # Collapse the bands of the image into a 1D array per pixel.
            arrays = centered.toArray()
            print("converteu em arrays ")
            # Compute the covariance of the bands within the region.           
            
            pmsReducer = {
                'reducer': ee.Reducer.centeredCovariance(),
                'geometry': geom,
                'scale': self.options['scale'],
                'maxPixels': 1e13
            }               
            
            covar = arrays.reduceRegion(**pmsReducer)

            # Get the 'array' covariance result and cast to an array.
            # This represents the band-to-band covariance within the region.
            covarArray = ee.Array(covar.get('array'))

            # Perform an eigen analysis and slice apart the values and vectors.
            eigens = covarArray.eigen()

            # This is a P-length vector of Eigenvalues.
            eigenValues = eigens.slice(1, 0, 1)

            # This is a PxP matrix with eigenvectors in rows.
            eigenVectors = eigens.slice(1, 1)

            # Convert the array image to 2D arrays for matrix computations.
            arrayImage = arrays.toArray(1)

            # Left multiply the image array by the matrix of eigenvectors.
            principalComponents = ee.Image(eigenVectors).matrixMultiply(arrayImage)

            # Turn the square roots of the Eigenvalues into a P-band image.
            sdImage = ee.Image(eigenValues.sqrt())\
                        .arrayProject([0]).arrayFlatten([self.getNewBandNames('sd')])

            # Turn the PCs into a P-band image, normalized by SD.
            # Throw out an an unneeded dimension, [[]] -> [].
            # Make the one band array image a multi-band image, [] -> image.
            # Normalize the PCs by their SDs.
            principalComponents = principalComponents.arrayProject([0]).arrayFlatten(
                [self.getNewBandNames('pc')]).divide(sdImage)
            
            return principalComponents
        
        return img



params = {
    'assets':{
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  # SPRNOME: 247/84
        'outputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/mosaics-normalized',     
        'inputAssets': 'projects/nexgenmap/MapBiomas2/LANDSAT/mosaics-normalized',
        'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas"   
    },
    'dateInit': '2002-01-01',
    'scale': 30,
    'numeroTask': 6,
    'numeroLimit': 45,
    'conta' : {
        '0': 'diegoUEFS'        
    },
}

#def gerenciador(cont, paramet):    
    
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
#    numberofChange = [kk for kk in paramet['conta'].keys()]
    
#    if str(cont) in numberofChange:

#        print("conta ativa >> {} <<".format(paramet['conta'][str(cont)]))        
#        gee.switch_user(paramet['conta'][str(cont)])
#        gee.init()        
#        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    # elif cont > paramet['numeroLimit']:
    #     cont = 0
    
    # cont += 1    
    # return cont


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

year_ = 2020
#####       Building collections    #############
gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
colHarmonic = ee.ImageCollection(params['assets']['inputAssets']).filter(
                                        ee.Filter.eq('method', 'harmonic')).filter(
                                        ee.Filter.eq('year', year_))
nameCol = colHarmonic.reduceColumns(ee.Reducer.toList(), ['id']).get('list').getInfo()
principalComponentAnalysisClass = principalComponentAnalysis(params['scale'])

arqFeitos = open("registros/pca_orbtilesAnos.txt", 'r')
imgAnosFeitos = [] 
for ii in arqFeitos.readlines():    
    ii = ii[:-1]    
    imgAnosFeitos.append(ii)

arqFeitos = open("registros/pca_orbtilesAnos.txt", 'a+')




#gerenciador(0, params)
for idname in nameCol:

    print("==== procesando imagem << {} >>".format(idname))
    
    # fitted_image_2017_217_67
    lsdados = idname.split('_')
    year = lsdados[2]
    _path = lsdados[3]
    _row = lsdados[4]
    
    fPathRow = 'T' + _path + '0' + _row

    if idname not in imgAnosFeitos:
        
        geoms = gradeLandsat.filter(ee.Filter.eq('TILE_T', fPathRow)).geometry()

        imgHarmonic = ee.Image(colHarmonic.filter(ee.Filter.eq('id', idname)).first())
        sizeCol = imgHarmonic.get('noImgs_serie').getInfo()

        imgPCA = principalComponentAnalysisClass.get_principalComponentAnalysis(imgHarmonic, geoms)
        imgPCA = imgPCA.add(10).max(0).multiply(1000)
    
        lsBND = [bnd for bnd in imgPCA.bandNames().getInfo()]
    
        if len(lsBND) > 5:
            print(" lista de bandas de PCA ", lsBND)
            imgPCA = imgPCA.select(lsBND[:5])
        
            name = 'pca_' + year + '_' + _path + '_' + _row
            imgPCA = ee.Image(imgPCA).set('year', int(year))    

            imgPCA = imgPCA.set('WRS_PATH', _path)
            imgPCA = imgPCA.set('WRS_ROW', _row)
            imgPCA = imgPCA.set('id', name)
            imgPCA = imgPCA.set('method', 'pca')
            imgPCA = imgPCA.set('noImgs_serie', sizeCol)
            imgPCA = imgPCA.set('source', 'geodatin')

            exportImage(imgPCA, name, geoms)

    arqFeitos.write(idname + '\n')
    

arqFeitos.close()





