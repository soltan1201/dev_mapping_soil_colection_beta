// https://code.earthengine.google.com/23926c11d1fc362ac46df690d1c4acff

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
    }
} ;


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
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
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
var asset_pathOutput = 'users/lazarobritoagro/degradacao';
var region_selected = 60;
var yyear = 1988;
var bioma_select = 'PANTANAL';
var windowsYear = janelasAnos(yyear, true);
var regionss = ee.FeatureCollection(param.regions).filter(
                  ee.Filter.eq('region', region_selected));
var regioes = regionss.geometry();
var gradeLandsat = ee.FeatureCollection(param.gradeLandsat).filterBounds(regioes);
var mapbiomas = ee.Image(param.inputAsset).select('classification_2021');
//Duna 23, Urbano 24, Mining 30
var maskEscluir = mapbiomas.eq(23).add(mapbiomas.eq(24)).add(mapbiomas.eq(30)).eq(0);
var areaMap = mapbiomas.remap(param.classMapB, param.classNew).selfMask();
var mapsSoils = ee.ImageCollection(param.class_solo)
                      .filter(ee.Filter.eq("region", region_selected.toString()))
                      .filter(ee.Filter.eq('year', yyear))
                      .first();
                      
// mapsSoils = mapsSoils.updateMask(maskEscluir).clip(regioes);
print("mapas de solo ", mapsSoils);
var mosaicHarms = ee.ImageCollection(param.asset_mosaic).filterBounds(regioes)
                            .filter(ee.Filter.inList('year', windowsYear));
                            
                    // .filter(ee.Filter.eq('biome', bioma_select));
print("mosaic harmonicos ", mosaicHarms);
mosaicHarms = mosaicHarms.map(ApplyReducers);

var Mosaicos = ee.ImageCollection(param.assetIm)
                    .filter(ee.Filter.eq('biome', bioma_select))
                    .filter(ee.Filter.eq('year', yyear))
                    .select(param.bandas).median().clip(regioes);    
print("Show mosaic Mapbiomas ", Mosaicos);

Map.addLayer(Mosaicos, visualizar.visMosaic,'Mosaic Col8', false);
windowsYear.forEach(function(myear){
    print();
    var mosaicHarmsYear = mosaicHarms.filter(ee.Filter.eq('year', myear)).mosaic().clip(regioes);
    print(" mosaicHarmsYear");
    if (myear === yyear){
        Map.addLayer(mosaicHarmsYear, visualizar.mosaic, 'MosaicHarm ' + myear.toString() + '_A');
    }else{
        Map.addLayer(mosaicHarmsYear, visualizar.mosaic, 'MosaicHarm ' + myear.toString(), false);
    }
})

Map.addLayer(mapbiomas, visualizar.visclassCC, "Mapbiomas Col7.1" , false);
Map.addLayer(mapsSoils.selfMask(), visualizar.reviewer, "mapSoil_" + yyear.toString());
var maskEsc = mapbiomas.eq(23).add(mapbiomas.eq(24)).add(mapbiomas.eq(30)).gt(0)
Map.addLayer(maskEsc.selfMask(),{min:0, max:1, palette: '000000, 00ffbb'}, 'AreaExcluir');
var gradeL8 = ee.Image().byte().paint({
  featureCollection: gradeLandsat,  color: 1,  width: 1.5});

Map.addLayer(gradeL8, {color: 'fec44f'}, "grade Mapping", false);
Map.addLayer(gradeLandsat, {color: 'fec44f'}, "grade real", false);

var regions = ee.Image().byte().paint({
  featureCollection: regionss,  color: 1,  width: 1.5});
Map.addLayer(regions, {color: 'ff004a'}, "regions", false);

var shpExport = ee.FeatureCollection(falsoPostivo).merge(Omisao_Soil);
var nameExp = 'shp_' + bioma_select + "_" + yyear.toString() + "_" + region_selected.toString();
processoExportar(shpExport, nameExp, asset_pathOutput);