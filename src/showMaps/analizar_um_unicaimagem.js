var visualizar = {
    'visMosaic': {
        min: 0.01,
        max: 0.35,
        bands: ['B4', 'B3', 'B2']
    },
    'mosaicoH': {
        min:3622, 
        max:20000,
        palette: 'ff7b00,ffaa00,ffdd00,ffea00,ffff3f,eeef20,dddf00,'+
                 'd4d700,bfd200,aacc00,80b918,55a630,2b9348,007f5f'
    }
} ;

// Applies scaling factors.
function applyScaleFactors(image) {
    var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
    var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
    return image.addBands(opticalBands, null, true)
                .addBands(thermalBands, null, true);
};

// Función para aplicar la máscara de nubes y sombras de nubes usando QA_PIXEL
var maskClouds = function(image) {
    var cloudBitMask = (1 << 3);     // Bit 3 para sombra de nubes
    var cloudShadowBitMask = (1 << 5); // Bit 5 para nubes
    // Selecciona la banda QA_PIXEL y aplica la máscara
    var qa = image.select('QA_PIXEL');
    var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
                .and(qa.bitwiseAnd(cloudShadowBitMask).eq(0));

    return image.updateMask(mask);
};

  

var path = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico/fitted_image_CERRADO_2021_218_71';
var imgTeste = ee.Image(path)
print("know the bands ", imgTeste)

var bandJan = 'LC08_218071_20210103';
var bandJul = "LC08_218071_20210714";
var bandNov ="LC08_218071_20211205";

var imgJan = imgTeste.select(bandJan);
var imgJul = imgTeste.select(bandJul);
var imgNov = imgTeste.select(bandNov);
var aseetLandsat = "LANDSAT/LC08/C02/T1_RT_TOA"
// var ImgCol = ee.ImageCollection(aseetLandsat)
//                   .filterDate('2021-01-01', '2021-12-31')
//                   .filterBounds(point);
// print(ImgCol)

var imgL8Jan = maskClouds(ee.Image(aseetLandsat + '/' + bandJan));
var imgL8Jul = maskClouds(ee.Image(aseetLandsat + '/' + bandJul));
var imgL8nov = maskClouds(ee.Image(aseetLandsat + '/' + bandNov));



Map.addLayer(imgL8Jan,visualizar.visMosaic, 'L8 Jan');
Map.addLayer(imgJan, visualizar.mosaicoH, "NDFIa Jan");
Map.addLayer(imgL8Jul,visualizar.visMosaic, 'L8 Jul');
Map.addLayer(imgJul, visualizar.mosaicoH, "NDFIa Jul");
Map.addLayer(imgL8nov,visualizar.visMosaic, 'L8 Out');
Map.addLayer(imgNov, visualizar.mosaicoH, "NDFIa Out");