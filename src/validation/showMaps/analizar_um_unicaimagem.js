var visualizar = {
    'visMosaic': {
        min: 0.01,
        max: 0.5,
        bands: ['B4', 'B3', 'B2']
    },
    'mosaicoH': {
        min:3622, 
        max:18000,
        palette: 'ff7b00,ffaa00,ffdd00,ffea00,ffff3f,eeef20,dddf00,'+
                 'd4d700,bfd200,aacc00,80b918,55a630,2b9348,007f5f'
    }
} ;

var path = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico/fitted_image_CERRADO_2021_218_71';
var imgTeste = ee.Image(path)
print("know the bands ", imgTeste)

var bandJan = 'LC08_218071_20210103';
var bandJul = "LC08_218071_20210714";
var bandNov ="LC08_218071_20211205";

var imgJan = imgTeste.select(bandJan);
var imgJul = imgTeste.select(bandJul);
var imgNov = imgTeste.select(bandNov);

var imgL8Jan = ee.Image('LANDSAT/LC08/C02/T1_TOA/' + bandJan);
var imgL8Jul = ee.Image('LANDSAT/LC08/C02/T1_TOA/' + bandJul);
var imgL8nov = ee.Image('LANDSAT/LC08/C02/T1_TOA/' + bandNov);

Map.addLayer(imgL8Jan,visualizar.visMosaic, 'L8 Jan');
Map.addLayer(imgJan, visualizar.mosaicoH, "NDFIa Jan");
Map.addLayer(imgL8Jul,visualizar.visMosaic, 'L8 Jul');
Map.addLayer(imgJul, visualizar.mosaicoH, "NDFIa Jul");
Map.addLayer(imgL8nov,visualizar.visMosaic, 'L8 Out');
Map.addLayer(imgNov, visualizar.mosaicoH, "NDFIa Out");