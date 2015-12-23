# -*- coding: utf-8 -*-

"""
機械学習データ作成ツール

機械学習データを作成する。

@author fullkawa
"""

usage = """
  python makelearning.py
"""

import numpy as np
import os
import pandas as pd
import re

from PlayData import PlayData

# データディレクトリ
DATA_DIR = os.path.join("..", "data")

# プレイデータディレクトリ
PLAYDATA_DIR = os.path.join(DATA_DIR, "play")

# 機械学習データディレクトリ
SVDATA_DIR = os.path.join(DATA_DIR, "supervisor")

"""
CSVファイル名からプレイ番号を取得する
@see makeplay.py get_csvfilename()
"""
def get_play(csvfilename):
  play = None
  matched = re.match(r'data_([0-9]+)_.+', csvfilename)
  if matched:
    play = int(matched.group(1))
  return play

"""
ゲーム終了時点での各プレイヤーの評価値を取得する
勝ち抜けゲームにおける評価値：勝ったプレイヤー＝１，負けたプレイヤー＝−１
"""
def get_evals_to_win(data):
  player_num = int(float(data.get_context('_player-num')))
  evals = np.full(player_num, -1.0) # 負け
  winner, wscore = [None, 0]
  for i in range(player_num):
    score = data.get_context('_player-{n}_score'.format(n=i+1))
    if score > wscore:
      winner, wscore = [i, score]
  evals[winner] = 1.0 # 勝ち
  return evals

"""
プレイデータを学習データに変換する
"""
def convert(source):
  represented = source.as_player()

  packed = represented.pack(fields=['turn-player_hand', 'prev-player_hand', 'next-player_hand', 'other-player_hand'], components=['C', 'G', 'P'])

  data = packed.sort_index(axis=0).sort_index(axis=1)
  #print data # debug

  rows, columns = data.shape
  onelined = PlayData(data.as_matrix().reshape(1, rows * columns))
  #print onelined # debug

  return onelined

evals, laststeps = [{}, {}]
#files = [file for file in data(os.listdir(PLAYDATA_DIR), reverse=True)]
files = sorted(os.listdir(PLAYDATA_DIR), reverse=True)

for file in files:
  #print 'file:', file # debugdata_000001
  play = get_play(file)
  filepath = os.path.join(PLAYDATA_DIR, file)
  outputpath = os.path.join(SVDATA_DIR, 'data_{0:0>6}.csv'.format(play))
  try:
    eval = evals[play]
    if '_tp' in file:
      data = PlayData(PlayData.from_csv(filepath))
      step = float(data.get_context('_step'))
      pno = int(data.get_context('_turn-p.-no'))
      score = eval[pno-1]*(step/laststeps[play])
      
      converted = convert(data)
      converted = pd.concat([converted, PlayData(np.array([[score]]))], axis=1)
      print 'output ->', outputpath # debug
      converted.to_csv(outputpath, header=False, index=False, mode='a')
      print 'step:', step, ', converted:', converted # debug
    
  except KeyError:
    data = PlayData(PlayData.from_csv(filepath))
    evals[play] = get_evals_to_win(data)
    laststeps[play] = float(data.get_context('_step'))
    print play, evals[play], laststeps[play] # debug


#packed.to_csv(os.path.join(SVDATA_DIR, '00000001.csv'), header=False, index=False)
