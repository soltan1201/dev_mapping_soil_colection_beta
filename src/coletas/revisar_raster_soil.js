

var param = {
    'input_solo': 'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
}

var raster_soil = ee.Image(param.input_solo);
print("show metadatas raster soil ", raster_soil)

var vis = {
    soil_red: {
        min: 1, max: 34,
        palette: ['ffe4aa','fca699','e2869b','c9729f','583b7e']
    }
}

raster_soil = raster_soil.reduce(ee.Reducer.sum());

Map.addLayer(raster_soil, vis.soil_red, 'soil')
