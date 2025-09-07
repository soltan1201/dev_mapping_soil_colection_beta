#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import ee
import os
import sys
import json
import collections
collections.Callable = collections.abc.Callable

from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
print("pathparent ", pathparent)
# pathparent = str('/home/superuser/Dados/projAlertas/proj_alertas_ML/src')
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
from gee_tools import *
courrentAcc, projAccount = get_current_account()
print(f"projetos selecionado {courrentAcc} >>> {projAccount} <<<")

try:
    ee.Initialize( project= projAccount )
    print(' 🕸️ 🌵 The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


params = {
    'gradeLandsat': 'projects/mapbiomas-workspace/AUXILIAR/cenas-landsat-v2',         
    'region': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'assetMapbiomas100': 'projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v2',
    "asset_vigor_pastagem": 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_pasture_vigor_v1',
    "asset_gride_landsats": 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/grades_to_mapping_soil',
    'input_solo': 'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'classMapB' :   [3, 4, 5, 6, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNotSoil': [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'regionsSel': [
        '21','22','23','24',
        # '31','32','35','34','33', #
        # '60','51','52','53',
        # '41','42','44','45','46','47'
        # '11','12','13','14','15','16','17','18','19',
    ],
    'lstYear': [
        # 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997,
        # 1998, 1999,2000, 2001, 
        # 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
        2013, 2014, 2015, 2016,
        # 2017,  2018, 2019, # 2020,
        2021, 2022, 2023, 2024
    ],
    'numeroTask': 10,
    'numeroLimit': 100,
    'conta' : {
        '0': 'caatinga01',
        '10': 'caatinga02',
        '20': 'caatinga03',
        '30': 'caatinga04',
        '40': 'caatinga05',        
        '50': 'solkan1201',        
        '60': 'superconta'        
    }
  
}

# https://code.earthengine.google.com/8f738cdf510e475ab685e3a85e366aec


# // 4. Calcule o índice NDVI
def index_select(nImg):
    # var nImg = applyScaleFactors(image);
    ndvi = nImg.normalizedDifference(['nir', 'red']).rename('ndvi')
    ndvi = ndvi.add(1).multiply(10000).toUint16()
    
    # normalized difference soil index (NDSI)
    #(B7 - B2)/ (B7 + B2)
    ndsi = nImg.normalizedDifference(['swir1', 'blue']).rename('ndsi')
    ndsi = ndsi.add(1).multiply(10000).toUint16()

    bsi = nImg.expression(
                "float(((b('red') + b('swir1')) - (b('nir') + b('blue'))) / ((b('red') + b('swir1')) + (b('nir') + b('blue'))))"
            ).rename('bsi')
    bsi = bsi.add(1).multiply(10000).toUint16()
    
    evi = nImg.expression(
                "float(2.4 * (b('nir') - b('red')) / (1 + b('nir') + b('red')))"
                ).rename('evi')
    evi = evi.add(10).multiply(1000).toUint16()
    
    msavi =  nImg.expression(
                "float((2 * b('nir') + 1 - sqrt((2 * b('nir') + 1) * (2 * b('nir') + 1) - 8 * (b('nir') - b('red'))))/2)"
            ).rename('msavi')
    msavi = msavi.add(10).multiply(1000).toUint16()

    # UI	Urban Index	urban
    ui = nImg.expression(
            "float((b('swir2') - b('nir')) / (b('swir2') + b('nir')))")\
                .rename(['ui']).toFloat() 
    ui = ui.add(1).multiply(10000).toUint16()

    # MBI	Modified Bare Soil Index
    mbi = (nImg.expression(
            "float(((b('swir1') - b('swir2') - b('nir')) /" + 
                " (b('swir1') + b('swir2') + b('nir'))) + 0.5)")
                    .rename(['mbi']).toFloat() 
        )
    mbi = mbi.add(1).multiply(10000).toUint16()

    vdvi = (nImg.expression(
            "float((2 * b('green') - b('red') - b('blue')) /" + 
                " (2 * b('green') + b('red') + b('blue')))")
                    .rename(['vdvi']).toFloat() 
        )
    vdvi = vdvi.add(1).multiply(10000).toUint16()
    
    # NDBI=(TM5−TM4)/(TM5+TM4) 
    # Normalized Diﬀerence Built-up Index (NDBI) 
    ndbi = (nImg.expression(
            "float( (b('swir1') - b('red')) / (b('swir1') + b('red')) )")
                    .rename(['ndbi']).toFloat() 
        )
    ndbi = ndbi.add(1).multiply(10000).toUint16()

    # mid-infrared index maps
    # (TM5 - TM7) / (TM5 + TM7)
    # (swir1 - swir2) / (swir1 + swir2)
    miim = (nImg.expression(
            "float((b('swir1') - b('swir2')) / (b('swir1') + b('swir2')))")
                .rename(['miim']).toFloat()) 
    miim = miim.add(1).multiply(10000).toUint16()

    # IBI (Index-based Built-Up Index) [1]  
    # (2 * B5 / (B5 + B4) - [B4/(B4 + B3) + B2/(B2+B5)])/ (2 * B5 / (B5 + B4) + [B4/(B4 + B3) + B2/(B2+B5)])
    ibi = (nImg.expression(
            "float((((2 * b('swir1')) / (b('swir1') + b('nir'))) - (b('nir') / (b('nir') + b('red'))) + ( b('green') / (b('swir1') + b('green')))) /" +     
                 " (((2 * b('swir1')) / (b('swir1') + b('nir'))) + (b('nir') / (b('nir') + b('red'))) + ( b('green') / (b('swir1') + b('green')))))")
                    .rename(['ibi']).toFloat() 
        )
    ibi = ibi.add(1).multiply(10000).toUint16()

    # Bare Soil Index (BI) ok
    # (swir2 + red) - (nir + blue) / ((swir2 + red) + (nir + blue))
    bi = (nImg.expression(
            "float(((b('swir2') + b('red')) - (b('nir') + b('blue')))/ ((b('swir2') + b('red')) + (b('nir') + b('blue'))))")
                    .rename(['bi']).toFloat() 
        )
    bi = bi.add(1).multiply(10000).toUint16()

    # Hyperspectral Bare Soil Index (HBSI)
    # (swir2 + green) - (nir + blue) / ((swir2 + green) + (nir + blue))
    hbsi = (nImg.expression(
            "float(((b('swir2') + b('green')) - (b('nir') + b('blue')))/ ((b('swir2') + b('green')) + (b('nir') + b('blue'))))")
                    .rename(['hbsi']).toFloat() 
        )
    hbsi = hbsi.add(1).multiply(10000).toUint16()

    # soil organic matter (SOM)
    #2.9470429299 − 0.0019428105·Green + 0.0001621927 ·SWIR1
    # som = (nImg.expression(
    #         "2.9470429299 − (b('green') * 0.0019428105 ) + (b('swir1') * 0.003522337)")
    #             .rename(['som']).toFloat())
    # som = som.add(1).multiply(10000).toUint16()

    # # silt (lodo)
    # # 28.432522580 + 0.010296555 ∙ Red − 0.003522337 ∙ SWIR1
    # silt = (nImg.expression(
    #         "float(28.432522580 + 0.010296555 * b('red') - 0.003522337 * b('swir1'))")
    #             .rename(['silt']).toFloat())
    # silt = silt.add(1).multiply(10000).toUint16()

    imgM = nImg.multiply(10000)
    return (imgM.addBands(ndvi).addBands(ndsi)
                .addBands(bsi).addBands(evi)
                .addBands(msavi).addBands(ui)
                .addBands(vdvi).addBands(ndbi)
                .addBands(bi).addBands(hbsi)
                .addBands(miim).addBands(ibi)
                # .addBands(som).addBands(silt)
                .addBands(mbi).toUint16()
                .copyProperties(nImg)
        )

def GET_NDFIA(IMAGE):
        
    lstBands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    lstFractions = ['gv', 'shade', 'npv', 'soil', 'cloud']
    endmembers = [            
        [0.05, 0.09, 0.04, 0.61, 0.30, 0.10], #/*gv*/
        [0.14, 0.17, 0.22, 0.30, 0.55, 0.30], #/*npv*/
        [0.20, 0.30, 0.34, 0.58, 0.60, 0.58], #/*soil*/
        [0.0 , 0.0,  0.0 , 0.0 , 0.0 , 0.0 ], #/*Shade*/
        [0.90, 0.96, 0.80, 0.78, 0.72, 0.65]  #/*cloud*/
    ];

    fractions = ee.Image(IMAGE).select(lstBands).unmix(
                                    endmembers= endmembers 
                                    # sumToOne= True, 
                                    # nonNegative= True
                                ).float()
    fractions = fractions.rename(lstFractions)
    # // print(UNMIXED_IMAGE);
    # GVshade = GV /(1 - SHADE)
    # NDFIa = (GVshade - SOIL) / (GVshade + )
    NDFI_ADJUSTED =( fractions.expression(
                            "float(((b('gv') / (1 - b('shade'))) - b('soil')) / ((b('gv') / (1 - b('shade'))) + b('npv') + b('soil')))" )
                            .rename('ndfia')
                    )

    NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()
    RESULT_IMAGE = (ee.Image(index_select(IMAGE)) ## adicionando indices extras
                                .addBands(fractions.multiply(10000).toUint16())
                                .addBands(NDFI_ADJUSTED))

    return ee.Image(RESULT_IMAGE).toUint16()

def getIntervalo(nyear):
    intervalo = []
    if nyear == 1985:
        intervalo = [nyear, nyear + 1, nyear + 2]
    elif nyear > 2022:
        intervalo = [2021, 2022, 2023]
    else:
        intervalo = [nyear - 1, nyear, nyear + 1]

    return intervalo

 # salva ftcol para um assetindexIni
# lstKeysFolder = ['cROIsN2manualNN', 'cROIsN2clusterNN'] 
def save_ROIs_toAsset(collection, name):
    # assetIds = 'projects/geo-data-s/assets/ROIsSoil/' + name
    assetIds = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/ROIsSoilexposto/' + name
    optExp = {
        'collection': collection,
        'description': name,
        'assetId': assetIds
    }
    task = ee.batch.Export.table.toAsset(**optExp)

    optExp = {
        'collection': collection,
        'description': name,
        'folder': 'ROIS_soilnew'
    }
    # task = ee.batch.Export.table.toDrive(**optExp)
    task.start()
    print("exportando ROIs da bacia $s ...!", name)

def gerenciador(cont):
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in params['conta'].keys()]    
    print(numberofChange)
    
    if str(cont) in numberofChange:
        print(f"inicialize in account #{cont} <> {params['conta'][str(cont)]}")
        switch_user(params['conta'][str(cont)])
        projAccount = get_project_from_account(params['conta'][str(cont)])
        try:
            ee.Initialize(project= projAccount) # project='ee-cartassol'
            print('The Earth Engine package initialized successfully!')
        except ee.EEException as e:
            print('The Earth Engine package failed to initialize!') 

        tarefas = tasks(
            n= params['numeroTask'],
            return_list= True)
        
        for lin in tarefas:   
            print(str(lin))         
            # relatorios.write(str(lin) + '\n')
    
    elif cont > params['numeroLimit']:
        return 0
    cont += 1    
    return cont

print("=====================  INICIALIZANDO PROCESSOS  =================================")
# exemplo filtrado 
# https://code.earthengine.google.com/343381e6f097b46363cff77fe44d4c2d
bandasInt = [
    'blue', 'red', 'nir', 'swir1', 'ndvi', 'ndsi', 'bsi', 
    'gv', 'shade', 'soil', 'ndfia', 'msavi', 'ui', 'mbi',
    'vdvi', 'ndbi','evi', 'bi', 'hbsi','miim','ibi', 'class'
]
contAcount = 0
# regionSelect = 31
lst_regions = [int(reg) for reg in params['regionsSel']]
# load path row of regions dict 
file_path = os.path.join(pathparent, "dados/dict_regions_grades.json")
dict_regions = {}
try:
    with open(file_path, 'r', encoding='utf-8') as arquivo_json:
        dict_regions = json.load(arquivo_json)
        print(f"\n Conteúdo do arquivo {file_path} carregado com {len(list(dict_regions.keys()))} regions ")
        print("region # 1 >> ", list(dict_regions.keys())[0])
except FileNotFoundError:
    print("O arquivo 'dados.json' não foi encontrado.")

except json.JSONDecodeError:
    print("Erro ao decodificar o JSON.")
# sys.exit()
# load shp of grides from landsat constelation
shp_grades_landsat = (ee.FeatureCollection(params["asset_gride_landsats"])
                            .map(lambda feat: feat.set('id_code', 1)))

for regionSelect in lst_regions[:]:
    print('regions >> ', regionSelect)
    regionSel = ee.FeatureCollection(params['region']).filter(ee.Filter.eq('region', regionSelect))
    total_pr = len(dict_regions[str(regionSelect)])
    for cc, path_row in enumerate(dict_regions[str(regionSelect)]):
        print(f' # {cc}/{total_pr} processing path_row {path_row}')
        # imgMaskReg = regionSel.reduceToImage(['region'], ee.Reducer.first()).gt(1)
        # print("region selecionadas ", regionSel.first().get('region').getInfo())
        # print(regionSel.first().get('region').getInfo())

        shp_grad_reg = shp_grades_landsat.filter(ee.Filter.eq('TILE_T', path_row))
        imgMask_pr = shp_grad_reg.reduceToImage(['id_code'], ee.Reducer.first()).gt(0)
        print("grade selecionada ", shp_grad_reg.first().get('TILE_T').getInfo())
        # print(regionSel.first().get('region').getInfo())

        # utilizaremos mapbiomas para coletar areas de solos que podem ser balizadas por essa área no ndfia
        mMapbiomas = ee.Image(params['assetMapbiomas100']).updateMask(imgMask_pr)
        print("************* raste MAPBIOMAS carregado **********************")
        # print(mMapbiomas.bandNames().getInfo())
        # sys.exit()
        if regionSelect < 25:
            print(" ------ coletando na região da Caatinga ---- ")
            layer_soil = ee.Image(params['input_solo']).unmask(0).updateMask(imgMask_pr)
            # Maximo de área de solo exposto em toda a serie historica
            mask_max_solo = layer_soil.reduce(ee.Reducer.sum()).gt(0)
            # print(layer_soil.bandNames().getInfo())
        else:
            # class soil in mapbiomas maps 
            mask_max_solo = mMapbiomas.eq(25).reduce(ee.Reducer.sum()).gt(0)

        # sys.exit()
        for yyear in params['lstYear'][:1]:
            mapaYY = mMapbiomas.select('classification_' + str(yyear))
            lstIntervaloYY = getIntervalo(yyear)
            print(f'processing year {yyear} and list >> {lstIntervaloYY}')

            lstIntBandsMB = ['classification_' + str(kk) for kk in lstIntervaloYY]
            lstIntBandsSoil = [f"Caatinga_{kk}_classification_{kk}" for kk in lstIntervaloYY]

            if regionSelect < 25:
                # camada de soil sendo selecionada
                # selecionando a clase de solo para valor 1            
                print('lista de bandas selecionadas para o intervalo ', lstIntBandsSoil)
                if int(yyear) < 2017:
                    maskYYSoil = layer_soil.select(lstIntBandsSoil).reduce(ee.Reducer.sum()).eq(3)
                else:
                    lstBND = ['Caatinga_2016_classification_2016', 'Caatinga_2017_classification_2017', 'Caatinga_2018_classification_2018']
                    maskYYSoil = layer_soil.select(lstBND).reduce(ee.Reducer.sum()).eq(3)
            else:
                # selecionando a clase de solo para valor 1            
                maskYYSoil = mMapbiomas.select(lstIntBandsMB).eq(25).reduce(ee.Reducer.sum()).eq(3)
            # sys.exit()
            # # vamos usar a camada de Vigor da pastagens 
            # # https://code.earthengine.google.com/c314d51721046e6ed6f69af502ee1428
            # usaremos faixas de NDFIa
            # https://code.earthengine.google.com/0434c7ac279cf361faae298a46b57f42

            # juntando as duas classes 
            # maskYYSoil = maskYYSoil.add(maskNotSoil).selfMask()
            for mmonth in range(1, 13):
                data_inicial = ee.Date.fromYMD(yyear, mmonth, 1)
                imColMonth = (ee.ImageCollection(params['asset_collectionId'])
                                .filterBounds(shp_grad_reg.geometry())
                                .filterDate(data_inicial, data_inicial.advance(1, 'month'))
                                .select(params['bnd_L']).first()
                                .updateMask(imgMask_pr)
                            )
                print(" Loaded Imagem Collection Month  ", imColMonth.bandNames().getInfo())

                #// Create a cloud-free, most recent value composite.
                # sys.exit()
                monthNDFIa = GET_NDFIA(imColMonth)
                print("lista de bandas  ", monthNDFIa.bandNames().getInfo())
                # sys.exit()
                # faxeamento do NDFIa para as áreas de coletas 
                # definindo intervalos de faixas 
                faixa_min = 9000
                faixa_max = 15000  #10500
                faixa_minSoil = 6500
                areas_col_notSoil = monthNDFIa.select('ndfia').gte(faixa_max).And(mask_max_solo.eq(0))        
                
                # areas_col_transic = (monthNDFIa.select('ndfia').lte(faixa_min)
                #                         .And(monthNDFIa.select('ndfia').gte(faixa_minSoil))
                #                 )
                # areas_col_Soil = monthNDFIa.select('ndfia').lte(faixa_minSoil)
                # areas_col_Soil = areas_col_Soil.multiply(1)   # ele já é 1
                # areas_col_transic = areas_col_transic.And(mask_max_solo.eq(0)).multiply(2)
                areas_col_notSoil = areas_col_notSoil.multiply(2)
                

                # if regionSelect < 25:
                #     # ele vai restringir mais ainda a áreas se suposto solo
                #     maskYYSoil = maskYYSoil #.And(areas_col_Soil)
                # else:
                #     # ele vai ampliar mais ainda a áreas se suposto solo
                #     # maskYYSoil = maskYYSoil.Or(areas_col_Soil)
                #     # tirar todas as áreas de interseção com as áreas de transcisão e não solo
                #     # areas_col_transic = areas_col_transic.multiply(maskYYSoil.eq(0))
                #     # tirar todas as áreas de interseção com as áreas de transcisão e não solo
                #     areas_col_notSoil = areas_col_notSoil.multiply(maskYYSoil.eq(0))

                # juntando todas as mascaras e tendo as classes 0, 1, 2, 3 separadas 
                maskYYSoiljoined = maskYYSoil.add(areas_col_notSoil)   # .add(areas_col_transic)
                MosaicoClean = (monthNDFIa.toFloat().addBands(maskYYSoiljoined.rename('class'))
                                    .select(bandasInt).updateMask(maskYYSoiljoined.gt(0))
                                    .selfMask()
                                    )
                # TILE_T= path_row,
                ptosTemp = MosaicoClean.stratifiedSample(
                                            numPoints= 500, 
                                            classBand= 'class', 
                                            region= shp_grad_reg.geometry(),                                 
                                            scale= 30,                                     
                                            dropNulls= True,
                                            geometries= True
                                        )
                # print("número de pontos ", ptosTemp.size().getInfo())
                # salvando o processo 
                save_ROIs_toAsset(ptosTemp, f'rois_{regionSelect}_{path_row}_{yyear}_{mmonth}')
                #  contAcount = gerenciador(contAcount) 
    sys.exit()