//GENERAL PARAMS
var GENERAL_PARAMS = {
    COL_L5: 'LANDSAT/LT05/C02/T1_L2',
    COL_L7: 'LANDSAT/LE07/C02/T1_L2',
    COL_L8: 'LANDSAT/LC08/C02/T1_L2',
    BIOMAS: 'projects/mapbiomas-workspace/AUXILIAR/ESTATISTICAS/COLECAO7/biome',
    CAATINGA: 'CAATINGA',
    DATE_INI: '2017-01-01',
    DATE_FIN: '2021-12-31',
    MAPBIOMAS: 'projects/mapbiomas-workspace/COLECAO4/mapbiomas_collection40_integration_v3',
    AOI: geometry
};

var batch = require('users/fitoprincipe/geetools:batch')

//LS PARAMS
var VIS_PARAMS_LS = {
    bands: ['SR_B6', 'SR_B5', 'SR_B3'],
    min: 0,
    max: 0.4
};

//INDEX PALETTE
var PALETTES = require('users/gena/packages:palettes');

var PALETTES = PALETTES.colorbrewer.RdYlGn[11];


//CLOUD AND SHADOW MASK
function MASK_L457SR(image) {
    // Bit 0 - Fill
    // Bit 1 - Dilated Cloud
    // Bit 2 - Unused
    // Bit 3 - Cloud
    // Bit 4 - Cloud Shadow
    var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
    var saturationMask = image.select('QA_RADSAT').eq(0);

    // Apply the scaling factors to the appropriate bands.
    var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
    var thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0);

    // Replace the original bands with the scaled ones and apply the masks.
    return image.addBands(opticalBands, null, true)
        .addBands(thermalBand, null, true)
        .updateMask(qaMask)
        .updateMask(saturationMask)
        .select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7'])
        .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
}

function MASK_L8SR(image) {
    // Bit 0 - Fill
    // Bit 1 - Dilated Cloud
    // Bit 2 - Cirrus
    // Bit 3 - Cloud
    // Bit 4 - Cloud Shadow
    var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
    var saturationMask = image.select('QA_RADSAT').eq(0);

    // Apply the scaling factors to the appropriate bands.
    var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
    var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);

    // Replace the original bands with the scaled ones and apply the masks.
    return image.addBands(opticalBands, null, true)
        .addBands(thermalBands, null, true)
        .updateMask(qaMask)
        .updateMask(saturationMask)
        .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
}


// HARMONIZATION ETM/TM to OLI
var coefficients = {
    itcps: ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]),
    slopes: ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
};

function L457SR_TO_L8SR(image) {
    var orig = image
    return image.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])
        .multiply(coefficients.slopes)
        .add(coefficients.itcps)
        //.round()
        //.toShort()
        .copyProperties(orig, orig.propertyNames())
}


// UNMIXING and NDFIA
var INDEX_PARAMS = ee.Dictionary({
    'gv': [0.05, 0.09, 0.04, 0.61, 0.30, 0.10],
    'npv': [0.14, 0.17, 0.22, 0.30, 0.55, 0.30],
    'soil': [0.20, 0.30, 0.34, 0.58, 0.60, 0.58],
    'shade': [0, 0, 0, 0, 0, 0],
    'cloud': [0.90, 0.96, 0.80, 0.78, 0.72, 0.65],
});

function GET_NDFIA (COLLECTION, INDEX_PARAMS) {

    return COLLECTION.map(function (IMAGE) {

        var GV = INDEX_PARAMS.get('gv');
        var NPV = INDEX_PARAMS.get('npv');
        var SOIL = INDEX_PARAMS.get('soil');
        var SHADE = INDEX_PARAMS.get('shade');
        var CLOUD = INDEX_PARAMS.get('cloud');

        var UNMIX_IMAGE = ee.Image(IMAGE)
            .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])
            .unmix([GV, NPV, SOIL, SHADE, CLOUD], true, true)
            .rename('GV', 'NPV', 'SOIL', 'SHADE', 'CLOUD')
        var UNMIXED_IMAGE = ee.Image(IMAGE).addBands(UNMIX_IMAGE)

        var NDFI_ADJUSTED = UNMIXED_IMAGE.expression(
            '((GV / (1 - SHADE)) - SOIL) / ((GV / (1 - SHADE)) + (NPV) + SOIL)', {
            'GV': ee.Image(UNMIXED_IMAGE).select('GV'),
            'SHADE': ee.Image(UNMIXED_IMAGE).select('SHADE'),
            'NPV': ee.Image(UNMIXED_IMAGE).select('NPV'),
            'SOIL': ee.Image(UNMIXED_IMAGE).select('SOIL')
        })
            .rename('NDFIa')

        NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()

        var RESULT_IMAGE = UNMIXED_IMAGE.addBands(NDFI_ADJUSTED)

        return ee.Image(RESULT_IMAGE)
    })
}

//LOAD CAATINGA BIOME

var CAATINGA = ee.FeatureCollection(GENERAL_PARAMS.BIOMAS)
    .filter(ee.Filter.eq('name_en', GENERAL_PARAMS.CAATINGA));

var GRID = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2')
    .filterBounds(CAATINGA)//.filterBounds(geometry)

Map.addLayer(GRID)

//LOAD AND PREP COLLECTIONS


var ano = 1988

var TIME_SEQUENCE = ee.List.sequence(ano, ano).map(function FITTED_NDFIa_IMAGE_YEAR(YEAR) {

    YEAR = ee.Number(YEAR)

    var GRID_FITTED = GRID.map(function FITTED_NDFIa_IMAGE(FEATURE) {

        var BEFORE_DATE = ee.Date.fromYMD(YEAR.subtract(2), 1, 1);
        var AFTER_DATE = ee.Date.fromYMD(YEAR.add(2), 12, 31);

        var COLECTION_L8 = ee.ImageCollection(GENERAL_PARAMS.COL_L8)
            .filterBounds(FEATURE.centroid().geometry())
            .filterDate(BEFORE_DATE, AFTER_DATE)
            .filter(ee.Filter.lte('CLOUD_COVER', 70))
            .map(MASK_L8SR)

        var COLECTION_L7 = ee.ImageCollection(GENERAL_PARAMS.COL_L7)
            .filterBounds(FEATURE.centroid().geometry())
            .filterDate(BEFORE_DATE, AFTER_DATE)
            .filter(ee.Filter.lte('CLOUD_COVER', 80))
            .map(MASK_L457SR)
            //.map(L457SR_TO_L8SR)

        var COLECTION_L5 = ee.ImageCollection(GENERAL_PARAMS.COL_L5)
            .filterBounds(FEATURE.centroid().geometry())
            .filterDate(BEFORE_DATE, AFTER_DATE)
            .filter(ee.Filter.lte('CLOUD_COVER', 80))
            .map(MASK_L457SR)
            //.map(L457SR_TO_L8SR)

        var COLLECTION = COLECTION_L8.merge(COLECTION_L5)//.merge(COLECTION_L7)

        COLLECTION = ee.ImageCollection(GET_NDFIA(COLLECTION, INDEX_PARAMS))
        
        COLLECTION = COLLECTION.map(function (image) { return image.clip(FEATURE) })



        // This field contains UNIX time in milliseconds.
        var TIME_FIELD = 'system:time_start';

        // Set the region of interest to a point.
        //var roi = geometry;

        // The dependent variable we are modeling.
        var DEPENDENT = 'NDFIa';

        // The number of cycles per year to model.
        var HARMONICS = 2;

        // Make a list of harmonic frequencies to model.
        // These also serve as band name suffixes.
        var HARMONIC_FREQUENCIES = ee.List.sequence(1, HARMONICS);

        // Function to get a sequence of band names for harmonic terms.
        var CONSTRUCT_BAND_NAMES = function (base, list) {
            return ee.List(list).map(function (i) {
                return ee.String(base).cat(ee.Number(i).int());
            });
        };

        // Construct lists of names for the harmonic terms.
        var COS_NAMES = CONSTRUCT_BAND_NAMES('cos_', HARMONIC_FREQUENCIES);
        var SIN_NAMES = CONSTRUCT_BAND_NAMES('sin_', HARMONIC_FREQUENCIES);

        // Independent variables.
        var INDEPENDENTS = ee.List(['constant', 't'])
            .cat(COS_NAMES).cat(SIN_NAMES);

        //print(INDEPENDENTS)
        var nINDEPENDENTS = COS_NAMES.cat(SIN_NAMES)

        // Function to add a time band.
        var ADD_DEPENDENTS = function (image) {
            // Compute time in fractional years since the epoch.
            var years = image.date().difference(GENERAL_PARAMS.DATE_INI, 'day');
            var timeRadians = ee.Image(years.multiply(2 * Math.PI)).rename('t');
            var constant = ee.Image(1);
            return image.addBands(constant).addBands(timeRadians.float());
        };

        //Get a mean of time series

        var IMG_MEAN = COLLECTION.select('NDFIa').reduce('mean').rename('mean')
        //Map.addLayer(IMG_MEAN)

        // Function to compute the specified number of harmonics
        // and add them as bands.  Assumes the time band is present.
        var ADD_HARMONICS = function (freqs) {
            return function (image) {
                // Make an image of frequencies.
                var frequencies = ee.Image.constant(freqs);
                // This band should represent time in radians.
                var time = ee.Image(image).select('t');
                // Get the cosine terms.
                var cosines = time.multiply(frequencies).divide(365.25).cos().rename(COS_NAMES);  //
                // Get the sin terms.
                var sines = time.multiply(frequencies).divide(365.25).sin().rename(SIN_NAMES);   //

                return image.addBands(cosines).addBands(sines);
            };
        };

        // Filter to the area of interest, mask clouds, add variables.
        var HARMONIC_LANDSAT = COLLECTION
            .map(ADD_DEPENDENTS)
            .map(ADD_HARMONICS(HARMONIC_FREQUENCIES));


        // The output of the regression reduction is a 4x1 array image.
        var HARMONIC_TREND = HARMONIC_LANDSAT
            .select(INDEPENDENTS.add(DEPENDENT))
            .reduce(ee.Reducer.linearRegression(INDEPENDENTS.length(), 1));


        // Turn the array image into a multi-band image of coefficients.
        var HARMONIC_TREND_COEFFICIENTS = HARMONIC_TREND.select('coefficients')
            .arrayProject([0])
            .arrayFlatten([INDEPENDENTS]);

        //print(HARMONIC_TREND_COEFFICIENTS)
        //Map.addLayer(HARMONIC_TREND_COEFFICIENTS)

        // Compute fitted values.
        var FITTED_HARMONIC = HARMONIC_LANDSAT.map(function (image) {
            return image.addBands(
                image.select(nINDEPENDENTS)
                    .multiply(HARMONIC_TREND_COEFFICIENTS.select(nINDEPENDENTS))
                    .reduce('sum')
                    .add(IMG_MEAN)
                    .rename('fitted'));
        });
        //print(FITTED_HARMONIC)
        
        FITTED_HARMONIC = FITTED_HARMONIC.select('fitted')
                            .filterDate(ee.Date.fromYMD(YEAR, 01, 01), ee.Date.fromYMD(YEAR, 12, 31))
        
        return ee.Image(FITTED_HARMONIC.reduce(ee.Reducer.sum()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.median()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.mean()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.variance()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.mode()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.stdDev()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.max()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.min()))
              .addBands(FITTED_HARMONIC.reduce(ee.Reducer.max()).subtract(
              FITTED_HARMONIC.reduce(ee.Reducer.min())).rename('fitted_amp'))
          
    })


    //print(ui.Chart.image.series(FITTED_HARMONIC.select(['NDFIa', 'fitted']), GENERAL_PARAMS.AOI , ee.Reducer.first(), 30))

    GRID_FITTED = ee.ImageCollection(GRID_FITTED)
    GRID_FITTED = ee.Image(GRID_FITTED.mosaic()).set('year', YEAR)

    //print(GRID_FITTED)
    //Map.addLayer(GRID_FITTED.mosaic())
    
    return GRID_FITTED
})
//print(TIME_SEQUENCE)
//
TIME_SEQUENCE = ee.ImageCollection.fromImages(TIME_SEQUENCE)
//
print(TIME_SEQUENCE)
Map.addLayer(TIME_SEQUENCE)
//
var size = TIME_SEQUENCE.size().getInfo()
var listOfImage = TIME_SEQUENCE.toList(size)

print(listOfImage)

for (var i = 0; i < size; i++) {
    var img = ee.Image(listOfImage.get(i));
    var test = img.get('year').getInfo();
    var id = 'projects/mapbiomas-arida/doctorate/mosaics_ndfia_adjusted/'+ test.toString();
    var region = geometry2
    
    Export.image.toAsset({
        image: img.toInt16(),
        description: test.toString(),
        assetId: id,
        region: region,
        scale: 30,
        maxPixels: 1e13,
        pyramidingPolicy: 'MODE'
    })
}





























//var exportar = function(img){
//  var name = img.get('year')
//  var option = {
//    image: img,
//    description: name,
//    assetId:'users/diegocosta/doctorate/arizona/mosaic_ndfia_fitted'+ name.toString(),
//    region: geometry2,   
//    scale: 30,
//    maxPixels:1e13
//  };
//
//  Export.image.toAsset(option);
//}

//var exportar = TIME_SEQUENCE.map(exportar)
//
//var asset = 'TEST'
//var options = {
//    name: TIME_SEQUENCE.get('year'),
//    scale: 30,
//    maxPixels: 1e13,
//    region: geometry2
//}
//
//batch.Download.ImageCollection.toAsset(TIME_SEQUENCE, asset, options)
