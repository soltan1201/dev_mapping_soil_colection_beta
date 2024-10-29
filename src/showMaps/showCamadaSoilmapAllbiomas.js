
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
        'min': 0, 'max': 1,
        'palette': 'FFFFFF, 8C2D04'
    },
    'mosaic': {
        min:5000, 
        max:15000,
        bands: ['median','min','max']
    },
    layerSoilMB : {min:0, max:1, palette: '000000, 00ffbb'}

} ;


var ApplyReducers = function (img) {
    var bndReds = ['median','stdDev','max','min'];
    // Reducer all bands to statistics reducers images
    var img_median = img.reduce(ee.Reducer.median()).rename('median');
    var img_stdDev = img.reduce(ee.Reducer.stdDev()).rename('stdDev');
    var img_max = img.reduce(ee.Reducer.max()).rename('max');
    var img_min = img.reduce(ee.Reducer.min()).rename('min');
    
    return img.addBands(img_median).addBands(img_stdDev)
                .addBands(img_max).addBands(img_min).select(bndReds);
};

var param = {
    'class_solo': 'projects/mapbiomas-workspace/DEGRADACAO/COLECAO/BETA/PROCESS/CAMADA_SOLO',
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
var dictNameBiome = {
    'AMAZONIA': 'Amazônia', 
    'CERRADO': 'Cerrado',
    'CAATINGA': 'Caatinga',
    'MATA_ATLANTICA': 'Mata Atlântica', 
    'PAMPA': 'Pampa',
    'PANTANAL': 'Pantanal'
};
var dictRegions = {
    "Pampa": ['51','52','53'],
    "Cerrado": ['31','32','35','34','33'],
    'Caatinga': ['21','22','23','24'],
    "Pantanal": ['60'],
    'Amazônia': ['11','12','13','14','15','16','17','18','19'],
    "Mata Atlântica":['41','42','44','45','46','47']
};

var yyear = 1988;

var regionss = ee.FeatureCollection(param.regions)
var gradeLandsat = ee.FeatureCollection(param.gradeLandsat)
var mapbiomas = ee.Image(param.inputAsset).select('classification_' + yyear.toString());

var mapsSoils = ee.ImageCollection(param.class_solo)
                      .filter(ee.Filter.eq('year', yyear)).max();

print("mapas de solo ", mapsSoils);
var mosaicHarms = ee.ImageCollection(param.asset_mosaic)
                            .filter(ee.Filter.eq('year', yyear));

print("mosaic harmonicos ", mosaicHarms);
mosaicHarms = mosaicHarms.map(ApplyReducers);

var Mosaicos = ee.ImageCollection(param.assetIm)                    
                    .filter(ee.Filter.eq('year', yyear))
                    .select(param.bandas).median() 

print("Show mosaic Mapbiomas ", Mosaicos);
Map.addLayer(Mosaicos, visualizar.visMosaic, 'Mosaic Col8', false);
Map.addLayer(mosaicHarmsYear, visualizar.mosaic, 'MosaicHarm ' + myear.toString() + '_A');
Map.addLayer(mapbiomas, visualizar.visclassCC, "Mapbiomas Col8" , false);
Map.addLayer(mapsSoils.selfMask(), visualizar.reviewer, "mapSoil_" + yyear.toString());
Map.addLayer(mapbiomas.eq(25).selfMask(),visualizar.layerSoilMB, 'soloMapbiomas', false);
var gradeL8 = ee.Image().byte().paint({
  featureCollection: gradeLandsat,  color: 1,  width: 1.5});
Map.addLayer(gradeL8, {color: 'fec44f'}, "grade Mapping", false);


var regions = ee.Image().byte().paint({
  featureCollection: regionss,  color: 1,  width: 1.5});
Map.addLayer(regions, {color: 'ff004a'}, "regions", false);

