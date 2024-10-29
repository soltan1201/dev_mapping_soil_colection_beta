
var palettes = require('users/mapbiomas/modules:Palettes.js');
var vis = {
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
    mosaicHarm: {
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
    asset_mosaic: 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    classmappingV3: 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3',
}
var yyear = 1988;
//bioma Caatinga apararece sem parametro bioma 
var mosaicHarm = ee.ImageCollection(param.asset_mosaic)
                        .filter(ee.Filter.eq('biome', null))

// print(mosaicHarm.aggregate_histogram('biome'))
print("show years with data ", mosaicHarm.aggregate_histogram('year'));
print("show metadata of Image Collection ", mosaicHarm.limit(3));
print("show quantity of raster in ", mosaicHarm.size())
var mosaicYY = mosaicHarm.filter(ee.Filter.eq('year', yyear));
mosaicYY = mosaicYY.map(ApplyReducers);

var classSoil = ee.ImageCollection(param.classmappingV3);

print("know metadata of image collection ClassSoil", classSoil);

Map.addLayer(mosaicYY, vis.mosaicHarm, 'mosaicHarm Caat');