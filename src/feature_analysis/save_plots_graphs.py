from sklearn import svm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from random import randint
import glob
import sys
import os
import plotly.express as px
from plotly.subplots import make_subplots








if __name__ == '__main__':

    npath = 'version3/*.csv'
    lst_pathCSV = glob.glob(npath)
    dirCSVs = [(cc, kk) for cc, kk in enumerate(lst_pathCSV[:])]
    print(lst_pathCSV)

    # Create an array with the colors you want to use
    colors = ["#E87E1A","#EA9999"]

    # Set your custom color palette
    sns.set_palette(sns.color_palette(colors))

    dict_class = {
        '0': 'not Soil',
        '1': 'Soil'
    }

    for cc, mdir in dirCSVs[:]:        
        print("processing = ", mdir)
        newdf = pd.read_csv(namefile)
        newdf = newdf.drop(['system:index', '.geo'], axis=1)
