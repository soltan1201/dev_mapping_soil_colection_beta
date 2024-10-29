
var palettes = require('users/mapbiomas/modules:Palettes.js');
var visualizar = {
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
    reviewer: {  
        'min': 0, 'max': 3,
        'palette': 'FFFFFF,8C2D04,FFFFB2,FFFFB2'
    },
    'mosaicHarm': {
        min:5000, 
        max:15000,
        bands: ['median','min','max']
    },
    layerSoilMB : {min:0, max:1, palette: '000000, 00ffbb'}

} ;
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

var  calculateArea = function (imageMap, ngeometry){
    var pixelArea = ee.Image.pixelArea().divide(10000)
    pixelArea = pixelArea.multiply(imageMap.eq(1).selfMask()).clip(ngeometry).rename('area');    
    var optRed = {
        'reducer': ee.Reducer.sum(),
        'geometry': ee.Geometry(ngeometry),
        'scale': 30,
        'bestEffort': true, 
        'maxPixels': 1e13
    }    
    var areas = pixelArea.reduceRegion(optRed)

    areas = areas.values().getInfo()       
    return areas
}
var param = {
    'class_solo': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  : [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'folder_rois': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIs'},
    'folder_roisVeg': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg'},
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_mosaic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2', 
    'bandas': ['red_median', 'green_median', 'blue_median'], 
};


var yyear = 1985;
var wrsP = 219;
var wrsR = 69;
var biome_act = 'CERRADO';
var keyPathRow = biome_act + "_" + wrsP.toString() + "_" + wrsR.toString();
var regionss = ee.FeatureCollection(param.regions)
var gradeLandsat = ee.FeatureCollection(param.gradeLandsat).filter(
                            ee.Filter.eq('PATH', wrsP)).filter(            
                                    ee.Filter.eq('ROW', wrsR)).geometry()

var mapbiomas = ee.Image(param.inputAsset).select('classification_' + yyear.toString());
var nameSaved = 'fitted_image_' + biome_act + "_" + yyear.toString() ;
nameSaved = nameSaved + '_' + wrsP.toString() + '_' + wrsR.toString() + 'V1';



var mosaicHarms = ee.ImageCollection(param.asset_mosaic).filter(
                      ee.Filter.eq('WRS_PATH', wrsP.toString())).filter(            
                          ee.Filter.eq('WRS_ROW', wrsR.toString()))
                              .filter(ee.Filter.eq('year', yyear))
                                //.first();
var sizeMosaic = mosaicHarms.size().getInfo();
if (sizeMosaic > 0){
    print("mosaic harmonicos ", mosaicHarms);
    mosaicHarms = mosaicHarms.first();
    print("numero de bandas ", mosaicHarms.bandNames());
    mosaicHarms = ApplyReducers(mosaicHarms);
    Map.addLayer(mosaicHarms, visualizar.mosaicHarm, 'MosaicHarm');
}

// projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2/classSoil_AMAZONIA_1985_1_57V1 
var mapsSoils = ee.ImageCollection(param.class_solo).filter(
                       ee.Filter.eq('WRS_PATH', wrsP.toString())).filter(            
                            ee.Filter.eq('WRS_ROW', wrsR.toString()))
                                .filter(ee.Filter.eq('year', yyear));
var sizeMap = mapsSoils.size().getInfo();
if (sizeMap > 0){
    print("mapas de solo ", mapsSoils);
    mapsSoils = mapsSoils.first()
}else{
    mapsSoils = ee.Image.constant(0).clip(regionss);
}
var maskMapsSoils = mapsSoils.gt(0);
Map.addLayer(mapsSoils.updateMask(maskMapsSoils), visualizar.reviewer, "mapa Soil");

var areasSoils = calculateArea(mapsSoils, gradeLandsat);
print("Área em solo ", areasSoils);

