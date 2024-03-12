//Global parameters
var params = {
    harmonic_col: 'projects/mapbiomas-arida/mosaic_harmonic',
    caatinga: 'users/CartasSol/shapes/nCaatingaBff3000',
    points_lapig: 'projects/mapbiomas-workspace/PONTOS/100K_LAPIG_PRELIMINAR/pts_Caatinga',
    year: 2017,
    mapbiomas_mosaic:'projects/mapbiomas-workspace/MOSAICOS/workspace-c5',
    split: 0.3,
    dirPoints: 'projects/mapbiomas-workspace/VALIDACAO/MAPBIOMAS_100K_POINTS_utf8'
  }

  var list_class = [
    'Mangue',
    'Aquicultura',
    'Mineração',
    'Praia e Duna',
    'Cultura Anual',
    'Pastagem Cultivada',
    'Cultura Perene',
    'Não Observado',
    'Floresta Plantada',
    'Rio, Lago e Oceano',
    'Formação Savânica',
    'Infraestrutura Urbana',
    'Formação Florestal',
    'Formação Campestre',
    'Afloramento Rochoso',
    'Cultura Semi-Perene',
    'Outra Área Não Vegetada'
  ]

// function to Apply reducers on ImageCollection
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

    return ee.Image(img_median)
            .addBands(img_mean)
            .addBands(img_vari)
            .addBands(img_mode)
            .addBands(img_stdDev)
            .addBands(img_max)
            .addBands(img_min)
            .addBands(img_amp)
            .copyProperties(img)
}

var years = ee.List.sequence(2000, 2017)

ee.List(years).slice(0,1).evaluate(function(lsyears){
  
  lsyears.forEach(function (year){
    
    function split_points (classe){

        var featureCol = ee.FeatureCollection(params.dirPoints)
           .filter(ee.Filter.eq("BIOMA", "CAATINGA"))
           .filterMetadata('POINTEDITE', 'equals', '-')
           .filterMetadata('CLASS_'+year, 'equals', classe)

      featureCol = featureCol.randomColumn('random')

      featureCol = featureCol.filter(ee.Filter.lt('random', params.split))

      return featureCol
    }

    var filtered_points = list_class.map(split_points)

    filtered_points = ee.FeatureCollection(filtered_points).flatten()
    
    //print(filtered_points)
    
    var harmonic_col = ee.ImageCollection(params.harmonic_col)
                          .filterMetadata('year', 'equals', year)
                          .map(ApplyReducers).mosaic()
    
    // Get the values for all pixels in each polygon in the training.
    var training = harmonic_col.sampleRegions({
    // Get the sample from the polygons FeatureCollection.
    collection: filtered_points,
    // Keep this list of properties from the polygons.
    properties: ['CLASS_'+year],
    // Set the scale to get Landsat pixels in the polygons.
    scale: 30
    
    });

    Export.table.toDrive(training)
    
  })
})
