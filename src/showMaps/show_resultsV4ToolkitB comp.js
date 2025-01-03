//https://code.earthengine.google.com/ec031c9c6753d13df1c545eed1aea111
var palettes = require('users/mapbiomas/modules:Palettes.js');
var visualizar = {
    'visclassCC': {
            "min": 0, 
            "max": 62,
            "palette":  palettes.get('classification9'),
            "format": "png"
    },
    'visMosaic': {
        min: 0,
        max: 2000,
        bands: ['red_median', 'green_median', 'blue_median']
    },
    'reviewer': {  
        'min': 0, 'max': 1,
        'palette': 'FFFFFF, 8C2D04'
    },
    'soilV2': {  
        'min': 0, 'max': 2,
        'palette': 'FFFFFF, 8b4513, a0522d'
    },
    'soilVBase': {  
        'min': 0, 'max': 1,
        'palette': 'FFFFFF, f4a460'
    },
    'mosaic': {
        min:5000, 
        max:15000,
        bands: ['median','min','max']
    },
    'excluir': {
        min: 0, 
        max: 1, 
        palette: '000000, 00ffbb'
    },
    'agropecuaria' : {
        min: 0, 
        max: 1, 
        palette: '000000,cd49e4'
    },
    'floresta' : {
        min: 0, 
        max: 1, 
        palette: '000000,32a65e'
    },
    'areaNVeg': {
        min: 0, 
        max: 1, 
        palette: '000000,ffaa5f'
    }
} ;

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
};


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
    'gv':    [0.05, 0.09, 0.04, 0.61, 0.30, 0.10],
    'npv':   [0.14, 0.17, 0.22, 0.30, 0.55, 0.30],
    'soil':  [0.20, 0.30, 0.34, 0.58, 0.60, 0.58],
    'shade': [0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 0.0 ],
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
        }).rename('NDFIa');

        NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16();
        var RESULT_IMAGE = UNMIXED_IMAGE.addBands(NDFI_ADJUSTED);

        return ee.Image(RESULT_IMAGE).select('NDFIa');
    })
}

var pointCenter = ee.Geometry.Point([-45.92222, -14.87282]);
function get_collection_NDFIa(myPoint){
    var TIME_SEQUENCE = ee.List.sequence(1985, 2023).getInfo();
    var allCollection = ee.ImageCollection([]);
    TIME_SEQUENCE.forEach(
                        function(YEAR) {
                            // YEAR = ee.Number(YEAR);
                            print("year " + YEAR)
                            var BEFORE_DATE = ee.Date.fromYMD(YEAR, 1, 1);
                            var AFTER_DATE = ee.Date.fromYMD(YEAR, 12, 31);
                            var COLECTION_L8 = ee.ImageCollection(GENERAL_PARAMS.COL_L8)
                                    .filterBounds(myPoint)
                                    .filterDate(BEFORE_DATE, AFTER_DATE)
                                    .filter(ee.Filter.lte('CLOUD_COVER', 70))
                                    .map(MASK_L8SR)

                            var COLECTION_L7 = ee.ImageCollection(GENERAL_PARAMS.COL_L7)
                                    .filterBounds(myPoint)
                                    .filterDate(BEFORE_DATE, AFTER_DATE)
                                    .filter(ee.Filter.lte('CLOUD_COVER', 80))
                                    .map(MASK_L457SR)

                            var COLECTION_L5 = ee.ImageCollection(GENERAL_PARAMS.COL_L5)
                                    .filterBounds(myPoint)
                                    .filterDate(BEFORE_DATE, AFTER_DATE)
                                    .filter(ee.Filter.lte('CLOUD_COVER', 80))
                                    .map(MASK_L457SR);

                            var COLLECTION = COLECTION_L8.merge(COLECTION_L5)//
                            // COLLECTION = ee.ImageCollection(GET_NDFIA(COLLECTION, INDEX_PARAMS));
                            allCollection = allCollection.merge(COLLECTION);
                        })

    // TIME_SEQUENCE = TIME_SEQUENCE.flatten();   
    print("know time sequence of Landsat ", allCollection);          

    allCollection = GET_NDFIA(allCollection, INDEX_PARAMS);
    print("know index on allCollection ", allCollection);

    return allCollection;
}

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
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'asset_biomas_raster': 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'inputAsset': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'classMapB' :   [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  :   [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
    'classFlorest': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_mosaic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2', 
    'bandas': ['red_median', 'green_median', 'blue_median'], 
    'lstBiomes' : ['Amazônia', 'Cerrado', 'Caatinga', 'Mata Atlântica', 'Pampa', 'Pantanal']
};
var dictNameBiome = {
    'Amazônia': 'AMAZONIA', 
    'Cerrado': 'CERRADO',
    'Caatinga': 'CAATINGA',
    'Mata Atlântica': 'MATAATLANTICA', 
    'Pampa': 'PAMPA',
    'Pantanal': 'PANTANAL'
};
var dictNameBiomes = {
    'Amazônia': 'AMAZONIA', 
    'Cerrado': 'CERRADO',
    'Caatinga': 'CAATINGA',
    'Mata Atlântica': 'MATA_ATLANTICA', 
    'Pampa': 'PAMPA',
    'Pantanal': 'PANTANAL'
};
var dict_raster = {
    'Amazônia': 1, 
    'Cerrado': 4,
    'Caatinga': 5,
    'Mata Atlântica': 2, 
    'Pampa': 6,
    'Pantanal': 3
}
var dictRegions = {
    "Pampa": ['51','52','53'],
    "Cerrado": ['31','32','35','34','33'],
    'Caatinga': ['21','22','23','24'],
    "Pantanal": ['60'],
    'Amazônia': ['11','12','13','14','15','16','17','18','19'],
    "Mata Atlântica":['41','42','44','45','46','47']
};

var MapMosaicL = null;
var MapMosaicD = null;
var MapMosHarmL = null;
var MapMosHarmD = null;
var MapCol90 = null;
// var MapFloresta = null;
var MapMaskAreaNVeg = null;
var MapSoilBase = null;
var MapSoilV4 = null;
var MaptoExc = null;
var MaptoAgr = null;
var MapRegs = null;
// https://code.earthengine.google.com/f428edf837b2d10b5d78157e0225d113

var yyear = 2005;
var bioma_select = 'Cerrado';
var visMosaic = true;

var lsAnos = ee.List([
    "1985", "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", 
    "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012",
    "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"
  ]);
 
var colectionYears = lsAnos.map(function(yyear){
                return ee.Feature(null, {'year': yyear,  'system_yValue': 0});
      });  
colectionYears = ee.FeatureCollection(colectionYears); //.map(function(feat){ return feat.set('system:yearValue', feat.id())});
print(" feature ", colectionYears);

var regionss = ee.FeatureCollection(param['regions']);     
var mapbiomasCol9 = ee.Image(param.inputAsset);
var mapsSoilsV4 = ee.ImageCollection(param.classmappingV4); // camada de base 

var mosaicHarms = ee.ImageCollection(param.asset_mosaic)//.map(function(img){return img.rename('class')});
print("show mosaic harmonicos the first 5 ", mosaicHarms.limit(5));
print(mosaicHarms.aggregate_histogram('biome'));
print(mosaicHarms.aggregate_histogram('year'));

var Mosaicos = ee.ImageCollection(param.assetIm).select(param.bandas);    
print("Show mosaic Mapbiomas the first 5 ", Mosaicos.limit(5));

var raster_biome = ee.Image(param['asset_biomas_raster'])

var pstyle ={
    mapleft : {
                style: {
                    border: '2px solid black'
                }
            },
    mapright: {
                style: {
                    stretch: 'both',
                    border: '2px solid black'
                }
            },
    barrayear: {
                position: 'bottom-center',
                width: '100%',
                height: '60px',
                margin: '0px',
                padding: '0px',
            },
    stretchp: {
                stretch: 'both'
            },
    selector: {
                position: 'bottom-center',
                width: '30%',
                height: '80px',
                margin: '0px',
                padding: '0px',
            },
    panel_head: {
                'width': '700px',
                'height': '70px',
                'position': 'top-right',
                // 'backgroundColor': '#cccccc',
                'margin': '0px 0px 0px 1px',
            },
    panel_ploting: {
                width: '650px',
                height: "300px",
                position: 'bottom-right'
            },
    labelTitulo : {
                fontSize: '18px', 
                fontWeight: 'bold',
                backgroundColor: '#F5F4F9'
            },
    style_label:  {
                position: 'bottom-center',
                width: '20%',
                height: '20px',
                margin: '0px',
                padding: '0px',
            },
    barra_options: {
                legend: 'none',
                lineWidth: 1,
                pointSize: 5,
                height: 60,
                vAxis: {
                    gridlines: {
                        count: 0
                    }
                },
                'chartArea': {
                    left: 30,
                    top: 10,
                    right: 30,
                    width: '100%',
                    height: '80%'
                },
                hAxis: {
                    textPosition: 'in',
                    showTextEvery: 1,
                    interpolateNulls: true,
                    slantedTextAngle: 90,
                    slantedText: true,
                    textStyle: {
                        color: '#000000',
                        fontSize: 12,
                        fontName: 'Arial',
                        bold: false,
                        italic: false
                    }
                },
                tooltip :{
                    trigger: 'none',
                },
                colors: ['#f0e896'],
                crosshair: {
                    trigger: 'both',
                    orientation: 'vertical',
                    focused: {
                        color: '#561d5e'
                    }
                }
            }
};
var regioes;
var MapLeft = ui.Map(pstyle.mapleft);
var MapRight = ui.Map(pstyle.mapright);
MapRight.setOptions('SATELLITE');
MapLeft.setOptions('SATELLITE');

var Mapeando = function(nyear){
    print(" ==== Processing year = " + nyear.toString());
    
    MapLeft.clear();
    MapRight.clear();
    
    print("Mapeando ano " + nyear.toString());
    var bandaActiva  = 'classification_' + nyear.toString();
    print("bioma  " + bioma_select);
    
    print(" mosaicHarms ", mosaicHarms.size());

    var baseBiomas = raster_biome.eq(dict_raster[bioma_select]);
    regioes = regionss.filter(ee.Filter.eq('bioma', bioma_select)).geometry();
    
    var mosaicoYyear = Mosaicos.filter(ee.Filter.eq('biome', dictNameBiome[bioma_select]))
                            .filter(ee.Filter.eq('year', parseInt(nyear)));
    print( " mosaicoYyear  ==> ", mosaicoYyear);
    mosaicoYyear = mosaicoYyear.median().updateMask(baseBiomas);
    
    var mosaicHarmsYyear = mosaicHarms.filter(ee.Filter.eq('biome', dictNameBiomes[bioma_select]))
                                .filter(ee.Filter.eq('year', parseInt(nyear)))
                                .map(ApplyReducers);    
    print( " mosaicHarmsYyear  ==> ", mosaicHarmsYyear);
    print( "  ", dictNameBiome[bioma_select]);
    mosaicHarmsYyear  =  mosaicHarmsYyear.mosaic().updateMask(baseBiomas); 
    
    //Duna 23, Urbano 24, Mining 30
    var areasIntMapb = mapbiomasCol9.select(bandaActiva)
                            .remap(param.classMapB, param.classNew)
                            .updateMask(baseBiomas);

    var maskExcluir = areasIntMapb.eq(1);
    var maskAgrop = areasIntMapb.eq(2);

    // Camada de solo exposto         
    var maskAreaNVeg = mapbiomasCol9.select(bandaActiva)
                            .updateMask(baseBiomas).eq(25).selfMask();
    print(" mapsSoilsV4 by biomes ", mapsSoilsV4.aggregate_histogram('biome'))
    var mapsSoilsV4Yyear = mapsSoilsV4.filter(ee.Filter.eq('biome', dictNameBiomes[bioma_select]))
                            .filter(ee.Filter.eq('year', parseInt(nyear)))
    print(" mapas Soils year ", mapsSoilsV4Yyear);                        
    mapsSoilsV4Yyear = mapsSoilsV4Yyear.max().gte(0.84).selfMask();
    MapMosaicL = ui.Map.Layer({
                    "eeObject": mosaicoYyear,
                    'visParams': visualizar.visMosaic,
                    'name': 'Mosaic Col9 ' + nyear.toString(),
                    'shown': true,
                    'opacity': 1
                });
    //
    MapMosaicD = ui.Map.Layer({
                    "eeObject": mosaicoYyear,
                    'visParams': visualizar.visMosaic,
                    'name': 'Mosaic Col9 ' + nyear.toString(),
                    'shown': true,
                    'opacity': 1
                });

    MapMaskAreaNVeg = ui.Map.Layer({
                    "eeObject": maskAreaNVeg,
                    'visParams': visualizar.areaNVeg,
                    'name': 'Área nVeget' + nyear.toString(),
                    'shown': true,
                    'opacity': 1
                });
    //            
    MapMosHarmL = ui.Map.Layer({
                "eeObject": mosaicHarmsYyear,
                'visParams': visualizar.mosaic,
                'name': 'MosaicHarm ' + nyear.toString() ,
                'shown': true,
                'opacity': 1
                });
    //
    MapMosHarmD = ui.Map.Layer({
                "eeObject": mosaicHarmsYyear,
                'visParams': visualizar.mosaic,
                'name': 'MosaicHarm ' + nyear.toString() ,
                'shown': true,
                'opacity': 1
                });
    //            
    MapCol90 = ui.Map.Layer({
                "eeObject": mapbiomasCol9.select(bandaActiva).updateMask(baseBiomas),
                'visParams': visualizar.visclassCC,
                'name': "Col9.0 y  " + nyear.toString(),
                'shown': false,
                'opacity': 1
                });

    MapSoilV4 = ui.Map.Layer({
                "eeObject": mapsSoilsV4Yyear,
                'visParams': visualizar.soilV2,
                'name': "mapSoil_V4_" + yyear.toString(),
                'shown': true,
                'opacity': 1
                });
                ///
    MaptoExc = ui.Map.Layer({
                "eeObject": maskExcluir.selfMask(),
                'visParams': visualizar.excluir,
                'name': 'AreaExcluirNotVeg',
                'shown': false,
                'opacity': 1
            });
    //
    MaptoAgr = ui.Map.Layer({
                "eeObject": maskAgrop.selfMask(),
                'visParams': visualizar.agropecuaria,
                'name': 'AreaAgropec',
                'shown': false,
                'opacity': 1
            });

    // 
    var dictPaint = {featureCollection: regionss,  color: 1,  width: 1.5};
    var regions = ee.Image().byte().paint(dictPaint);    
    MapRegs = ui.Map.Layer({
        "eeObject": regions,
        'visParams':{color: 'ff004a'},
        'name': 'regions',
        'shown': false,
        'opacity': 1
    })
    
    if (visMosaic === true){ 
        print("show MapRight ", MapRight.layers())
        MapRight.remove(MapMosaicD);
        MapRight.remove(MapMosHarmD);
        MapRight.remove(MaptoExc);
        MapRight.remove(MapSoilV4);
        MapRight.remove(MaptoAgr);
        MapLeft.remove(MapCol90);
        MapLeft.remove(MapMosaicL);
        MapLeft.remove(MapMosHarmL);
        MapRight.remove(MapMaskAreaNVeg);
        // MapFinal.clear()
    }

    MapLeft.add(MapMosaicL);
    MapLeft.add(MapMosHarmL);
    MapLeft.add(MapCol90);
    MapRight.add(MapMosaicD);
    MapRight.add(MapMosHarmD);
    MapRight.add(MapSoilV4);
    MapRight.add(MapMaskAreaNVeg);
    MapRight.add(MaptoExc);
    MapRight.add(MaptoAgr);
    MapRight.add(MapRegs);

    // MapRight.setCenter(lstRegion[region_selected][0], lstRegion[region_selected][1], 12);
}
 
print('Iniciando Rotina no Cerrado...🔥🔥' );
Mapeando(yyear);
var barra_year = ui.Chart.feature.byFeature(
                    colectionYears, 'year', 'system_yValue')
                    .setChartType('LineChart')
                    .setOptions(pstyle.barra_options);
    
barra_year.style().set(pstyle.barrayear);
    
    
barra_year.onClick(function (xValue, yValue, seriesName) {
    if (!xValue) return;
    var feature = ee.Feature(
        ee.FeatureCollection(colectionYears)
        .filter(ee.Filter.eq('year', xValue))
        .first()
    );
    yyear = xValue;
    print("selecionado o ano ===> " + xValue)
    Mapeando(yyear);
    MapRight.add(panelPlot);
    MapRight.onClick(run_plot_Serie);
    MapLeft.onClick(run_plot_Serie);
});

function format_image(img){
    var nband = ee.Algorithms.String(ee.List(img.bandNames()).get(0));
    var lname = nband.length();
    var yyear = ee.Number.parse(nband.slice(ee.Number(lname).subtract(8), ee.Number(lname).subtract(4)));
    var mmonth = ee.Number.parse(nband.slice(ee.Number(lname).subtract(4), ee.Number(lname).subtract(2)));
    var dday = ee.Number.parse(nband.slice(ee.Number(lname).subtract(2), ee.Number(lname)));
    var dataImg = ee.Date.fromYMD(yyear, mmonth, dday);
    return ee.Image(img).rename('class').set('system:time_start', dataImg);
}

function format_image_Collection_fromBands(images){
    var redBnds = ee.List(images.bandNames());    
    var lstIterImg = redBnds.iterate(
                      function(itmbnd, mylist){
                          var img = ee.Image(images).select([itmbnd]);
                          var lname = ee.Algorithms.String(itmbnd).length();
                          var subStringbnd = ee.String(itmbnd).slice(ee.Number(lname).subtract(2), ee.Number(lname).subtract(1))
                          var lstUpdate = ee.Algorithms.If( 
                                          ee.Algorithms.IsEqual(subStringbnd.compareTo(ee.Algorithms.String('_')), 0),
                                          ee.List(mylist),
                                          ee.List(mylist).add(format_image(img))
                                      )
                          return lstUpdate;
                      },
                      ee.List([])
                  )
    return ee.ImageCollection(lstIterImg)
}

    
function  run_plot_Serie (coords) {
    // Update the lon/lat panel with values from the click event.
    lon.setValue('lon: ' + coords.lon.toFixed(2)),
    lat.setValue('lat: ' + coords.lat.toFixed(2));

    // Add a red dot for the point clicked on.
    var point = ee.Geometry.Point(coords.lon, coords.lat);
    var dot = ui.Map.Layer(point, {color: 'FF0000'}, 'point_clicked');
    MapRight.layers().set(7, dot); // colocar o ponto no local certo      
    // MapLeft.layers().set(1, dot);
    ////////////////////////////////////////////////////////////////////////////////
    // Plot the fitted model and the original data at the ROI- Modis.
    var mosaicHarmspto = mosaicHarms.filterBounds(point);
    print(" newlstndfi ", mosaicHarmspto);


    var newlstndfi = ee.List(mosaicHarmspto.toList(mosaicHarmspto.size()));
    var lstBndNDFI = newlstndfi.iterate( 
            function(item, mylist){
                var imtmp = ee.Image(item);
                var lsttemp = ee.Algorithms.If(
                    ee.Algorithms.IsEqual(ee.Number(ee.List(imtmp.bandNames()).size()).eq(1), 1),
                    ee.List(mylist).add(format_image(imtmp)),
                    ee.List(mylist).cat(format_image_Collection_fromBands(imtmp))
                )
                return lsttemp;
            },
            ee.List([])
        )
    print("Lista de imagens formatadas ", ee.ImageCollection.fromImages(lstBndNDFI));
    var indChartHarmonic= ui.Chart.image.series(
                ee.ImageCollection.fromImages(lstBndNDFI), point, ee.Reducer.first(), 30)
                // .setSeriesNames([ indexAnalise, 'estimado'])
                .setOptions({
                      colors: ['#8d5959'],
                      pointShape: 'diamond',
                      lineWidth: 1,
                      pointSize: 3,
                });
    panelPlot.widgets().set(2, indChartHarmonic);   
    
    var imgCol_NDFIa = get_collection_NDFIa(point);
    var indChartHarmonic= ui.Chart.image.series(
        imgCol_NDFIa, point, ee.Reducer.first(), 30)
        // .setSeriesNames([ indexAnalise, 'estimado'])
        .setOptions({
              colors: ['#8d5959'],
              pointShape: 'diamond',
              lineWidth: 1,
              pointSize: 3,
        });
    panelPlot.widgets().set(3, indChartHarmonic);   
    
    var lstImgMaps = lsAnos.iterate(
                        function(nyear, mylist){
                            // print(nyear);
                            var imgYY = mapbiomasCol9.select(ee.String('classification_').cat(nyear));
                            // print("imagem year ", imgYY)
                            var dateYY = ee.Date.fromYMD(ee.Number.parse(nyear), 1,1);
                            mylist = ee.List(mylist).add(imgYY.rename('class').set('system:time_start', dateYY));
                            return mylist;
                        }, ee.List([]))

    var chartmapUsos = ui.Chart.image.series(
                ee.ImageCollection.fromImages(lstImgMaps), point, ee.Reducer.first(), 30)
                .setOptions({
                    colors: ['#ffb961'], //palettes.get('classification8'),
                    pointShape: 'diamond',
                    lineWidth: 1,
                    pointSize: 3,
                    backgroundColor: '#05313d',
              });
    panelPlot.widgets().set(4, chartmapUsos); 

}

MapRight.onClick(run_plot_Serie);
MapLeft.onClick(run_plot_Serie);

var panel = ui.Panel([barra_year],
    ui.Panel.Layout.Flow('vertical'), pstyle.stretchp);

var label_ini = ui.Label('     ');
var label_fin = ui.Label('     ');
var seletor_Bioma = ui.Select({
    items: param.lstBiomes,
    onChange: function(nbiome){
        bioma_select = nbiome;
        print("selecionado o Bioma ===> " + nbiome);
    }
})
// Set a place holder.
seletor_Bioma.setPlaceholder('Biome Choosed Cerrado...');
seletor_Bioma.style().set(pstyle.selector);

label_ini.style().set(pstyle.style_label);
label_fin.style().set(pstyle.style_label);

// Create a panel to hold our widgets.
var panelPlot = ui.Panel();
panelPlot.style().set(pstyle.panel_ploting);


// Create an intro panel with labels.
var titulo =  ui.Label({
    value: 'Sistem of classification of fire',
    style: pstyle.labelTitulo
})

var accion = ui.Label(' (Click into map to inpects) ')
var panelHead = ui.Panel({
    layout: ui.Panel.Layout.flow('horizontal'),
    style: pstyle.panel_head
});
panelHead.add(titulo);
panelHead.add(accion);
panelPlot.add(panelHead);
var lon = ui.Label();
var lat = ui.Label();
panelPlot.add(ui.Panel([lon, lat], ui.Panel.Layout.flow('horizontal')));

var Maplincados = ui.Map.Linker([MapLeft, MapRight]);
MapRight.centerObject(regioes, 8)
MapRight.add(panelPlot)
var compPanel = ui.SplitPanel({
    firstPanel: Maplincados.get(0),
    secondPanel: Maplincados.get(1),
    orientation: 'horizontal',
    wipe: true,
    style: {
        stretch: 'both'
    }
});

var panel0 = ui.Panel(
        [compPanel],
        ui.Panel.Layout.Flow('vertical', true), 
        pstyle.stretchp
    );

var panel_region = ui.Panel(
        [label_ini, seletor_Bioma, label_fin],
        ui.Panel.Layout.Flow('horizontal'), {
            border: '2px solid black',
            height: '30px',
        }
    )
var panel_parametro = ui.Panel([panel_region],
        ui.Panel.Layout.Flow('vertical'), {}
    )
var panel = ui.Panel(
        [panel_parametro, panel0, barra_year],
        ui.Panel.Layout.Flow('vertical'), pstyle.stretchp
    );
ui.root.widgets().reset([panel]);
ui.root.setLayout(ui.Panel.Layout.Flow('vertical'))