# !/usr/bin/env python
import glob
import pandas as pd
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from itertools import starmap
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import StratifiedKFold

from sklearn.pipeline import Pipeline
from sklearn.feature_selection import RFE
from sklearn.feature_selection import RFECV
from sklearn.linear_model import Perceptron
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from multiprocessing import Pool
# def plot_selectKBest(XValues, sscore):
#     X_indices = np.arange(XValues.shape[-1])
#     plt.figure(1)
#     plt.clf()
#     plt.bar(X_indices - 0.05, sscore, width=0.2)
#     plt.title("Feature univariate score")
#     plt.xlabel("Feature number")
#     plt.ylabel(r"Univariate score ($-Log(p_{value})$)")
#     plt.show()

# def Univariate_feature_selectionF_test (X_train, y_train):
#     selector = SelectKBest(f_classif, k=4)
#     selector.fit(X_train, y_train)
#     scores = -np.log10(selector.pvalues_)
#     scores /= scores.max()
#     plot_selectKBest(X_train, scores)
colunas =  [
    'blue', 'bsi', 'evi', 'gv', 'mbi', 'msavi', 'ndbi', 'ndsi', 'ndvi', 'nir', 'red', 'shade', 'soil', 'swir1', 'ui', 'vdvi'
]

analisesbyRegionOnly = True


# get a list of models to evaluate
def get_models():
    models = dict()    
    # numberVar = len(colunas) - 5
    # building the three models 
    # cart# , n_features_to_select= numberVar
    # rfe = RFECV(estimator=DecisionTreeClassifier())
    # model = RandomForestClassifier()
    # models['cart'] = Pipeline(steps=[('s',rfe),('m',model)])
    # rf
    rfe = RFECV(estimator=RandomForestClassifier())
    model = DecisionTreeClassifier()
    models['rf'] = Pipeline(steps=[('s',rfe),('m',model)])
    # gbm
    rfe = RFECV(estimator=GradientBoostingClassifier())
    model = RandomForestClassifier()
    models['gbm'] = Pipeline(steps=[('s',rfe),('m',model)])
    #SVM
    # rfe = RFECV(estimator=SVC())
    # model = RandomForestClassifier()
    # models['svc'] = Pipeline(steps=[('s',rfe),('m',model)])

    return models

# evaluate a give model using cross-validation
def evaluate_model(nmodel, X, y):
    # cv = RepeatedStratifiedKFold(n_splits= 1, n_repeats=3, random_state=1)
    skf = StratifiedKFold(n_splits=5)
    scores = cross_val_score(nmodel, X, y, scoring='accuracy', cv=skf, n_jobs=2)
    return scores

def building_process_Model(X_train, y_train):
    # get the models to evaluate
    models = get_models()
    # evaluate the models and store results
    
    nmodel = starmap(lambda name, model: evaluate_model(model, X_train, y_train), models.items())
    for cc in range(10):
        scores = next(nmodel)
        print("Score ")
        print(scores)
        results.append(scores)
        name = models.keys()[cc]
        print("name = ", name)
        names.append(name)
        print('>%s %.3f (%.3f)' % (name, np.mean(scores), np.std(scores)))
    # plot model performance for comparison
    plt.boxplot(results, labels=names, showmeans=True)
    plt.show()

# loading table of ROIs and begining testing analises
def load_table_to_processing(cc, dir_fileCSV):
    df_tmp = pd.read_csv(dir_fileCSV)
    print(f"# {cc} loading train DF {df_tmp[colunas].shape} and ref {df_tmp['class'].shape}")
    X_train, X_test, y_train, y_test = train_test_split(df_tmp[colunas], df_tmp['class'], test_size=0.1, shuffle=False)


    # print(df_tmp.columns)
    # building_process_Model(df_tmp[colunas], df_tmp['class'])
    results, names = list(), list()
    # get the models to evaluate
    models = get_models()

    for name, model in models.items():
        scores = evaluate_model(model, X_train, y_train)
        print('>%s %.3f (%.3f)' % (name, np.mean(scores), np.std(scores)))
        print(scores)

def load_table_to_process(cc, dir_fileCSV, showPlot= True):
    df_tmp = pd.read_csv(dir_fileCSV)
    print(f"# {cc} loading train DF {df_tmp[colunas].shape} and ref {df_tmp['classe'].shape}")
    # X_train, X_test, y_train, y_test = train_test_split(df_tmp[colunas], df_tmp['class'], test_size=0.1, shuffle=False)

    min_features_to_select = 2
    print("get variaveis")    
    # gbm    
    skf = StratifiedKFold(n_splits=3)
    # model = RandomForestClassifier()
    model = GradientBoostingClassifier(n_estimators=35, learning_rate=1.5, max_depth=2, random_state=10)
    rfecv = RFECV(
            estimator=model,
            step=1,
            cv= skf,
            scoring= 'accuracy',
            min_features_to_select= min_features_to_select,
            n_jobs=6,
            importance_getter= 'auto'
        )

    rfecv.fit(df_tmp[colunas], df_tmp['classe'])
    print(f"Optimal number of features: {rfecv.n_features_}")
    print("ranking ", rfecv.ranking_)
    print("")
    print("Support ", rfecv.support_)

    if showPlot:
        plot_scoreImportanceBands(rfecv, min_features_to_select, dir_fileCSV)

    return rfecv.ranking_


def load_table_concate_to_process(dirFilesCSV, nameReg, showPlot= True):
    df_from_each_file = []
    for cc, pathcsv in enumerate(dirFilesCSV):
        df_tmp = pd.read_csv(pathcsv)
        print(f"# {cc} loading train DF {df_tmp[colunas].shape} and ref {df_tmp['class'].shape}")
        df_tmp = df_tmp.drop(['system:index', '.geo'], axis=1)
        df_tmp = df_tmp[df_tmp['class'] != 5]
        df_from_each_file.append(df_tmp)    

    concat_df  = pd.concat(df_from_each_file, axis=0, ignore_index=True)
    print("temos {} filas ".format(concat_df.shape))

    # X_train, X_test, y_train, y_test = train_test_split(df_tmp[colunas], df_tmp['class'], test_size=0.1, shuffle=False)

    min_features_to_select = 4
    print("get variaveis")    
    # gbm    
    skf = StratifiedKFold(n_splits=3)
    # model = RandomForestClassifier()
    model = GradientBoostingClassifier(n_estimators=65, learning_rate=1.5, max_depth=2, random_state=10)
    rfecv = RFECV(
            estimator=model,
            step=1,
            cv= skf,
            scoring= 'accuracy',
            min_features_to_select= min_features_to_select,
            n_jobs=6,
            importance_getter= 'auto'
        )

    rfecv.fit(concat_df[colunas], concat_df['class'])
    print(f"Optimal number of features: {rfecv.n_features_}")
    print("ranking ", rfecv.ranking_)
    print("")
    print("Support ", rfecv.support_)

    if showPlot:
        plot_scoreImportanceBands(rfecv, min_features_to_select, nameReg)

    return rfecv.ranking_


def plot_scoreImportanceBands(rfecvModel, min_feats_selected, myDirFile):
    n_scores = len(rfecvModel.cv_results_["mean_test_score"])
    plt.figure()
    plt.xlabel("Number of features selected")
    plt.ylabel("Mean test accuracy")
    plt.errorbar(
        range(min_feats_selected, n_scores + min_feats_selected),
        rfecvModel.cv_results_["mean_test_score"],
        yerr=rfecvModel.cv_results_["std_test_score"],
    )
    plt.title("Recursive Feature Elimination \nwith correlated features")
    dirSave = myDirFile.replace('version3', 'myPlots')
    dirSave = dirSave.replace('csv', 'png')
    plt.savefig( dirSave, dpi=(250), bbox_inches='tight')    
    # plt.show()
    plt.close()

def getNameFeature (lst_features):
    lstBands = []
    for cc, numbImp in enumerate(lst_features):
        if numbImp < 4:
            lstBands.append(colunas[cc])

    return lstBands

def getFeatureSeleciontion_byRegionYear(lstPathCsvs):
    for cc, mdir in lstPathCsvs[:]:        
        print("processing = ", cc, " <=> " , mdir)
        region = mdir.replace('version3/', '').split('_')[-2]
        myear = mdir.replace('version3/', '').split('_')[-1]

        lst_rank = load_table_to_process(cc, mdir, True)
        print("lista ordenadas de bandas processadas ", lst_rank)
        lstNameBands = getNameFeature(lst_rank)
        print("Bandas importantes \n ==> ", lstNameBands)
        newdir = mdir[:-4] + '.txt'
        filesave = open(newdir, 'w+')
        for band_rank in lstNameBands:
            filesave.write(band_rank + '\n')
        
        filesave.close()
        time.sleep(60)

def getFeatureSeleciontion_byRegion(lstPathCsvs):
    lstReg = []
    # rois_shp_CERRADO_1992_31_manual        
    for cc, mdir in lstPathCsvs[:]:    
        region = mdir.replace('version3/', '').split('_')[-2]
        # myear = mdir.replace('version3/', '').split('_')[-1]
        if region not in lstReg:
            lstReg.append(region)

    print("we try to work with {} regions \n ==> {}".format(len(lstReg), lstReg))

    for reg in lstReg:
        nameProc = 'rois_coleta_soil_' + str(reg)
        lstDirProc = []
        for cc, mdir in lstPathCsvs[:]:      
            if  str(reg) in mdir:  
                print("processing region => ", reg, " <=> " , mdir)    
                lstDirProc.append(mdir)    

        lst_rank = load_table_concate_to_process(lstDirProc, nameProc, True)
        print("lista ordenadas de bandas processadas ", lst_rank)

        # sys.exit()
        lstNameBands = getNameFeature(lst_rank)
        print("Bandas importantes \n ==> ", lstNameBands)
        newdir = nameProc + '.txt'
        filesave = open(newdir, 'w+')

        for band_rank in lstNameBands:
            filesave.write(band_rank + '\n')
        
        filesave.close()
        time.sleep(120)

if __name__ == '__main__':

    # /home/superusuario/Dados/mapbiomas/col8/features/
    npath = 'roisSoils/*.csv'
    lst_pathCSV = glob.glob(npath)
    dirCSVs = [(cc, kk) for cc, kk in enumerate(lst_pathCSV[:])]
    print(lst_pathCSV)
    # # Create a pool with 4 worker processes
    # with Pool(4) as procWorker:
    #     # The arguments are passed as tuples
    #     result = procWorker.starmap(
    #                     load_table_to_processing, 
    #                     iterable= dirCSVs, 
    #                     chunksize=5)

    if analisesbyRegionOnly:        
        getFeatureSeleciontion_byRegion(dirCSVs)

    # else:        
    #     getFeatureSeleciontion_byRegionYear(dirCSVs)