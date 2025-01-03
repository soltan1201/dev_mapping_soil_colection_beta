import glob
import os 
import copy
import pandas as pd


pathbase = os.getcwd()
path_Foldercsv = pathbase + '/SHP_pointsSoil/*'
allfileCSVs = glob.glob(path_Foldercsv)
print(f"we have {len(list(allfileCSVs))} files CSV")
dictRowPath = {}
for cc, npath in enumerate(allfileCSVs):
    print(f" # {cc}  >> {npath}")
    nameKey = npath.split('/')[-1][-10:-4]
    print(nameKey)

    lstKeydict = list(dictRowPath.keys())
    if nameKey not in lstKeydict:
        dicttmp = {}
        nyear = npath.split('/')[-1].split('_')[2]
        dicttmp[nyear] = npath
        dictRowPath[nameKey] = dicttmp

    else:
        dicttmp = copy.deepcopy(dictRowPath[nameKey])
        nyear = npath.split('/')[-1].split('_')[2]
        dicttmp[nyear] = npath
        dictRowPath[nameKey] = dicttmp

lstSerieC = []
for kkey, dictYY in dictRowPath.items():
    print("   >>> " + kkey)
    lstYY = [int(kk) for kk in dictYY.keys()]
    lstYY.sort()
    for nyear in lstYY:
        print(f"     {nyear} >> {dictYY[str(nyear)]}") 

    if len(lstYY) > 36:
        lstSerieC.append(kkey)


for rowkey in lstSerieC[:1]:
    print(f"   >>> {rowkey}")
    dictYY = dictRowPath[rowkey]
    for yearKey, nmpath in dictYY.items():
        print(f"     {yearKey} >> {nmpath}") 
        dftmp = pd.read_csv(nmpath)
        dftmp = dftmp.drop(['system:index', '.geo'], axis=1)    
        print(" colunas >> ", dftmp.columns)
        print(dftmp.shape)
        
        # Iterating over rows
        # for index, row in dftmp.iterrows():            
        #     print(row)

        for i in dftmp.index:  # Here, index defaults to 0, 1, 2
            print(f"Row {i}: {dftmp.loc[i]}")
        # building new
        print(dftmp.head(5)) 
        print(dftmp.tail(5)) 



