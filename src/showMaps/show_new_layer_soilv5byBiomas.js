var palettes = require('users/mapbiomas/modules:Palettes.js');
var vis = {
    'visclassCC': {
            "min": 0, 
            "max": 69,
            "palette":  palettes.get('classification9'),
            "format": "png"
    },
    'visMosaic': {
        min: 0,
        max: 0.15,
        bands: ['red', 'green', 'blue']
    },
    'reviewer': {  
        'min': 0, 'max': 1,
        'palette': 'FFFFFF, D93FFF',
    },
    'soilV2': {  
        'min': 0, 'max': 2,
        'palette': 'FFFFFF, cc7a03, a0522d'
    },
}
// biomas para print 
//https://code.earthengine.google.com/4ec7b9b33ffa6d859e4699c6d37e66df
//
var params = {
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'asset_layer_soil': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV5',
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'assetMapbiomas90': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'months': [1,2,3,4,5,6,7,8,9,10,11,12]
}
var dictRegions = {
    "PAMPA": [51,52,53],
    "CERRADO": [31,32,35,34,33],
    'CAATINGA': [21,22,23,24],
    "PANTANAL": [60],
    'AMAZONIA': [11,12,13,14,15,16,17,18,19],
    "MATAATLANTICA":[41,42,44,45,46,47]
};
var dictRegionsS = {
    "Pampa": ['51','52','53'],
    "Cerrado": ['31','32','35','34','33'],
    'Caatinga': ['21','22','23','24'],
    "Pantanal": ['60'],
    'Amazônia': ['11','12','13','14','15','16','17','18','19'],
    "Mata Atlântica":['41','42','44','45','46','47']
};
var biomas_select = 'CAATINGA';
var yyear = 2021;
var regionsSelect = dictRegions[biomas_select];
var regionSel = ee.FeatureCollection(params.region).filter(ee.Filter.inList('region', regionsSelect));
var imgMaskReg = regionSel.reduceToImage(['region'], ee.Reducer.first()).gt(1);
var mapsSoilsV4 = ee.ImageCollection(params.classmappingV4)
                      .filter(ee.Filter.inList('region',  dictRegionsS[biomas_select]))
                      .filter(ee.Filter.eq('year', yyear))
// 31regionSel.geometry()); // camada de base 
print('show layer versao 4', mapsSoilsV4)
params.months.forEach(function(mmonth){
    var data_inicial = ee.Date.fromYMD(yyear, mmonth, 1);
    var imColMonth = ee.ImageCollection(params.asset_collectionId)
                        .filterBounds(regionSel.geometry())
                        .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                        .select(params.bnd_L).max()
                        .updateMask(imgMaskReg);
                
    var layer_soil = ee.ImageCollection(params.asset_layer_soil)
                          .filter(ee.Filter.inList('region', regionsSelect))
                          .filter(ee.Filter.eq('year', yyear))
                          .filter(ee.Filter.eq('month', mmonth))
                          .first();
                          
    print("Loading layer soil from " + yyear + " >> " + mmonth);
    Map.addLayer(imColMonth, vis.visMosaic, 'mosaic month', false);
    Map.addLayer(layer_soil.selfMask(), vis.soilV2, 'layer soil_' + mmonth, false);
});

mapsSoilsV4 = mapsSoilsV4.max().gte(0.84).selfMask();
var mMapbiomas = ee.Image(params['assetMapbiomas90'])
                        .updateMask(imgMaskReg).select('classification_' + String(yyear));

Map.addLayer(mapsSoilsV4, vis.reviewer, "layer soil HarmV4");
Map.addLayer(mMapbiomas, vis.visclassCC, 'Mapbiomas ' + yyear,false);                    
var dictPaint = {featureCollection: regionSel,  color: 1,  width: 1.5};
var regions = ee.Image().byte().paint(dictPaint);
Map.addLayer(regions, {color: 'ff004a'}, "regions", true);