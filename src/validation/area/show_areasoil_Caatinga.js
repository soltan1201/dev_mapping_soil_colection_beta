//https://code.earthengine.google.com/5ce329648a09948a62504b919e78d983

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
    'diference': {
        min: -1, 
        max: 2, 
        palette: ['#2532e4',"#FFFFFF",'#ffefc3', '#d4271e']
    },
    
} ;

var dictNameBiome = {
    'Amazônia': 'AMAZONIA', 
    'Cerrado': 'CERRADO',
    'Caatinga': 'CAATINGA',
    'Mata Atlântica': 'MATAATLANTICA', 
    'Pampa': 'PAMPA',
    'Pantanal': 'PANTANAL'
};
var dictIdbiomas = {
    'Amazônia': 1,
    'Caatinga': 5,
    'Cerrado': 4,
    'Mata Atlântica': 2,
    'Pampa': 6,
    'Pantanal': 3
};
var param = {
    'classmappingV4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    'classmappingV0Caat':  'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'asset_colection_9': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',
    'asset_biomas_raster': 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'asset_biomas_shp': 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019',
    'asset_estados_shp': 'projects/mapbiomas-workspace/AUXILIAR/estados-2016',
    'asset_estados_raster': 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2', 
    'bandas': ['red_median', 'green_median', 'blue_median'], 
};

var bioma_select= 'Caatinga';
print("valor bioma id ", parseInt(dictIdbiomas[bioma_select]));
var layerSoil = null;
var nyear =  2015;
var syear =  '2015';
var geocuf = '22';
var biomaraster = ee.Image(param['asset_biomas_raster']).eq(parseInt(dictIdbiomas[bioma_select]));
var mapbiomasC9 = ee.Image(param['asset_colection_9']).updateMask(biomaraster)
var Mosaicos = ee.ImageCollection(param.assetIm)
            .filter(ee.Filter.eq('biome', dictNameBiome[bioma_select]))
            .filter(ee.Filter.eq('year', nyear)).select(param.bandas); 
Mosaicos = Mosaicos.mosaic().updateMask(biomaraster)

layerSoil = ee.Image(param['classmappingV0Caat']).updateMask(biomaraster);
print(" para caatinga ver as bandas ", layerSoil.bandNames());

var limitBioma = ee.FeatureCollection(param['asset_biomas_shp'])
                .filter(ee.Filter.eq("featureid", dictIdbiomas[bioma_select]));

print(" limite do biomas ", limitBioma.size().getInfo());

var banda_sel = "Caatinga_" + syear + "_" + "classification_" + syear;
var tmpSoil = layerSoil.select(banda_sel);
var mapbiomasYY = mapbiomasC9.select("classification_" + syear);
print(" mapbiomasYY ", mapbiomasYY);
var tempSoilMapbiomas = mapbiomasYY.eq(25).add(mapbiomasYY.eq(23)).gte(1);
var layerDiference = tempSoilMapbiomas.multiply(2).subtract(tmpSoil);
var maskSoil = layerDiference.neq(0);
Map.addLayer( Mosaicos, visualizar.visMosaic, 'Mosaic Col9 ' + syear);
Map.addLayer(limitBioma, {color: 'yellow'}, 'bioma', false);

Map.addLayer(tmpSoil, {palette: 'red'}, 'soil');
Map.addLayer(tempSoilMapbiomas, {palettes: '#db4d4f'}, 'soil_mapbiomas');
Map.addLayer(layerDiference.updateMask(maskSoil), visualizar.diference, 'soil_diference');