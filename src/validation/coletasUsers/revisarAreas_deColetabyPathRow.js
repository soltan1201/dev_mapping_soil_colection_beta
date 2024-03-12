
var palettes = require('users/mapbiomas/modules:Palettes.js');
var visualizar = {
    'visclassCC': {
            "min": 0, 
            "max": 62,
            "palette":  palettes.get('classification7'),
            "format": "png"
    },
    'visMosaic': {
        min: 0,
        max: 2000,
        bands: ['red_median', 'green_median', 'blue_median']
    },
    'reviewer': {  
        'min': 0, 'max': 2,
        'palette': 'FFFFFF, 8C2D04, FF0000'
    },
    'mosaicoH': {
        min:5000, 
        max:15000,
        bands: ['median','min','max']
    }
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
}
var param = {
    'class_solo': 'projects/mapbiomas-workspace/DEGRADACAO/COLECAO/BETA/PROCESS/CAMADA_SOLO',
    'classmappingV2': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  : [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
    'folder_rois': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIs'},
    'folder_roisVeg': {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg'},
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_mosaic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'asset_mosaic2': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonicoCaat',
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

var region_selected = 41;
var wpath = 214;
var wrow = 64;
var yyear = 1986;
var bioma_select = 'MATA_ATLANTICA';

var regionss = ee.FeatureCollection(param.regions);
var regioes = regionss.geometry();
var gradeLandsat = ee.FeatureCollection(param.gradeLandsat)
                                    .filter(ee.Filter.eq('PATH', parseInt(wpath))).filter(
                                    ee.Filter.eq('ROW', parseInt(wrow)))
var mapbiomas = ee.Image(param.inputAsset).select('classification_' + yyear.toString());
//Duna 23, Urbano 24, Mining 30
var areasIntMapb = mapbiomas.remap(param.classMapB, param.classNew);
var nameImg = 'fitted_image_' + bioma_select + '_' + yyear.toString() + '_' + wpath.toString() + '_' + wrow.toString();
var mosaicHarms = ee.Image(param.asset_mosaic + "/" + nameImg )

mosaicHarms = ApplyReducers(mosaicHarms);

var Mosaicos = ee.ImageCollection(param.assetIm)
                    .filter(ee.Filter.eq('year', yyear))
                    .select(param.bandas).median()  
print("Show mosaic Mapbiomas ", Mosaicos);

Map.addLayer(Mosaicos, visualizar.visMosaic,'Mosaic Col8', false);
Map.addLayer(mosaicHarms, visualizar.mosaicoH, 'MosaicHarm ' + yyear.toString() + '_A');
Map.addLayer(mapbiomas, visualizar.visclassCC, "Mapbiomas Col8" , false);
Map.addLayer(areasIntMapb, visualizar.reviewer, 'reclass', false)
