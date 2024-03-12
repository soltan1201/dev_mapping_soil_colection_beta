//https://code.earthengine.google.com/ec031c9c6753d13df1c545eed1aea111
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
    // 'classmapping': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOIL',
    'classmappingV3': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV3',
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'inputAsset': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
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
var MapCol8 = null;
// var MapFloresta = null;
var MapMaskAreaNVeg = null;
var MapSoilBase = null;
var MapSoilV4 = null;
var MaptoExc = null;
var MaptoAgr = null;
var MapRegs = null;
// https://code.earthengine.google.com/f428edf837b2d10b5d78157e0225d113
var lstRegion = {
      '51': [-53.08, -31.09],
      '52': [-53.29, -30.61],
      '53': [-54.62, -29.42],
      '31': [-45.12, -6.99],
      '32': [-45.07, -14.96],
      '35': [-49.28, -13.27],
      '34': [-54.76, -14.19],
      '33': [-50.50, -19.49],
      '21': [-41.15, -10.85],
      '22': [-42.06, -7.41],
      '23': [-38.36, -5.69],
      '24': [-40.17, -12.21],
      '60': [-56.66, -18.29],
      '11': [-66.88, -5.09],
      '12': [-62.40, 2.64],
      '13': [-57.88, -0.33],
      '14': [-51.84, 0.86],
      '15': [-59.10, -14.85],
      '16': [-60.12, -8.44],
      '17': [-55.11, -11.03],
      '18': [-52.60, -5.94],
      '19': [-47.08, -3.14],
      '41': [-42.40, -19.21],
      '42': [-46.88, -24.57],
      '44': [-50.53, -22.30],
      '45': [-38.74, -14.25],
      '46': [-51.90, -27.75],
      '47': [-51.32, -25.04]
};

var region_selected = '35';
var yyear = 2005;
var bioma_select = 'Cerrado';
var visMosaic = true;

var lsAnos = ee.List([
    1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 
    1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
    2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022
  ]);
 
var colectionYears = lsAnos.map(function(yyear){
                return ee.Feature(null, {'year': yyear,  'system:yValue': 0});
      });  
colectionYears = ee.FeatureCollection(colectionYears);
print(" feature ", colectionYears);

var regionss = ee.FeatureCollection(param.regions);     
var mapbiomasCol8 = ee.Image(param.inputAsset);
var mapsSoilsV3 = ee.ImageCollection(param.classmappingV3); // camada de base 
var mapsSoilsV4 = ee.ImageCollection(param.classmappingV4); // camada de base 

var mosaicHarms = ee.ImageCollection(param.asset_mosaic);
print("show mosaic harmonicos the first 5 ", mosaicHarms.limit(5));

var Mosaicos = ee.ImageCollection(param.assetIm).select(param.bandas);    
print("Show mosaic Mapbiomas the frist 5 ", Mosaicos.limit(5));

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
    print("region " + region_selected);
    var regioes = regionss.filter(ee.Filter.eq('region', parseInt(region_selected))).geometry();
    
    var mosaicoYyear = Mosaicos.filter(ee.Filter.eq('biome', dictNameBiome[bioma_select]))
                            .filter(ee.Filter.eq('year', nyear)).median().clip(regioes);

    var mosaicHarmsYyear = mosaicHarms.filterBounds(regioes)
                                .filter(ee.Filter.eq('year', nyear))
                                .map(ApplyReducers);    
                                
    mosaicHarmsYyear  =  mosaicHarmsYyear.mosaic().clip(regioes);                           
    
    //Duna 23, Urbano 24, Mining 30
    var areasIntMapb = mapbiomasCol8.select(bandaActiva)
                            .remap(param.classMapB, param.classNew)
                            .clip(regioes);
    var maskExcluir = areasIntMapb.eq(1);
    var maskAgrop = areasIntMapb.eq(2);
    // var mapbiomasFlorest = mapbiomas.select(bandaActiva)
    //                         .remap(param.classMapB, param.classFlorest)
    //                         .clip(regioes).selfMask();
    // var mapAfloramento = mapbiomas.select(bandaActiva)
    //                             .clip(regioes).eq(29).selfMask();    //   
    // Camada de solo exposto         
    var maskAreaNVeg = mapbiomasCol8.select(bandaActiva)
                            .clip(regioes).eq(25).selfMask();
    var mapsSoilsV3Yyear = mapsSoilsV3.filterBounds(regioes)
                            .filter(ee.Filter.eq('year', nyear))
                            .max();//.clip(regioes);
    print("know number of images maps soil ", mapsSoilsV3Yyear);
    //
    // mapsSoilsV2Yyear = mapsSoilsV2Yyear.updateMask(maskExcluir).clip(regioes);
    print("mapas de solo base version 3", mapsSoilsV3Yyear);    
    // var maskVersion3 = mapsSoilsV3Yyear.eq(1);                      
    
    var mapsSoilsV4Yyear = mapsSoilsV4.filter(ee.Filter.eq('region', region_selected))
                            .filter(ee.Filter.eq('year', nyear))
                            .max().gte(0.0);//.clip(regioes);

    MapMosaicL = ui.Map.Layer({
                    "eeObject": mosaicoYyear,
                    'visParams': visualizar.visMosaic,
                    'name': 'Mosaic Col8 ' + nyear.toString(),
                    'shown': true,
                    'opacity': 1
                });
    //
    MapMosaicD = ui.Map.Layer({
                    "eeObject": mosaicoYyear,
                    'visParams': visualizar.visMosaic,
                    'name': 'Mosaic Col8 ' + nyear.toString(),
                    'shown': true,
                    'opacity': 1
                });
    // MapFloresta = ui.Map.Layer({
    //                 "eeObject": mapbiomasFlorest,
    //                 'visParams': visualizar.floresta,
    //                 'name': 'Florest Col8 ' + nyear.toString(),
    //                 'shown': true,
    //                 'opacity': 1
    //             });
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
    MapCol8 = ui.Map.Layer({
                "eeObject": areasIntMapb,
                'visParams': visualizar.visclassCC,
                'name': "Mapbiomas Col8.0" + nyear.toString(),
                'shown': false,
                'opacity': 1
                });
    //
    MapSoilBase = ui.Map.Layer({
                "eeObject": mapsSoilsV3Yyear.eq(1).selfMask(),
                'visParams': visualizar.soilVBase,
                'name': "mapSoil_V3Base_" + yyear.toString(),
                'shown': true,
                'opacity': 1
                });

    MapSoilV4 = ui.Map.Layer({
                "eeObject": mapsSoilsV4Yyear,
                'visParams': visualizar.soilV2,
                'name': "mapSoil_V4_" + yyear.toString(),
                'shown': true,
                'opacity': 1
                });
    

    //
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
            MapRight.remove(MapSoilBase);
            MapRight.remove(MapSoilV4);
            MapRight.remove(MaptoAgr);
            MapLeft.remove(MapCol8);
            MapLeft.remove(MapMosaicL);
            MapLeft.remove(MapMosHarmL);
            // MapRight.remove(MapFloresta);
            MapRight.remove(MapMaskAreaNVeg);
            // MapFinal.clear()
    }

    MapLeft.add(MapMosaicL);
    MapLeft.add(MapMosHarmL);
    MapLeft.add(MapCol8);
    //
    MapRight.add(MapMosaicD);
    MapRight.add(MapMosHarmD);
    MapRight.add(MapSoilBase);
    MapRight.add(MapSoilV4);
    // MapRight.add(MapFloresta);
    MapRight.add(MapMaskAreaNVeg);
    MapRight.add(MaptoExc);
    MapRight.add(MaptoAgr);
    MapRight.add(MapRegs);

    // MapRight.setCenter(lstRegion[region_selected][0], lstRegion[region_selected][1], 12);
}
 
print('Iniciando Rotina no Cerrado...🔥🔥' );
Mapeando(yyear);
var barra_year = ui.Chart.feature.byFeature(
                    colectionYears, 'year', 'system:yValue')
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
});
    
    
var panel = ui.Panel([barra_year],
    ui.Panel.Layout.Flow('vertical'), pstyle.stretchp);

var label_ini = ui.Label('     ');
var label_fin = ui.Label('     ');
var seletor_Bioma = ui.Select({
    items: param.lstBiomes,
    onChange: function(nbiome){
        bioma_select = nbiome;
        print("selecionado o Bioma ===> " + nbiome);
        var lstReg = dictRegions[bioma_select];
        seletor_reg.items().reset(lstReg);
                    
        // Set the first band to the selected band.
        seletor_reg.setValue(seletor_reg.items().get(0));
    }
})
// Set a place holder.
seletor_Bioma.setPlaceholder('Biome Choosed Cerrado...');


var seletor_reg = ui.Select({
    items: dictRegions[bioma_select],
    onChange: function(nregion){
        region_selected = nregion;
        print("selecionada a Região ===> " + nregion);
        MapRight.setCenter(lstRegion[region_selected][0], lstRegion[region_selected][1], 12)
    }
})
// Set a place holder.
seletor_reg.setPlaceholder('Region Choosed 35...');
seletor_Bioma.style().set(pstyle.selector);
seletor_reg.style().set(pstyle.selector);

label_ini.style().set(pstyle.style_label);
label_fin.style().set(pstyle.style_label);

// MapRight.addLayer(ee.Image().select(), {}, "Mosaic Col8'");
// MapRight.addLayer(ee.Image().select(), {}, "MosaicHarm");
// MapRight.addLayer(ee.Image().select(), {}, "mapSoil_V2 ");
// MapRight.addLayer(ee.Image().select(), {}, "AreaExcluirNotVeg");
// MapRight.addLayer(ee.Image().select(), {}, "AreaAgropecuaria");
// MapRight.addLayer(ee.Image().select(), {}, "Regions");
// //
// MapLeft.addLayer(ee.Image().select(), {}, "Mosaic Col8'");
// MapLeft.addLayer(ee.Image().select(), {}, "MosaicHarm");
// MapLeft.addLayer(ee.Image().select(), {}, "Mapbiomas Col7.1");



var Maplincados = ui.Map.Linker([MapLeft, MapRight]);
MapRight.setCenter(-60.354, -7.942, 8)
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
        ui.Panel.Layout.Flow('vertical', true), pstyle.stretchp
    );

var panel_region = ui.Panel(
        [label_ini, seletor_Bioma, seletor_reg, label_fin],
        ui.Panel.Layout.Flow('horizontal'), {
            border: '2px solid black',
            height: '50px',
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