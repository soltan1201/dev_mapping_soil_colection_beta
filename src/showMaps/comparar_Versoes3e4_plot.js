
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
    'probabilistic': {  
        'min': 0, 'max': 1,
        'palette': 'c18078,a2645d,5f2f24,4b231b,361712'
    },
    'soilv4': {  
        'min': 0, 'max': 1,
        'palette': 'f55435'
    },
    'mosaicoH': {
        min:5000, 
        max:15000,
        bands: ['median','min','max']
    }
} ;

function plotTemperature(imCol){
    var myGeom = ee.Geometry.Point([-42.35976, -15.36177])
    //Charts Long Term Time Series
    var chartOC = Chart.image.series(imCol, myGeom,  ee.Reducer.mean(), 1000,
          'system:time_start').setOptions({
            title: 'Série de ',
            hAxis: {title: 'Tempo (dia, mês, ano)'},
            vAxis: {title: 'valor NDFIa'},
    });
    print('Série  ' , chartOC);
}


//exporta a imagem classificada para o asset
var processoExportar = function (ROIsFeat, nameB, idAssetF){

    var assetId = idAssetF + '/' + nameB;
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetId         
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!");
};

var janelasAnos = function (ano, printar){
    var lsAnos = [
          1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 
          1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
          2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022
        ];
    var sizeSerie = lsAnos.length;
    var janela = [];
    var index = lsAnos.indexOf(ano);
    print("index ", index)
    if (ano - 1985 < 2){
        print("INICIO DA SERIE");
        janela = lsAnos.slice(0, 5);
    }else{
        if (2022 - ano < 3){
            print(" FINAL DA SERIE  ")
            janela = lsAnos.slice(sizeSerie - 5, sizeSerie);
        }else{
            janela = lsAnos.slice(index - 2, index + 3);
        }
    }
    if (printar === true){
            print(' ==> ', janela)}
    
    return janela;
};
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
    'classmappingV2': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV2',  // vacio
    'classmappingV3': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3',
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'asset_biomas_raster': 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  : [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
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
var dictNomeBiome = {
    'Amazônia': 'AMAZONIA', 
    'Cerrado': 'CERRADO',
    'Caatinga': 'CAATINGA',
    'Mata Atlântica': 'MATA_ATLANTICA', 
    'Pampa': 'PAMPA',
    'Pantanal': 'PANTANAL' 
};
var dictRegions = {
    "Pampa": ['51','52','53'],
    "Cerrado": ['31','32','35','34','33'],
    'Caatinga': ['21','22','23','24'],
    "Pantanal": ['60'],
    'Amazônia': ['11','12','13','14','15','16','17','18','19'],
    "Mata Atlântica":['41','42','44','45','46','47']
};

var region_selected = 60;
var yyear = 1985;
var bioma_select = 'CERRADO';
var biomesBase = ee.Image(param.asset_biomas_raster).gt(0);
var regionss = ee.FeatureCollection(param.regions);
print("loading Regions " + region_selected.toString() + " from " + bioma_select);
var regioes = regionss.geometry();
var gradeLandsat = ee.FeatureCollection(param.gradeLandsat).filterBounds(regioes);
var mapbiomas = ee.Image(param.inputAsset).select('classification_' + yyear.toString());
// camada de solo de mapbiomas  
var mapBiomasSolo = mapbiomas.eq(22);
// preparing layers to delete
//Duna 23, Urbano 24, Mining 30
var areasIntMapb = mapbiomas.remap(param.classMapB, param.classNew);
var maskExcluir = areasIntMapb.eq(1);
var maskAgrop = areasIntMapb.eq(2);

// plotTemperature
var mapsSoilV3 = ee.ImageCollection(param.classmappingV3)
                      .filter(ee.Filter.eq('year', yyear))
                      .filter(ee.Filter.eq('biome', bioma_select))



mapsSoilV3 = mapsSoilV3.map(function(img){return img.eq(1).rename('classification_' + String(yyear));})
print("Show image Collection from V3 mapSoil ", mapsSoilV3);
mapsSoilV3 = mapsSoilV3.max().updateMask(biomesBase);

var mapsSoilV4 = ee.ImageCollection(param.classmappingV4)
                      .filter(ee.Filter.eq('year', yyear))
                      .filter(ee.Filter.eq('biome', bioma_select))
mapsSoilV4 = mapsSoilV4.max().updateMask(biomesBase);
// Lodaing layer mosaics
var mosaicHarms = ee.ImageCollection(param.asset_mosaic)                                                       
                            .filter(ee.Filter.eq('biome', bioma_select));
print("mosaic harmonicos ", mosaicHarms);
plotTemperature(mosaicHarms);

var mosaicHarmsred = mosaicHarms.filter(ee.Filter.eq('year', yyear)) .map(ApplyReducers);

var Mosaicos = ee.ImageCollection(param.assetIm)
                    .filter(ee.Filter.eq('year', yyear))
                    .select(param.bandas).median()  
print("Show mosaic Mapbiomas ", Mosaicos);

Map.addLayer(Mosaicos, visualizar.visMosaic,'Mosaic Col8', false);
Map.addLayer(mosaicHarmsred, visualizar.mosaicoH, 'MosaicHarm ' + yyear.toString() + '_A', false);
Map.addLayer(mapbiomas, visualizar.visclassCC, "Mapbiomas Col7.1" , false);
Map.addLayer(mapsSoilV3.selfMask(), visualizar.reviewer, "mapSoilV3_" + yyear.toString());
Map.addLayer(mapsSoilV4, visualizar.probabilistic, "mapSoilV4_" + yyear.toString(), false);
Map.addLayer(mapsSoilV4.gt(0.84).selfMask(), visualizar.soilv4, "cut_mapSoilV4_" + yyear.toString(), false);
var maskEsc = mapbiomas.eq(23).add(mapbiomas.eq(24)).add(mapbiomas.eq(30)).gt(0)
Map.addLayer(maskEsc.selfMask(),{min:0, max:1, palette: '000000, 00ffbb'}, 'AreaExcluir', false);
Map.addLayer(mapBiomasSolo.selfMask(), {min:0, max: 1, palette: '000000, ff00bb'}, "Solos Mapbiomas")
// 


// Map.addLayer(gradeL8, {color: 'fec44f'}, "grade Mapping", false);
// Map.addLayer(gradeLandsat, {color: 'fec44f'}, "grade real", false);

// var regions = ee.Image().byte().paint({
//   featureCollection: regionss,  color: 1,  width: 1.5});
// Map.addLayer(regions, {color: 'ff004a'}, "regions", false);
