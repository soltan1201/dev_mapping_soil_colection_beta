var Palettes = require('users/mapbiomas/modules:Palettes.js');
var palette = Palettes.get('classification7');
var vis = {
    mapbiomas : {
        min: 1,
        max: 62,
        palette: palette
    },
    soil: {
        min: 0, max: 1,
        palette: 'FFFFFF, B68037'
    }
}

var getPolygonsfromFolder = function(assetsROis){
    
    var getlistPtos = ee.data.getList(assetsROis);   
    var lstFeatsPtos = [];
    print("getlistPtos ", getlistPtos);
    getlistPtos.forEach(function(idAsset){ 
        // print(idAsset)
        var path_ = idAsset.id;
        var partes = path_.split('/');
        var name = partes[partes.length - 1]
        lstFeatsPtos.push(name)
                  
    }) ;     
    return  lstFeatsPtos;
}
var params = {
'assets':{
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',  //# SPRNOME: 247/84
    'inputAsset': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico/',     
    'biomas': "users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas",   
    'mapbiomas': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'inputROIs': {'id':'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil'}
},
'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
// # 'classNew'  : [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
'classNew'  : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
'sensorIds': {        
    'L5': 'LANDSAT/LT05/C01/T1_SR',
    'L7': 'LANDSAT/LE07/C01/T1_SR',
    'L8': 'LANDSAT/LC08/C01/T1_SR'
}, 
'zeroT1_SR' : false,
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
        '229' : ['58','59','60','61','62','63','64','65','66','67','68','69','70','71'],		
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
}, 
'lsPath' : {
    'AMAZONIA' : ['1','2','3','4','5','6','220','221','222','223','224','225','226','227','228','229','230','231','232','233'], 
    'CAATINGA' : ['214','215','216','217','218','219','220'],
    'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'],
    'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'],  
    'PAMPA':['220','221','222','223','224','225'],
    'PANTANAL':['225','226','227','228']
}, 
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
'list_biomes': ['AMAZONIA', 'CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'], // 'CAATINGA',
'bnd_LG': ['blue','green','red','nir','swir1','swir2','pixel_qa'],
'bnd_L': ['blue','green','red','nir','swir1','swir2'],
'CC': 70,
'initYear': 1985,
'endYear': 2023,
'dependent': 'NDFIa',
'harmonics': 2,
'dateInit': '2018-01-01'    
}



var mapsBiomas = ee.Image(params['assets']['mapbiomas'])
var anoInicial = params['initYear']
var lsAnos = ee.List.sequence(params['initYear'], params['endYear']).getInfo()
print("lista de anos ", lsAnos)
var gradeLandsat = ee.FeatureCollection(params['assets']['gradeLandsat'])
var coletaSoil = true
// # imgColmosaic = ee.ImageCollection(params['assets']['inputAsset'])
var dictPath = {}
var lstBnd = ['min','max','stdDev','amp','class']
// # 'AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'

var classAct = 1
if (params['assets']['inputROIs']['id'].indexOf('ROIsSoil') > -1){
classAct = 1
}else{
classAct = 0
}
var lstFeatCols = getPolygonsfromFolder(params['assets']['inputROIs']);
print("readed  featCols in the folder Assets => " + lstFeatCols.length.toString());

var nameROIs = 'rois_fitted_image_AMAZONIA_2022_1_57';
var partes = nameROIs.split("_");
var biome_act = partes[3];
var wrsP = partes[5];
var wrsR = partes[6];
var yyear = partes[4];
print("reading Bioma  =>  " + biome_act);
print("reading Path = " + wrsP);
print("reading Row = " + wrsR);
print("reading Year = " + yyear);

var geoms = gradeLandsat.filter(ee.Filter.eq('PATH', parseInt(wrsP))).filter(
                                    ee.Filter.eq('ROW', parseInt(wrsR))).geometry() 
var geomsBounds = geoms.buffer(-2000)
var recMapbiomas = mapsBiomas.clip(geoms)


var nameImg = 'fitted_image_' + biome_act + '_' + yyear + '_' + wrsP + '_' + wrsR

var imgMosYY = ee.Image(params['assets']['inputAsset'] + nameImg);

print("image MosYY ", imgMosYY);
var bandsIm = imgMosYY.bandNames().getInfo();
print("bandas iniciais ", bandsIm)

if (bandsIm.length  > 0){
    if (yyear === '2022'){
        yyear = '2021';
    }
    var maskMapbiomas = recMapbiomas.select('classification_' + yyear)
                                    .remap(params.classMapB, params.classNew)
                                    .clip(geomsBounds)
    
    if (coletaSoil === true){
        imgMosYY = imgMosYY.updateMask(maskMapbiomas)
        var imgMin = imgMosYY.reduce(ee.Reducer.min()).rename('min')
        var imgMax = imgMosYY.reduce(ee.Reducer.max()).rename('max')
        var imgstdDev = imgMosYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
        var imgAmp = imgMax.subtract(imgMin).rename('amp')                   
        
        var maskSoil = imgMin.lte(6000)//# .multiply(imgMax.lte(9000)).multiply(imgAmp.lte(4000))                            
        imgMosYY = imgMosYY.addBands(imgMin).addBands(imgMax).addBands(
                            imgstdDev).addBands(imgAmp).addBands(
                                    maskSoil.rename('class'))
                                        
    }else{
        var maskMapbiomas = maskMapbiomas.eq(0).rename('class')
        var imgMosYY = imgMosYY.updateMask(maskMapbiomas)
        var imgMin = imgMosYY.reduce(ee.Reducer.min()).rename('min')
        var imgMax = imgMosYY.reduce(ee.Reducer.max()).rename('max')
        var imgstdDev = imgMosYY.reduce(ee.Reducer.stdDev()).rename('stdDev')
        var imgAmp = imgMax.subtract(imgMin).rename('amp') 

        imgMosYY = imgMosYY.addBands(imgMin).addBands(imgMax).addBands(
                            imgstdDev).addBands(imgAmp).addBands(
                                    maskMapbiomas)
    }
    imgMosYY = imgMosYY.select(lstBnd)
    
    Map.addLayer(geomsBounds, {color: 'green'}, 'limit grade', false);
    Map.addLayer(recMapbiomas.select('classification_' + yyear), vis.mapbiomas, 'Mapbiomas');
    Map.addLayer(maskMapbiomas.selfMask(), vis.soil, 'MaskSoil');
    Map.addLayer(imgMosYY, {}, 'imgMosYY');
    
    // Map.centerObject(geomsBounds, 12);
    
    var pmtSample= {
        'numPoints': 1500,
        'classBand': 'class',
        'region': geomsBounds,                            
        'scale': 30,                            
        'projection': 'EPSG:3665',                        
        'dropNulls': true,
        'tileScale': 4,
        'geometries': true
    }
    var points = imgMosYY.stratifiedSample(pmtSample)  
}