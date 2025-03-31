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
        'palette': 'FFFFFF, 8b4513, a0522d'
    },
}
var params = {
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'asset_layer_soil': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV5',
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'assetMapbiomas90': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'months': [1,2,3,4,5,6,7,8,9,10,11,12]
}

var yyear = 2021;
var regionSelect = 31;
var regionSel = ee.FeatureCollection(params.region).filter(ee.Filter.eq('region', regionSelect));
var imgMaskReg = regionSel.reduceToImage(['region'], ee.Reducer.first()).gt(1);
var mapsSoilsV4 = ee.ImageCollection(params.classmappingV4)
                      .filter(ee.Filter.eq('region',  String(regionSelect)))
                      .filter(ee.Filter.eq('year', yyear))
// 31regionSel.geometry()); // camada de base 
print('show layer versao 4', mapsSoilsV4)
params.months.forEach(function(mmonth){
    var data_inicial = ee.Date.fromYMD(yyear, mmonth, 1);
    var imColMonth = ee.ImageCollection(params.asset_collectionId)
                        .filterBounds(regionSel.geometry())
                        .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                        .select(params.bnd_L).first()
                        .updateMask(imgMaskReg);
                
    var layer_soil = ee.ImageCollection(params.asset_layer_soil)
                          .filter(ee.Filter.eq('region', regionSelect))
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

Map.addLayer(mapsSoilsV4, vis.reviewer, "layer soil V4");
Map.addLayer(mMapbiomas, vis.visclassCC, 'Mapbiomas ' + yyear,false);                    