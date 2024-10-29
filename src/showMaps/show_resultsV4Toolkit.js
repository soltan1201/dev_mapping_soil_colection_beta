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
            },
    charOptions: {
        'title': 'Inspector',
        'legend': 'none',
        'chartArea': {
            left: 30,
            right: 2,
        },
        'titleTextStyle': {
            color: '#ffffff',
            fontSize: 10,
            bold: true,
            italic: false
        },
        'tooltip': {
            textStyle: {
                fontSize: 10,
            },
            // isHtml: true
        },
        'backgroundColor': '#21242E',
        'pointSize': 6,
        'crosshair': {
            trigger: 'both',
            orientation: 'vertical',
            focused: {
                color: '#dddddd'
            }
        },
        'hAxis': {
            // title: 'Date', //muda isso aqui
            slantedTextAngle: 90,
            slantedText: true,
            textStyle: {
                color: '#ffffff',
                fontSize: 8,
                fontName: 'Arial',
                bold: false,
                italic: false
            },
            titleTextStyle: {
                color: '#ffffff',
                fontSize: 10,
                fontName: 'Arial',
                bold: true,
                italic: false
            },
            viewWindow: {
                max: 36,
                min: 0
            },
            gridlines: {
                color: '#21242E',
                interval: 1
            },
            minorGridlines: {
                color: '#21242E'
            }
        },
        'vAxis': {
            title: 'Class', // muda isso aqui
            textStyle: {
                color: '#ffffff',
                fontSize: 10,
                bold: false,
                italic: false
            },
            titleTextStyle: {
                color: '#ffffff',
                fontSize: 10,
                bold: false,
                italic: false
            },
            viewWindow: {
                max: 50,
                min: 0
            },
            gridlines: {
                color: '#21242E',
                interval: 2
            },
            minorGridlines: {
                color: '#21242E'
            }
        },
        'lineWidth': 0,
        // 'width': '300px',
        // 'height': '200px',
        'margin': '0px 0px 0px 0px',
        'series': {
            0: { color: '#21242E' }
        },
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
    
    var lstImgMaps = lsAnos.iterate(
                        function(nyear, mylist){
                            var imgYY = mapbiomasCol9.select('classification_' + nyear);
                            var dateYY = ee.Date.fromYMD(parseInt(nyear), 1,1);
                            mylist = ee.List(mylist).add(imgYY.rename('class').set('system:time_start', dateYY));
                            return mylist; 
                        }, ee.List([]))

    var chartmapUsos = ui.Chart.image.byRegion(
                ee.ImageCollection.fromImages(lstBndNDFI), point, ee.Reducer.first(), 30)
                .setOptions(pstyle.charOptions);
    panelPlot.widgets().set(3, chartmapUsos); 

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