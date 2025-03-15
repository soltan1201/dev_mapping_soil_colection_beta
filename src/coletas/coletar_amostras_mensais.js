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
    mosaico: {
        bands: ["red","green","blue"],
        gamma: 1,
        max: 3000,
        min: 55
    },
    mosaicoGEE: {
        bands: ["red","green","blue"],
        gamma: 1,
        max: 0.2,
        min: 0.05
    },
    indiceNDFI:{
        min: 1000, 
        max: 10000,
        palette: paletaNDFI
    }
}
var trueColor432Vis = {
    min: 0.0,
    max: 0.4,
  };
  
  
  var params = {
      'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
      'assetMapbiomas90': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',  
      'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
      'asset_ndfia_harmonic':  'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonico',
      'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
      'classMapB' :   [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
      'classNotSoil': [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0],
      'regionsSel': [21,31,32],
      'harmonics': 2,  
      'dates':{
          '0': '-01-01',
          '1': '-12-31'
      },      
      'zeroT1_SR' : false,
      'sensorIdsToa': {        
          'L5': 'LANDSAT/LT05/C02/T1_TOA',
          'L7': 'LANDSAT/LE07/C02/T1_TOA',
          'L8': 'LANDSAT/LC08/C02/T1_TOA',
          'L9': 'LANDSAT/LC09/C02/T1_TOA'
      },
      'bnd' : {
          'L5': ['B1','B2','B3','B4','B5','B7','QA_PIXEL','QA_RADSAT'],
          'L7': ['B1','B2','B3','B4','B5','B7','QA_PIXEL','QA_RADSAT'],
          'L8': ['B2','B3','B4','B5','B6','B7','QA_PIXEL','QA_RADSAT'],
          'L9': ['B2','B3','B4','B5','B6','B7','QA_PIXEL','QA_RADSAT']
      }, 
      'indexProc': {
          'L5': 'LT05',
          'L7': 'LE07',
          'L8': 'LC08',
          'L9': 'LC09'
      },   
      'bnd_LG': ['blue','green','red','nir','swir1','swir2','pixel_qa'],
      'bnd_QA': ['blue','green','red','nir','swir1','swir2','QA_PIXEL', 'QA_RADSAT'],
      'bnd_L': ['blue','green','red','nir','swir1','swir2'],
      'CC': 70,   
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

function defineSensor(year){
    var ss = 'L8';
    var arrayYY = [2000, 2001, 2002, 2012];
    if (year >= 2012){
        ss = 'L8';
    }else{
        if (arrayYY.indexOf(year) > -1){
            ss = "L7";        
        }else{
            ss = 'L5';
        }
    }
    print("SS " + ss);
    return ss;
}

function cloudMask_QA_pixel(image){
    var img = image
    var qaMask = image.select('QA_PIXEL').eq(21824).rename("qaMask"); //# 6 "1s" to account for snow
    var saturationMask = image.select('QA_RADSAT').eq(0);
    image = image.updateMask(qaMask).updateMask(saturationMask).multiply(10000);
    //# 'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    image = image.select(params['bnd_L']);
    return image.copyProperties(img);
}

function cloudMaskL57_QA_pixel(image){
    var img = image
    var qaMask = image.select('QA_PIXEL').eq(5440).rename("qaMask"); //# 6 "1s" to account for snow
    var saturationMask = image.select('QA_RADSAT').eq(0);
    image = image.updateMask(qaMask).updateMask(saturationMask).multiply(10000);
    // # 'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    image = image.select(params['bnd_L']);  
    return image.copyProperties(img);
}

function getCollectionCru(mmes, ano, myGeom){

    var ss = defineSensor(ano);
    var date0 = ee.Date.fromYMD(ano,mmes, 1);
    var date1 = date0.advance(1, 'month');
    // print(params['sensorIds'][ss])
    print(date0, date1);
    // print(params['bnd'][ss]) 
    // print(params['bnd_LG'])
    var imgColLandsat = null;
    if (ss === 'L8'){        
        imgColLandsat = (ee.ImageCollection(params['sensorIdsToa'][ss])
                            .filterBounds(myGeom)
                            .filterDate(date0, date1)
                            .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))
                            .select(params['bnd'][ss], params['bnd_QA'])
                    )
        // # incluindo o processamento OliToEtmRMA 
        // # imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL8(img))
        imgColLandsat = imgColLandsat.map(cloudMask_QA_pixel)
    }else{
        if (ss === 'L9'){
            print(" processing L9 and L8 ")
            imgColLandsat = (ee.ImageCollection(params['sensorIdsToa']['L8']).merge(
                                ee.ImageCollection(params['sensorIdsToa'][ss]))
                                    .filterBounds(myGeom)
                                    .filterDate(date0, date1)
                                    .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))
                                    .select(params['bnd'][ss], params['bnd_QA'])
                            )
            imgColLandsat = imgColLandsat.map(cloudMask_QA_pixel);
        }else{
            if (ss === 'L5'){
                if (params['zeroT1_SR'] == False){        
                    print("==> L5 <== " + params['sensorIdsToa']['L5'])
                    imgColLandsat = ( ee.ImageCollection(params['sensorIdsToa']['L5'])
                                        .filterBounds(myGeom)
                                        .filterDate(date0, date1)
                                        .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))
                                        .select(params['bnd']['L5'], params['bnd_QA'])  
                                )
                }else{
                    print("==> L5 <== " + params['sensorIdsToa']['L5'])
                    imgColLandsat = (ee.ImageCollection(params['sensorIdsToa']['L5'])
                                        .filterBounds(myGeom)
                                        .filterDate(date0, date1)
                                        .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))
                                        .select(params['bnd']['L5'], params['bnd_QA'])
                                )                   
                    imgColLandsat = imgColLandsat.map(cloudMaskL57_QA_pixel);
                }
            }else{
                // ss = 'L7'
                print("== L7 == " + params['sensorIdsToa']['L7']);
                imgColLandsat = (ee.ImageCollection(params['sensorIdsToa']['L7'])
                                    .filterBounds(myGeom)
                                    .filterDate(date0, date1)
                                    .filter(ee.Filter.lt("CLOUD_COVER", params['CC']))
                                    .select(params['bnd']['L7'], params['bnd_QA'])
                                )
                // # imgColLandsat = imgColLandsat.map(lambda img: self.cloudMaskL57(img))
                imgColLandsat = imgColLandsat.map(cloudMaskL57_QA_pixel);
            }
        }
    }
    return imgColLandsat;
}
  
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



function GET_NDFIA(IMAGE) {
        
        var lstBands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];
        var lstFractions = ['GV', 'SHADE', 'NPV', 'SOIL', 'CLOUD'];
        var endmembers = [            
            [ 500,  900,  400, 6100, 3000, 1000],  //# 'gv': 
            [ 190,  100,   50,   70,   30,   20],  //# 'shade':
            [1400, 1700, 2200, 3000, 5500, 3000],  //# 'npv': 
            [2000, 3000, 3400, 5800, 6000, 5800],  //# 'soil':
            [9000, 9600, 8000, 7800, 7200, 6500]   //# 'cloud': 
        ];

        var fractions = ee.Image(IMAGE).select(lstBands).unmix(endmembers, true, true);
        fractions = fractions.rename(lstFractions);
        // print(UNMIXED_IMAGE);
        var NDFI_ADJUSTED = fractions.expression(
                                "float( ((b('GV') / (1 - b('SHADE'))) - b('SOIL')) / ((b('GV') / (1 - b('SHADE'))) + (b('NPV')) + b('SOIL')) )"
                              ).rename('NDFIa')

        NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()
        
        var RESULT_IMAGE = ee.Image(index_select(IMAGE, false))
                                    .addBands(fractions.multiply(10000).toUint16())
                                    .addBands(NDFI_ADJUSTED);

        return ee.Image(RESULT_IMAGE).toUint16()
    
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

var mosaicHarm = ee.ImageCollection(params.asset_ndfia_harmonic)
                        .filter(ee.Filter.eq('year', 2021))
                        .filterBounds(regionSel).select([0])
                        .map(function(img){return img.rename('banda')});
print(mosaicHarm)
mosaicHarm = mosaicHarm.mosaic().updateMask(imgMaskReg);
var data_inicial = ee.Date.fromYMD(yyear, mmonth, 1);
var mosaicMensal =  ee.ImageCollection(params.asset_collectionId)
                        .filterBounds(regionSel.geometry())
                        .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                        .select(params.bnd_L).first()
                        .updateMask(imgMaskReg);
    
print(" mmosaico Mensal Landsat ", mosaicMensal)
var lstBands = ['classification_2019', 'classification_2020','classification_2021'];
print(lstBands[0]);
var mMapbiomas = ee.Image(params.assetMapbiomas90).updateMask(imgMaskReg);
print(mMapbiomas);
var maskYYSoil = mMapbiomas.select(lstBands).eq(25);
maskYYSoil = maskYYSoil.reduce(ee.Reducer.sum()).eq(3);

var maskNotSoilPre = mMapbiomas.select(lstBands[0])
                        .remap(params.classMapB, params.classNotSoil);
var maskNotSoilCourr = mMapbiomas.select(lstBands[1])
                        .remap(params.classMapB, params.classNotSoil);
var maskNotSoilPos = mMapbiomas.select(lstBands[2])
                        .remap(params.classMapB, params.classNotSoil);

var maskNotSoil = maskNotSoilCourr.add(maskNotSoilPre).add(maskNotSoilPos).gt(1).multiply(2);
maskYYSoil = maskYYSoil.add(maskNotSoil);

var imColMonth = getCollectionCru(mmonth, yyear, regionSel);
print(" Imagem Collection Month  ", imColMonth);
// Create a cloud-free, most recent value composite.
// var imgComp =  GET_NDFIA(imColMonth.first());
// print(imgComp)
// bdikb
mosaicMensal = GET_NDFIA_mosaic(mosaicMensal);
imColMonth = imColMonth.map(GET_NDFIA);
imColMonth = imColMonth.qualityMosaic('NDFIa').updateMask(maskYYSoil.gt(0)).selfMask();



// imColMonth= imColMonth.updateMask(mMapbiomas)
var ptosTemp = imColMonth.addBands(maskYYSoil.rename('class')).select(bandasInt).stratifiedSample({
                                    numPoints: 5000, 
                                    classBand: 'class', 
                                    region: regionSel.geometry(),                                       
                                    scale: 30,                                     
                                    dropNulls: true,
                                    geometries: true
                                });


print(ptosTemp.limit(30));
Map.addLayer(ee.Image.constant(1), {min:0, max: 1}, 'base');
// Paint all the polygon edges with the same number and width, display.
var outlineReg = ee.Image().byte().paint({featureCollection: regionSel, color: 1, width: 3});
Map.addLayer(outlineReg, {palette: 'FF0000'}, 'Regions');

Map.addLayer(imColMonth, paramVis.mosaico, 'mosaico Mensal');
Map.addLayer(mosaicMensal, paramVis.mosaicoGEE, 'mosaico Mensal GEE');
Map.addLayer(imColMonth.select('NDFIa'), paramVis.indiceNDFI, 'ndfia');
Map.addLayer(mosaicMensal.select('NDFIa'), paramVis.indiceNDFI, 'ndfia GEE');
Map.addLayer(mosaicHarm, paramVis.indiceNDFI, 'ndfia Harmonic');
Map.addLayer(maskYYSoil.selfMask(), {min:0, max: 2, palette: ['red', 'blue']}, 'maps');