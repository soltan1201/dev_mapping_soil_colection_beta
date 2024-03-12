import ee
import sys
import collections
collections.Callable = collections.abc.Callable
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

def GetPolygonsfromFolder(assetFolder, sufixo):
  
    getlistPtos = ee.data.getList(assetFolder)
    print(f"deleting {len(getlistPtos)} files ")
    lstBacias = []
    for cc, idAsset in enumerate(getlistPtos): 
        path_ = idAsset.get('id') 
        lsFile =  path_.split("/")
        name = lsFile[-1]
        idBacia = name.split('_')[0]
        if idBacia not in lstBacias:
            lstBacias.append(idBacia)
        # print(name)
        # if str(name).startswith(sufixo): AMOSTRAS/col7/CAATINGA/classificationV
        if sufixo in str(name): 
            print("eliminando {}:  {}".format(cc, name))
            print(path_)
            # ee.data.deleteAsset(path_) 
    
    print(lstBacias)

# asset = {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsVeg2'}
asset = {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoil'}
# asset = {'id': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsManualSoilPtos'} # 
# asset ={'id' :'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsInt3CC'}
# asset ={'id' :'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsInt'}
# asset = {"id": "projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoil"}

GetPolygonsfromFolder(asset, '')  # 

