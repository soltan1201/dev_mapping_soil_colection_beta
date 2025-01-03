// Display the masked result.
var palette_color_index = 
    'FFFFFF,FFFCFF,FFF9FF,FFF7FF,FFF4FF,FFF2FF,FFEFFF,FFECFF,FFEAFF,FFE7FF,FFE5FF,FFE2FF,FFE0FF,'+
    'FFDDFF,FFDAFF,FFD8FF,FFD5FF,FFD3FF,FFD0FF,FFCEFF,FFCBFF,FFC8FF,FFC6FF,FFC3FF,FFC1FF,FFBEFF,'+
    'BCFF,FFB9FF,FFB6FF,FFB4FF,FFB1FF,FFAFFF,FFACFF,FFAAFF,FFA7FF,FFA4FF,FFA2FF,FF9FFF,FF9DFF,'+
    'FF9AFF,FF97FF,FF95FF,FF92FF,FF90FF,FF8DFF,FF8BFF,FF88FF,FF85FF,FF83FF,FF80FF,FF7EFF,FF7BFF,'+
    'FF6EFF,FF6CFF,FF69FF,FF67FF,FF79FF,FF76FF,FF73FF,FF71FF,FF64FF,FF61FF,FF5FFF,FF5CFF,FF5AFF,'+
    'FF57FF,FF55FF,FF52FF,FF4FFF,FF4DFF,FF4AFF,FF48FF,FF45FF,FF42FF,FF40FF,FF3DFF,FF3BFF,FF38FF,'+
    'FF36FF,FF33FF,FF30FF,FF2EFF,FF2BFF,FF29FF,FF26FF,FF24FF,FF21FF,FF1EFF,FF1CFF,FF19FF,FF17FF,'+
    'FF14FF,FF12FF,FF0FFF,FF0CFF,FF0AFF,FF07FF,FF05FF,FF02FF,FF00FF,FF00FF,FF0AF4,FF15E9,FF1FDF,'+
    'FF2AD4,FF35C9,FF3FBF,FF4AB4,FF55AA,FF5F9F,FF6A94,FF748A,FF7F7F,FF8A74,FF946A,FF9F5F,FFAA55,'+
    'FFB44A,FFBF3F,FFC935,FFD42A,FFDF1F,FFE915,FFF40A,FFFF00,FFFF00,FFFB00,FFF700,FFF300,FFF000,'+
    'FFEC00,FFE800,FFE400,FFE100,FFDD00,FFD900,FFD500,FFD200,FFCE00,FFCA00,FFC600,FFC300,FFBF00,'+
    'FFBB00,FFB700,FFB400,FFB000,FFAC00,FFA800,FFA500,FFA500,F7A400,F0A300,E8A200,E1A200,D9A100,'+
    'D2A000,CA9F00,C39F00,BB9E00,B49D00,AC9C00,A59C00,9D9B00,969A00,8E9900,879900,7F9800,789700,'+
    '709700,699600,619500,5A9400,529400,4B9300,439200,349100,2D9000,258F00,1E8E00,168E00,0F8D00,'+
    '078C00,008C00,008C00,008700,008300,007F00,007A00,007600,007200,006E00,006900,006500,006100,'+
    '005C00,005800,005400,005000,004C00'
var vizParams = {
    'ndfia': {min: 0, max: 20000, palette: palette_color_index},
    'mosaico': {min:0, max: 0.3, bands: ['B3', 'B2', 'B1']},
    'mosaic_proc': {min:0, max: 0.3, bands: ['Red', 'Green', 'Blue']}, // , ,   
    'mosaic_p': {min:0, max: 0.4, bands: ['red', 'green', 'blue']} // , ,  
};
var coefficients = {
    itcps: ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]).multiply(10000),
    slopes: ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
};
// Function to get and rename bands of interest from OLI.
function renameOli(img) {
    return img.select(
        ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'QA_PIXEL'],
        ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']);
}

// Function to get and rename bands of interest from ETM+.
function renameEtm(img) {
    return img.select(
        ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL'],
        ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']);
}

function fmask(img) {
    var cloudShadowBitMask = 1 << 3;
    var cloudsBitMask = 1 << 5;
    var qa = img.select('QA_PIXEL');
    var mask = qa.bitwiseAnd(cloudShadowBitMask)
                  .eq(0)
                  .and(qa.bitwiseAnd(cloudsBitMask).eq(0));
    return img.updateMask(mask);
}
function etmToOli(img) {
    return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'])
        .multiply(coefficients.slopes)
        .add(coefficients.itcps)
        .round()
        .toShort()
        .addBands(img.select('QA_PIXEL'));
}

// Define function to prepare OLI images.
function prepOli(img) {
    var orig = img;
    img = renameOli(img);
    img = fmask(img);
    img = calcNbr(img);
    return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}

// Define function to prepare ETM+ images.
function prepEtm(img) {
    var orig = img;
    img = renameEtm(img);
    img = fmask(img);
    // img = etmToOli(img);
    // img = calcNbr(img);
    return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}

  
var asset_geom = 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2'
// var asset = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico/index_ndfia_CAATINGA_198512_214_64'
var asset = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico/index_ndfia_CAATINGA_199812_214_65'
var imgNDFIa = ee.Image(asset);
print("imagens NDFIa ", imgNDFIa);

var geomFF = ee.FeatureCollection(asset_geom)
                  .filter(ee.Filter.eq('PATH', 214))
                  .filter(ee.Filter.eq('ROW', 65));
print (" geometria orbita ", geomFF);

var imgCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA')
                  .filterBounds(geomFF.geometry().centroid())
                  .filterDate('1998-01-01', '1998-12-31');
                  
print(imgCol)


Map.addLayer(geomFF, {color: 'green'}, 'geom', false);
// Map.addLayer(imgCol, vizParams.mosaico, 'imgCol')
var imgColN = imgCol.map(prepEtm)
Map.addLayer(imgColN, vizParams.mosaic_proc, 'imgCol Prep')
var lstBand = imgNDFIa.bandNames().getInfo();
lstBand.forEach(function(nameBnd){
    Map.addLayer(imgNDFIa.select(nameBnd), vizParams.ndfia, 'NDFIa ' + nameBnd);
})


// Map.centerObject(geomFF, 13)