// https://code.earthengine.google.com/f24b8212d09bb5d710d638ea32373bcc

var asset_grad = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/grades_to_mapping_soil';
var feat_gride_Br = ee.FeatureCollection(asset_grad);


var asset_region = 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2';
var feat_reg = ee.FeatureCollection(asset_region)

Map.addLayer(feat_reg, {color: 'red'}, 'region');
Map.addLayer(feat_gride_Br, {color: 'yellow'}, 'grade');