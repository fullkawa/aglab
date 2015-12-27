# -*- coding: utf-8 -*-

"""
ゲーム解析ツール

プレイデータを機械学習させることにより、ゲームを解析する。
@see http://scikit-learn.org/stable/auto_examples/svm/plot_svm_regression.html

@author fullkawa
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.svm import SVR
from sklearn.decomposition import PCA

# データディレクトリ
DATA_DIR = os.path.join('..', 'data')

# 学習データディレクトリ
SVDATA_DIR = os.path.join(DATA_DIR, 'supervisor')

# 学習データファイル
SVDATA_FILE = os.path.join(SVDATA_DIR, 'data.csv')

# データの列数
DATA_NUM = 63

# 学習データの割合
TRAIN_DATA_RATIO = .9

# FIXME:未使用→隠れ層のノード数
HIDDEN_UNIT_SIZE = 62

data = np.genfromtxt(open(SVDATA_FILE), delimiter=',', filling_values=0)
[params, scores] = np.hsplit(data, [DATA_NUM])
[train_params, test_params] = np.vsplit(params, [len(params) * TRAIN_DATA_RATIO])
[train_scores, test_scores] = np.vsplit(scores, [len(scores) * TRAIN_DATA_RATIO])
print 'test_params:'
print test_params # debug
print 'test_scores:'
print test_scores # debug
print

pca = PCA(n_components=1)
pca.fit(train_params)
train_params_pca = pca.transform(train_params)
print 'train_params_pca:'
print train_params_pca # debug
train_params_pcar = train_params_pca.reshape(train_params_pca.shape[0])
#print 'train_params_pcar:'
#print train_params_pcar # debug

test_params_pca = pca.transform(test_params)
test_params_pcar = test_params_pca.reshape(test_params_pca.shape[0])
#print 'test_params_pcar:'
#print test_params_pcar # debug

train_scores_r = train_scores.reshape(train_scores.shape[0])
print 'train_scores_r:'
print train_scores_r # debug
print

svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
svr_lin = SVR(kernel='linear', C=1e3)
svr_poly = SVR(kernel='poly', C=1e3, degree=2)
"""
y_rbf = svr_rbf.fit(train_params, train_scores).predict(test_params)
y_lin = svr_lin.fit(train_params, train_scores).predict(test_params)
y_poly = svr_poly.fit(train_params, train_scores).predict(test_params)
"""
print train_params_pca.shape, train_scores_r.shape # debug
y_rbf = svr_rbf.fit(train_params_pca, train_scores_r).predict(train_params_pca)
y_lin = svr_lin.fit(train_params_pca, train_scores_r).predict(train_params_pca)
y_poly = svr_poly.fit(train_params_pca, train_scores_r).predict(train_params_pca)

plt.scatter(train_params_pca, train_scores_r, c='k', label='train_data')
plt.hold('on')
print train_params_pca.shape, y_rbf.shape # debug
plt.plot(train_params_pca, y_rbf, c='g', label='RBF model')
plt.plot(train_params_pca, y_lin, c='r', label='Linear model')
plt.plot(train_params_pca, y_poly, c='b', label='Polynomial model')
plt.xlabel('params')
plt.ylabel('score')
plt.title('Janken Card Game')
plt.legend()
plt.show()


