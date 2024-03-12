// https://code.earthengine.google.com/5af814a35ff4e480ea15f50d2eef3fcc
var dictGradesBR = {
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
};

var param = {
    'asset_mosaic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',   
    'asset_mapbiomas':  'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'asset_output':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIs',
    'propiedadedasImages': [
        'WRS_PATH','WRS_ROW','biome','method',
        'noImgs_serie','source','year'
    ],
    'lsGrade' : dictGradesBR, 
    'lsPath' : {
        'AMAZONIA' : ['2','3','4','5','6','220','221','222','223','224','225','226','227','228','229','230','231','232','233'], # '1',
        'CAATINGA' : ['214','215','216','217','218','219','220'],
        'CERRADO': ['217','218','219','220','221','222','223','224','225','226','227','228','229','230'],
        'MATA_ATLANTICA':['214','215','216','217','218','219','220','221','222','223','224','225'], // 
        'PAMPA':['220','221','222','223','224','225'],
        'PANTANAL':['225','226','227','228']
    },
    'lst_biomas': ['AMAZONIA','CAATINGA','CERRADO','MATA_ATLANTICA','PAMPA','PANTANAL'],
    'bandas': ['red_median', 'green_median', 'blue_median'],
};
var palettes = require('users/mapbiomas/modules:Palettes.js');
var vis = {
    'mosaic': {
        min:5000, 
        max:15000,
        bands: ['median','min','max']
    },
    visclassCC: {
            "min": 0, 
            "max": 62,
            "palette":  palettes.get('classification7'),
            "format": "png"
    },
    visMosaic: {
        min: 0,
        max: 2000,
        bands: ['red_median', 'green_median', 'blue_median']
    },
};
var ApplyReducers = function (img) {

    var bndReds = ['sum','median','mean','mode','stdDev','max','min','amp'];
    // Reducer all bands to statistics reducers images
    var img_sum =  img.reduce(ee.Reducer.sum()).rename('sum');
    var img_median = img.reduce(ee.Reducer.median()).rename('median');
    var img_mean = img.reduce(ee.Reducer.mean()).rename('mean');    
    var img_mode = img.reduce(ee.Reducer.mode()).rename('mode');
    var img_stdDev = img.reduce(ee.Reducer.stdDev()).rename('stdDev');
    var img_max = img.reduce(ee.Reducer.max()).rename('max');
    var img_min = img.reduce(ee.Reducer.min()).rename('min');
    var img_amp = img_max.subtract(img_min).rename('amp');
    
    return img.addBands(img_median).addBands(img_mean).addBands(img_sum)
                .addBands(img_mode).addBands(img_stdDev)
                .addBands(img_max).addBands(img_min).addBands(img_amp)
                .select(bndReds) //.copyProperties(img)
};


var save_ROIs_toAsset = function(collection, name_exp){

    var optExp = {
        'collection': collection,
        'description': name_exp,
        'assetId': param.asset_output + "/" + name_exp
    };
    Export.table.toAsset(optExp);
    print("exports a set points ...!", name_exp)
};

var sample_points_inPolygons = function(feat){
      var pmtros = {
            region: feat.geometry(), 
            points: 100
      };
      var featCPoints = ee.FeatureCollection.randomPoints(pmtros);
      return featCPoints;
};

var imgMapCol71 = ee.Image(param.asset_mapbiomas).select('classification_2021');
var imgCol = ee.ImageCollection(param.asset_mosaic)
                    .filter(ee.Filter.eq('biome', param.lst_biomas[3]));
imgCol = imgCol.map(ApplyReducers)
print("Show the first images ", imgCol.first());

var Mosaicos = ee.ImageCollection(param.assetIm)
                      .filter(ee.Filter.eq('biome', 'MATAATLANTICA'))
                      .filter(ee.Filter.eq('year', 2021))
                      .select(param.bandas).median();    
print("Show mosaic Mapbiomas ", Mosaicos);

var ROIspol = ee.FeatureCollection(areas_solo_exp).merge(outras_areas);
var pointsROIs = ROIspol.map(sample_points_inPolygons);
pointsROIs = pointsROIs.flatten();
var nameExp = "rois_points_" + param.lst_biomas[3];
// Save the feature Collections
save_ROIs_toAsset(pointsROIs, nameExp);

Map.addLayer(Mosaicos, vis.visMosaic,'Mosaic Col8', false);
Map.addLayer(imgMapCol71, vis.visclassCC,'Col71_2021', false);
Map.addLayer(imgCol, vis.mosaic, 'MosaicHarm Red');