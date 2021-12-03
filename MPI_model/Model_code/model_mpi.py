from sklearn.base import BaseEstimator, ClassifierMixin

# Add more packages as required

# import all classfier methods and metrics
from sklearn import ensemble
from sklearn import tree
from sklearn import linear_model
from sklearn import neighbors
from sklearn import svm

from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier

#import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn import clone
from sklearn import metrics

#import selection method
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split

from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import LeaveOneOut

#import validation and others
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.tree import export_graphviz

#other utility packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot
from random import randint
from scipy.spatial import distance
import seaborn as sns

import os

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

from tqdm import tqdm_notebook as tqdm
import time

from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer

from sklearn.metrics import roc_auc_score
from sklearn import metrics
from sklearn.metrics import confusion_matrix

import timeit
import math
from collections import Counter
from sklearn.impute import SimpleImputer

from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder

from sklearn.preprocessing import MinMaxScaler

import pickle
import sys

def merge_data(dfleft, dfright, key):
  print("shape of MPI df:", dfleft.shape)
  print("shape of PC df:", dfright.shape)
  return dfleft.merge(dfright, how='left', on=key)

def load_data(path, pathPc):
    mpidf = pd.read_csv(path)
    pcdf = pd.read_csv(pathPc)
    merge_df = merge_data(mpidf, pcdf, 'HN')
    return merge_df

def load_data2(path):
    mpidf = pd.read_csv(path)
    return mpidf

def merge_data(dfleft, dfright, key):
  print("shape of MPI df:", dfleft.shape)
  print("shape of PC df:", dfright.shape)
  return dfleft.merge(dfright, how='left', on=key)

def load_data(path, pathPc):
    mpidf = pd.read_csv(path)
    pcdf = pd.read_csv(pathPc)
    merge_df = merge_data(mpidf, pcdf, 'HN')
    return merge_df

def fill_null(X):
  imp = SimpleImputer(missing_values=np.nan, strategy='mean')
  imp.fit(X)
  SimpleImputer()
  X_trans = pd.DataFrame(0, index=np.arange(len(X)), columns = X.columns)
  X_trans.loc[:, X.columns] = imp.transform(X)
  return X_trans

def plot_missing(df):
  plt.figure(figsize=(20,12))
  sns.heatmap(df.isna(), cbar=False, cmap='viridis', yticklabels=False)

def clean_data(df):
    print("before drop", df.shape)
    #1. drop  features (HN, Date, CAG Lab)
    df = df.drop("HN", axis=1)
    df = df.drop("Date", axis=1)
    df = df.drop("CAG_LAB", axis=1)
    print("after drop", df.shape)

    #edit feat
    #1. Gender
    df['Gender'].loc[(df['Gender'].str.contains("m") > 0) | (df['Gender'].str.contains("M") > 0)] = 'M'
    df['Gender'].loc[(df['Gender'].str.contains("f") > 0) | (df['Gender'].str.contains("F") > 0)] = 'F'

    print('F',df['Gender'].loc[(df['Gender'] == 'F')].count())
    print('M',df['Gender'].loc[(df['Gender'] == 'M')].count())

    df['Gender'] = df['Gender'].fillna('F')

    # 2. remaining
    df_pc = df.iloc[:, 115:]
    
    #PC features
    for key,value in df_pc.dtypes.iteritems():
      df[key] = pd.to_numeric(df[key], errors='coerce')
      if(value == "object"):
        df[key].loc[(df[key] != '0') & (df[key] != '1')] = '0'
        df[key] = df[key].astype(int)
        # print("loop1:",key+":",df[key].dtypes)
      elif(value == "float"):
        df[key].loc[(df[key] != 0) & (df[key] != 1)] = 0
        df[key] = df[key].astype(int)
        # print("loop1:",key+":",df[key].dtypes)

    #other features
    df2 = df[[c for c in df if c not in ['Gender']]]
    for key,value in df2.dtypes.iteritems():
      df[key] = pd.to_numeric(df[key], errors='coerce')
      if(value == "float"):
        pass
        # df[key] = df[key].astype('category')
        print("loop2:",key+":",df[key].dtypes)
      elif(value == "object" and key != 'Gender'):
        df[key] = pd.to_numeric(df[key], errors='coerce')
        # df[key] = df[key].astype('category')
        print("loop2:",key+":",df[key].dtypes)
    plot_missing(df)
    df.iloc[:, :113] = fill_null(df.iloc[:, :113])
    df.iloc[:, 114:] = fill_null(df.iloc[:, 114:])
    plot_missing(df)
    return df

def create_cag(df):
  # Assumption : if LADCAG or LCXCAG or RCACAG = 1, Also CAG = 1
  df.loc[(df.LADCAG == 1) | (df.LCXCAG == 1) | (df.RCACAG == 1), 'CAG'] = 1
  df.loc[(df.LADCAG != 1) & (df.LCXCAG != 1) & (df.RCACAG != 1), 'CAG'] = 0
  df['CAG'] = df.CAG.astype(int)
  return df

def partition_data(df):
    X = df[[c for c in df if c not in ['LADCAG', 'LCXCAG', 'RCACAG', 'CAG']]]
    YCAG = df['CAG']
    YLAD = df['LADCAG']
    YLCX = df['LCXCAG']
    YRCA = df['RCACAG']
    return X, YCAG, YLAD, YLCX, YRCA

def init_feature(df_X):
    #mpi feature
    initFeature = df_X[[c for c in df_X if c not in ['Gender']]]
    return initFeature

def getOnehotencoderSex(df_X):
    sexDummy = pd.get_dummies(df_X)
    return sexDummy

def extractFeat(df_X):
    
    featX = df_X.copy()
    init_feat = init_feature(featX)
    sex_feat = getOnehotencoderSex(featX['Gender'])

        
    #concat features
    featX.reset_index(drop=True, inplace=True)
    featX = pd.concat([init_feat, sex_feat], axis=1)
    featX['F'] = featX['F'].astype(int)
    featX['M'] = featX['M'].astype(int)
    # feat = feat.drop("Gender", axis=1)
    
    return featX

def standard_scale(df, column):
  if(type(column) != str):
    X = df.values
    scaler = preprocessing.Normalizer()
    scaler.fit(X)
    X_scaled = scaler.transform(X)
    df = pd.DataFrame(data = X_scaled, columns=column)
  return df

def min_max_scale(df, column):
  if(type(column) != str):
    X = df.values
    scaler = preprocessing.Normalizer()
    scaler.fit(X)
    X_scaled = scaler.transform(X)
    df = pd.DataFrame(data = X_scaled, columns=column)
  return df

def normalize(df, column):
  if(type(column) != str):
    X = df.values
    scaler = preprocessing.Normalizer()
    scaler.fit(X)
    X_scaled = scaler.transform(X)
    df = pd.DataFrame(data = X_scaled, columns=column)
  return df

def find_corr(feat, Y):
  df = pd.concat([feat, Y], axis=1)
  plt.figure(figsize=(102,100))
  cor = df.corr(method='pearson') #‘kendall’, ‘spearman’
  
  sns.heatmap(cor.sort_values(by=[Y.name], axis=1, ascending=False), annot=True, cmap=plt.cm.Reds)

  # plt.show()
  sns_plot = sns.heatmap(cor.sort_values(by=[Y.name], axis=1, ascending=False), annot=True, cmap=plt.cm.Reds)
  figure = sns_plot.get_figure()    

  pd.set_option("display.max_rows", None, "display.max_columns", None)
  # Convert correlation matrix to 1-D Series and sort
  sorted_mat = cor.unstack().sort_values()

  return sorted_mat, figure, cor

def feat_selection(feat, target):
  sorted_mat_scale, figure_corr, cor_scale = find_corr(feat, target)
  cor_target_scale = abs(cor_scale[target.name])
  relevant_features_scale = cor_target_scale[cor_target_scale >= 0.1]
  
  print(len(feat.columns), "-", len(feat.columns)-len(relevant_features_scale))
  print("=", len(relevant_features_scale))
  print(relevant_features_scale.index)
  
  feat_corr = feat[[c for c in feat if c in relevant_features_scale.index]]
  df_corr = pd.DataFrame(cor_target_scale.sort_values())
  
  return feat_corr, df_corr, figure_corr

def train_model_indivi(model, param):
  
  outer_cv = LeaveOneOut()
  tuned_model = BayesSearchCV(model, param, n_iter=60, n_jobs=-1, scoring="accuracy", cv=outer_cv)

  return tuned_model, outer_cv

def accuracy_cal(predict, actual):
  acc = sum(predict == actual) / len(actual)
  return acc

def sensitivity(tp, fn):
  sen = (tp+0.001)/(tp+fn+0.001)
  return sen

def specificity(tn, fp):
  spec = (tn+0.001)/(tn+fp+0.001)
  return spec

def train_eval(model, algorithm, feat, Y):
  
  train_accList = []
  test_accList = [] 
  
  senList = []
  specList = [] 
  senTrainList = []
  specTrainList = [] 

  biasList = []
  test_errList = []
  varianceList = []
  aucList = []
  loo = LeaveOneOut()
  index = 0
  for train_index, test_index in loo.split(feat):
    print("\nStart iter", test_index)
    X_train, X_test = feat.loc[train_index], feat.loc[test_index]
    y_train, y_test = Y.loc[train_index], Y.loc[test_index]
    
    # print("start fit iter", test_index)
    model.fit(X_train.values, y_train.values)
    # print("stop fit iter", test_index)

    #predict
    train_predictCAG = model.predict(X_train.values)
    test_predictCAG = model.predict(X_test.values)

    #accuracy
    train_accList.append(accuracy_cal(train_predictCAG, y_train))
    test_accList.append(accuracy_cal(test_predictCAG, y_test))
    # print("acc", train_accList[index], test_accList[index])

    #test matrix
    tn, fp, fn, tp = confusion_matrix(test_predictCAG, y_test.values, labels=[0, 1]).ravel()
    # print("tn, fp, fn, tp")
    # print(tn, fp, fn, tp)

    sens = sensitivity(tp, fn)
    speci = specificity(tn, fp)
    senList.append(sens)
    specList.append(speci)
    # print("sen, spec", senList[index], specList[index])

    #train matrix
    tnt, fpt, fnt, tpt = confusion_matrix(train_predictCAG, y_train, labels=[0, 1]).ravel()
    # print("tnt, fpt, fnt, tpt")
    # print(tnt, fpt, fnt, tpt)
    
    senst = sensitivity(tpt, fnt)
    specit = specificity(tnt, fpt)

    senTrainList.append(senst)
    specTrainList.append(specit)

    #bias, variance
    biasList.append(1 - train_accList[index]) # train_err
    test_errList.append(1 - test_accList[index])
    varianceList.append(test_errList[index] - biasList[index])

    # print(biasList[index], test_errList[index], varianceList[index])
    
    index = index+1
    print("success iter", test_index)
    # break

  # run['model-{}/evaluation/accuracy-train'.format(f'{algorithm}')] = train_accList
  # run['model-{}/evaluation/accuracy-test'.format(f'{algorithm}')] = test_accList
  acc_train = sum(train_accList)/len(Y)
  acc_test = sum(test_accList)/len(Y)
  
  sen_total = sum(senList)/len(Y)
  spec_total = sum(specList)/len(Y)
  sen_train_total = sum(senTrainList)/len(Y)
  spec_train_total = sum(specTrainList)/len(Y)
  
  bias_total = sum(biasList)/len(Y)
  test_err_total = sum(test_errList)/len(Y)
  variance_total = sum(varianceList)/len(Y)
  
  return acc_train, acc_test, sen_total, spec_total, bias_total, test_err_total, variance_total, sen_train_total, spec_train_total

def pre_processing(path, pathPC, algorithm, target):
    
    #1. load data
    # df_NC = load_data(path, pathPC)
    
    #2. clean data
    # df_clean = clean_data(df_NC.copy())

    #3. create CAG
    # df = create_cag(df_clean)
    df = load_data2(path)

    #4. partition data
    X, YCAG, YLAD, YLCX, YRCA = partition_data(df)
    if(target == "CAG"):
      Y = YCAG
    elif(target == "LAD"):
      Y = YLAD
    elif(target == "LCX"):
      Y = YLCX
    else:
      Y = YRCA

    #5. extract features
    feat = extractFeat(X)

    # 6. normalize
    feat_scale = feat.copy()
    feat_scale = normalize(feat_scale, feat_scale.columns)

    feat_corr = feat_scale
    
    return feat_corr, Y

def export_pickle(feat, Y, model):
    model.fit(feat, Y)
    pickle.dump(model, open('model_mpi', 'wb'))
    load_model = pickle.load(open('model_mpi', 'rb'))
    print(load_model)
    print("success")

def run_pipeline(path, pathPC, algorithm, target):

    final_feat, Y = pre_processing(path, pathPC, algorithm, target)

    def status_print(optim_result):
    # """Status callback durring bayesian hyperparameter search"""
    # Get all the models tested so far in DataFrame format
      all_models = pd.DataFrame(bayes.cv_results_)
      # Get current parameters and the best parameters    
      best_params = pd.Series(bayes.best_params_)
      print('Model #{}\nBest scores: {}\nBest params: {}\n'.format(
          len(all_models),
          np.round(bayes.best_score_, 4),
          bayes.best_params_
      ))

    if(algorithm == 'xgb'):
      param = {
      'learning_rate': Real(.05, .1+.05) #lower bound and upper bound
      , 'objective':['binary:logistic']
      , 'subsample': Real(.2, .5)
      , 'n_estimators': Integer(20, 70)
      , 'min_child_weight': Integer(20, 40)
      , 'reg_alpha': Real(0, 0+.7)
      , 'reg_lambda': Real(0, 0+.7)
      , 'colsample_bytree': Real(.1, .1+.7)
      , 'max_depth': Integer(2, 6)
      }
      model = XGBClassifier()

    bayes, cv_corr = train_model_indivi(model, param)
    bayes.fit(final_feat.values, Y.values, callback=status_print)
    
    if(algorithm == 'xgb'):
      model_bayes = XGBClassifier(**bayes.best_params_)

    acc_train, acc_test, sen_test, spec_test, bias, test_err, variance, sen_train, spec_train = train_eval(model_bayes, algorithm, final_feat, Y)
    export_pickle(final_feat, Y, model_bayes)

    return acc_train, acc_test, sen_test, spec_test, bias, test_err, variance, sen_train, spec_train


if __name__ == "__main__":
    name = 'xgb'
    path = "Data/data.csv"
    path_pc = ""
    
    acc_train, acc_test, sen_test, spec_test, bias, test_err, variance, sen_train, spec_train = run_pipeline(path, path_pc, name, 'CAG')
    print("accuracy:", acc_test
    ,"sensitivity:", sen_test
    ,"specificity", spec_test)
