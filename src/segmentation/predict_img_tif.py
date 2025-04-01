#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
### importando librerias
import os
import sys
# import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
# from rasterio.plot import show
import numpy as np
from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
print("pathparent ", pathparent)
# pathparent = str('/home/superuser/Dados/projAlertas/proj_alertas_ML/src')
sys.path.append(pathparent)
import argparse

import tensorflow as tf
from tensorflow import keras
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

if tf.config.list_physical_devices('GPU'):
    physical_devices = tf.config.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(physical_devices[0], True) #This is a recomendation.
    print(tf.test.is_built_with_cuda())
    print(tf.config.list_physical_devices('GPU'))
else:
    print("GPU not found")

bandasInt = [
    'blue', 'red', 'nir', 'swir1', 'ndvi', 'ndsi', 'bsi',
    'gv', 'shade', 'soil', 'ndfia', 'msavi', 'ui', 'mbi',
    'evi'
]

#  lsFiles[0]
# Function to reshape array input
def reshape_input(array):
    shape = array.shape
    return array.reshape(shape[0], shape[1])# , 1
def processing_predict_img(name_img, path_mosaico, bandNumP):
    path_matrix1 = os.path.join(path_mosaico,name_img)
    try:
        raster_terreno = rasterio.open(path_matrix1)
        print("matrix load from ", path_matrix1)
        # print('CRS of Raster Data: ' + str(raster_terreno.crs))
        # print('Number of Raster Bands: ' + str(raster_terreno.count))
        # print('Interpretation of Raster Bands: ' + str(raster_terreno.colorinterp))
        print("reading parameters of metadata from image....")
        bandNum = raster_terreno.count
        height = raster_terreno.height
        width = raster_terreno.width
        # crs = raster_terreno.crs
        # transform = raster_terreno.transform
        shape = (height, width)
        print(f"image with height {height} | idth  {width} | bandNum {bandNum}")
        image_pred = []
        for cc, nband in enumerate(bandasInt):
            # print(f" #{cc}  band selected >> {nband}")
            image_pred.append(raster_terreno.read(cc + 1))
        image_pred = np.stack(image_pred)
        # deletar varaivel raster_terreno
        del raster_terreno
        # Predict image using the model
        # bandNumP = len(var_select)
        imgvector_pred = reshape_input(np.stack(image_pred).reshape(bandNumP, -1).T)
        print("reshape array to Vector >> ", imgvector_pred.shape)
        del image_pred
        imgvector_pred = np.nan_to_num(imgvector_pred, nan=0.0)
        print("print do primeiro pixel com todas as bandas \n", imgvector_pred[0,:])

        # Predict
        prediction = modelMond.predict(imgvector_pred, batch_size= 1000)
        prediction = np.argmax(prediction, 1)
        prediction = prediction.reshape(shape[0], shape[1])

        return prediction, True
    except:
        print("processing  FAILS ")
        return None, False



# path_base = '/content/drive/MyDrive/mapbiomas/layer_soil'

print(" loading model in drive folder ")
path_model = os.path.join(pathparent, 'models')
print(">>> ", path_model)
path_patchs = os.path.join(os.path.join(pathparent, 'dados'), 'patchs')
path_patchs_pred = os.path.join(os.path.join(pathparent, 'dados'), 'patchs_pred')

# path_folder = '/home/superuser/Dados/mapbiomas/dev_mapping_soil_colection_beta/src/dados/patchs'
parser = argparse.ArgumentParser()
parser.add_argument('names_folders', type=str,  
                    default= 'dados,patchs,patchs_pred', 
                    help="set the name of folders to read and save patchs images" 
            )
try:
    args = parser.parse_args()
    lstNamePath = args.names_folders
    partes = lstNamePath.split(",")
    tmpFolder = os.path.join(os.path.join(pathparent, partes[0]), partes[1])
    if str(path_patchs) != str(tmpFolder):
        print("<<<<<< change the path folder  >>>>>>>>>>>>>> ")
        path_patchs = tmpFolder
        path_patchs_pred = os.path.join()
except argparse.ArgumentTypeError as e:
    print(f"Invalid argument: {e}")

askHD = input('the datas are another HD?, digite true or false : ')
if askHD == 'true':
    new_path = input("please digit the complet dir of folder dataset >")
    if new_path:
        path_patchs = new_path

# sys.exit()
print(f' visit patch >> {path_patchs}')
print(f' visit patch Predict >> {path_patchs_pred}')
# Recreate the exact same model, including its weights and the optimizer
name_model = 'model_LSoil_22_03_25_month_all_15v_7000e.keras'
modelMond = keras.models.load_model(os.path.join(path_model, name_model))
modelMond.summary()

lstFilesPred = os.listdir(path_patchs_pred)
lstarrayPred = [arr_name.replace('.npy', '.tif') for arr_name in lstFilesPred]
print(f" we have {len(lstarrayPred)} array numpy processed ")
print("name files array numpy changes ", lstarrayPred[:5])
del lstFilesPred
# Listar arquivos no bucket
names_imgtif = os.listdir(path_patchs)
# Mostra os primeiros 5 arquivos
print("Arquivos no bucket:", names_imgtif[:5])  
numero_bnd = len(names_imgtif)
print(f" files total in repository {numero_bnd}")
lstNamesTIF = [name_tif for name_tif in names_imgtif if name_tif not in lstarrayPred]
del lstarrayPred
del names_imgtif
print(f" we have to process {len(lstNamesTIF)} patchs .... ")
# sys.exit()
for cc, name_img in enumerate(lstNamesTIF[:]):
    print(f"#{cc} processing {name_img}")
    arr_pred, to_save = processing_predict_img(name_img, path_patchs, numero_bnd)
    if to_save:
        print("shape array predict ", arr_pred.shape)
        # Salvar
        dir_name = os.path.join(path_patchs_pred, name_img.replace(".tif",".npy"))
        print(f"saving in >> {dir_name}")
        np.save(dir_name, arr_pred)
    

