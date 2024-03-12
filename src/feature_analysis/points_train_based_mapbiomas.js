var params = {
  asset_bacias: 'projects/mapbiomas-workspace/AMOSTRAS/col5/CAATINGA/ROIsXBaciasBalmin300v3/',
  asset_harmonics: 'projects/mapbiomas-arida/mosaic_harmonic',
}

var list_bacias = ee.List([

'759' ,'7611' , '766', '767',
'771' , '7612','7613','7614',
'7615',  '772', '773','774' , 
'775' , '777' ,'776' , '763',
'7618', '765' , '762', '746', 
'7619','7616' ,'7617', '744', 
'745' , '747' , '732', '743', 
'742' , '741' ,'752' , '753', 
'751' ,'754'  ,'756' , '755',
'758' , '757'

])

function ApplyReducers (img) {
var img_sum =  ee.Image(img).reduce(ee.Reducer.sum())
var img_median = ee.Image(img).reduce(ee.Reducer.median())
var img_mean = ee.Image(img).reduce(ee.Reducer.mean())
var img_vari = ee.Image(img).reduce(ee.Reducer.variance())
var img_mode = ee.Image(img).reduce(ee.Reducer.mode())
var img_stdDev = ee.Image(img).reduce(ee.Reducer.stdDev())
var img_max = ee.Image(img).reduce(ee.Reducer.max())
var img_min = ee.Image(img).reduce(ee.Reducer.min())
var img_amp = img_max.subtract(img_min).rename('amplitude')

return img_median
    .addBands(img_mean)
    .addBands(img_vari)
    .addBands(img_mode)
    .addBands(img_stdDev)
    .addBands(img_max)
    .addBands(img_min)
    .addBands(img_amp)
    .copyProperties(img)
}

list_bacias.evaluate(function(lsbacias){

lsbacias.forEach(function (bacia){

var list_years = ee.List.sequence(1985, 2019)

function coord_year (year){

var points_1 = ee.FeatureCollection(params.asset_bacias+bacia+'_0').filterMetadata('year', 'equals', year)

var points_2 = ee.FeatureCollection(params.asset_bacias+bacia+'_1').filterMetadata('year', 'equals', year) 

var points_bacia_year = points_1.merge(points_2)

var harmonic_col = ee.ImageCollection(params.asset_harmonics)
                    .filterMetadata('year', 'equals', year)
                    .map(ApplyReducers).mosaic()

var feat_points = ee.Image(harmonic_col)
                 .sampleRegions({
                  'collection': ee.FeatureCollection(points_bacia_year), 
                   'properties': ['class','year'], 
                   'scale': 30, 
                   'geometries': true
                   })

return feat_points

}

var points_year = list_years.map(coord_year)

points_year = ee.FeatureCollection(points_year).flatten()

Export.table.toDrive({
'collection': points_year,
'description': 'exportando_bacia'+bacia,
'folder': 'bacias_caatinga_doutorado',
'fileNamePrefix': 'bacia'+bacia
})

//Export.table.toAsset({
//  'collection': ee.FeatureCollection(points_year),
//  'description': 'exportando_bacia'+bacia,
//  'assetId': 'users/diegocosta/doctorate/points_train_min300_mapbiomas/'+bacia
//})

})

})
