var paletaNDFI = 
'ffffff,fffcff,fff9ff,fff7ff,fff4ff,fff2ff,ffefff,ffecff,ffeaff,ffe7ff,' +
'ffe5ff,ffe2ff,ffe0ff,ffddff,ffdaff,ffd8ff,ffd5ff,ffd3ff,ffd0ff,ffceff,' +
'ffcbff,ffc8ff,ffc6ff,ffc3ff,ffc1ff,ffbeff,ffbcff,ffb9ff,ffb6ff,ffb4ff,' +
'ffb1ff,ffafff,ffacff,ffaaff,ffa7ff,ffa4ff,ffa2ff,ff9fff,ff9dff,ff9aff,' +
'ff97ff,ff95ff,ff92ff,ff90ff,ff8dff,ff8bff,ff88ff,ff85ff,ff83ff,ff80ff,' +
'ff7eff,ff7bff,ff79ff,ff76ff,ff73ff,ff71ff,ff6eff,ff6cff,ff69ff,ff67ff,' +
'ff64ff,ff61ff,ff5fff,ff5cff,ff5aff,ff57ff,ff55ff,ff52ff,ff4fff,ff4dff,' +
'ff4aff,ff48ff,ff45ff,ff42ff,ff40ff,ff3dff,ff3bff,ff38ff,ff36ff,ff33ff,' +
'ff30ff,ff2eff,ff2bff,ff29ff,ff26ff,ff24ff,ff21ff,ff1eff,ff1cff,ff19ff,' +
'ff17ff,ff14ff,ff12ff,ff0fff,ff0cff,ff0aff,ff07ff,ff05ff,ff02ff,ff00ff,' +
'ff00ff,ff0af4,ff15e9,ff1fdf,ff2ad4,ff35c9,ff3fbf,ff4ab4,ff55aa,ff5f9f,' +
'ff6a94,ff748a,ff7f7f,ff8a74,ff946a,ff9f5f,ffaa55,ffb44a,ffbf3f,ffc935,' +
'ffd42a,ffdf1f,ffe915,fff40a,ffff00,ffff00,fffb00,fff700,fff300,fff000,' +
'ffec00,ffe800,ffe400,ffe100,ffdd00,ffd900,ffd500,ffd200,ffce00,ffca00,' +
'ffc600,ffc300,ffbf00,ffbb00,ffb700,ffb400,ffb000,ffac00,ffa800,ffa500,' +
'ffa500,f7a400,f0a300,e8a200,e1a200,d9a100,d2a000,ca9f00,c39f00,bb9e00,' +
'b49d00,ac9c00,a59c00,9d9b00,969a00,8e9900,879900,7f9800,789700,709700,' +
'699600,619500,5a9400,529400,4b9300,439200,349100,2d9000,258f00,1e8e00,' +
'168e00,0f8d00,078c00,008c00,008c00,008700,008300,007f00,007a00,007600,' +
'007200,006e00,006900,006500,006100,005c00,005800,005400,005000,004c00';
var paramVis = {
    mosaicoGEE: {
        bands: ["red","green","blue"],
        gamma: 1,
        max: 2000,
        min: 5
    },
    indiceNDFI:{
        min: 1000, 
        max: 10000,
        palette: paletaNDFI
    },
    vigor_pasto: {
        min: 1, 
        max: 3,
        palette: ['#f06a6d', '#f3b276', '#61ad55']
    },
    soil_maps: {
        min:0, max: 1, 
        palette: ['#C01313FF']
    },
    sample_area_notSoil: {
        min:0, max: 1, 
        palette: ['#E59B11FF']
    },
    sample_area_soil: {
        min:0, max: 1, 
        palette: ['#F04806FF']
    }
}
var trueColor432Vis = {
    min: 0.0,
    max: 0.4,
  };
  
  
  var params = {
        'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
        'assetMapbiomas90': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',  
        "asset_vigor_pastagem": 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_pasture_vigor_v1',
        'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
        'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
        'input_solo': 'users/diegocosta/doctorate/Bare_Soils_Caatinga',
        'regionsSel': [21,31,32],
        'harmonics': 2,  
        'dates':{
            '0': '-01-01',
            '1': '-12-31'
        },    
        'bnd_LG': ['blue','green','red','nir','swir1','swir2','pixel_qa'],
        'bnd_QA': ['blue','green','red','nir','swir1','swir2','QA_PIXEL', 'QA_RADSAT'],
        'bnd_L': ['blue','green','red','nir','swir1','swir2'], 
        'WRS_PATH': null,
        'WRS_ROW' : null,
        'initYear': 1985,
        'endYear': 2023,
        'dependent': 'NDFIa',
        'harmonics': 2,
        'dateInit': '1987-01-01', 
        'lstYear': [
            1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 
            1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
            2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
        ]  
};

// 4. Calcule o índice NDVI
function index_select(nImg, reescalar){
    // var nImg = applyScaleFactors(image);
    var ndvi = nImg.normalizedDifference(['nir', 'red']).rename('NDVI');
    ndvi = ndvi.add(1).multiply(10000).toUint16();
    var ndsi = nImg.normalizedDifference(['swir1', 'nir']).rename('NDSI');
    ndsi = ndsi.add(1).multiply(10000).toUint16();
    var bsi = nImg.expression(
                "float(((b('red') + b('swir1')) - (b('nir') + b('blue'))) / ((b('red') + b('swir1')) + (b('nir') + b('blue'))))"
            ).rename('BSI');
    bsi = bsi.add(1).multiply(10000).toUint16();
    var evi = nImg.expression(
                "float(2.4 * (b('nir') - b('red')) / (1 + b('nir') + b('red')))"
                ).rename('evi');
    evi = evi.add(10).multiply(1000).toUint16();
    var imgM = nImg;
    if(reescalar){
        var imgM = nImg.multiply(10000);
    }
    return imgM.addBands(ndvi).addBands(evi).addBands(ndsi).addBands(bsi).toUint16().copyProperties(nImg);
}

function GET_NDFIA_mosaic(IMAGE) {
        
    var lstBands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];
    var lstFractions = ['GV', 'SHADE', 'NPV', 'SOIL', 'CLOUD'];
    var endmembers = [            
        [0.05, 0.09, 0.04, 0.61, 0.30, 0.10], /*gv*/
        [0.14, 0.17, 0.22, 0.30, 0.55, 0.30], /*npv*/
        [0.20, 0.30, 0.34, 0.58, 0.60, 0.58], /*soil*/
        [0.0 , 0.0,  0.0 , 0.0 , 0.0 , 0.0 ], /*Shade*/
        [0.90, 0.96, 0.80, 0.78, 0.72, 0.65]  /*cloud*/ 
    ];

    var fractions = ee.Image(IMAGE).select(lstBands).unmix(endmembers, true, true);
    fractions = fractions.rename(lstFractions);
    // print(UNMIXED_IMAGE);
    var NDFI_ADJUSTED = fractions.expression(
                            "float( ((b('GV') / (1 - b('SHADE'))) - b('SOIL')) / ((b('GV') / (1 - b('SHADE'))) + (b('NPV')) + b('SOIL')) )"
                          ).rename('NDFIa')

    NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()
    var RESULT_IMAGE = ee.Image(index_select(IMAGE, true))
                                .addBands(fractions.multiply(10000).toUint16())
                                .addBands(NDFI_ADJUSTED);

    return ee.Image(RESULT_IMAGE).toUint16()

}


var yyear = 2020;
var mmonth = 1;

var bandasInt = ['blue', 'red', 'nir', 'swir1', 'NDVI', 'NDSI', 'BSI', 'GV', 'SHADE', 'SOIL', 'NDFIa', 'class'];
var regionSelect = 31;
var regionSel = ee.FeatureCollection(params.region).filter(ee.Filter.eq('region', regionSelect));
print("regions selecionadas ", regionSel);
var imgMaskReg = regionSel.reduceToImage(['region'], ee.Reducer.first()).gt(1);

var data_inicial = ee.Date.fromYMD(yyear, mmonth, 1);
var mosaicMensal =  ee.ImageCollection(params.asset_collectionId)
                        .filterBounds(regionSel.geometry())
                        .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                        .select(params.bnd_L).first()
                        .updateMask(imgMaskReg);
mosaicMensal = GET_NDFIA_mosaic(mosaicMensal);
print(" mmosaico Mensal Landsat ", mosaicMensal);
var lstBands = ['classification_2015', 'classification_2016','classification_2017'];
var lstBandsVigor = ['vigor_2015', 'vigor_2016','vigor_2017'];
var lstBNDSoil = [
    'Caatinga_2015_classification_2015', 
    'Caatinga_2016_classification_2016', 
    'Caatinga_2017_classification_2017'
];
print("primeira banda ", lstBands[0]);
var mMapbiomas = ee.Image(params.assetMapbiomas90).updateMask(imgMaskReg);
print(mMapbiomas);
var maskYYSoil = mMapbiomas.select(lstBands).eq(25);
maskYYSoil = maskYYSoil.reduce(ee.Reducer.sum()).eq(3);

var layer_soil = ee.Image(params.input_solo).select(lstBNDSoil)
                        .reduce(ee.Reducer.sum()).eq(3);
print("show layer soil ", layer_soil);
var map_past_vigor = ee.Image(params.asset_vigor_pastagem).gt(1).select(lstBandsVigor)
                            .reduce(ee.Reducer.sum()).eq(3);
print("show layer vigor da pastagem ", map_past_vigor);

var interval_min = 9000;
var int_max = 10500;
var areas_col_notSoil = mosaicMensal.select('NDFIa').lte(int_max).and(mosaicMensal.select('NDFIa').gte(interval_min));
var feixao = 6500;
var areas_col_soil = mosaicMensal.select('NDFIa').lte(feixao);

// Paint all the polygon edges with the same number and width, display.
var outlineReg = ee.Image().byte().paint({featureCollection: regionSel, color: 1, width: 3});
Map.addLayer(outlineReg, {palette: 'FF0000'}, 'Regions');

Map.addLayer(mosaicMensal, paramVis.mosaicoGEE, 'mosaico Mensal GEE');
Map.addLayer(mosaicMensal.select('NDFIa'), paramVis.indiceNDFI, 'ndfia GEE');
// Map.addLayer(map_past_vigor.selfMask(), paramVis.vigor_pasto, 'Vigor_pastagem');
Map.addLayer(areas_col_notSoil.selfMask(), paramVis.sample_area_notSoil, 'samples areas notSoil');
Map.addLayer(areas_col_soil.selfMask(), paramVis.sample_area_soil, 'samples areas Soil');
Map.addLayer(maskYYSoil.selfMask(), paramVis.soil_maps, 'maps Soil');
