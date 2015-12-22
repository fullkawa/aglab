# -*- coding: utf-8 -*-

"""
ゲーム定義ファイル

@author fullkawa
"""

import numpy as np

import common

"""
ゲームタイトル
"""
title = 'ジャンケンカードゲーム'

"""
プレイ人数(最小〜最大)
"""
min_players = 3
max_players = 3

"""
ゲーム独自のパラメータ定義
"""

# プレイヤー1人あたりのグー/チョキ/パーカード枚数
each_card = 2

# グー/チョキ/パーカードの合計枚数
hand_num = max_players * each_card

"""
コンポーネント定義
  キー =そのコンポーネントを表す簡潔な表記
    name: 名称
    num:  数量
"""
components = {
  'G': {
    'name': 'グー',
    'num' : hand_num
  },
  'C': {
    'name': 'チョキ',
    'num' : hand_num
  },
  'P': {
    'name': 'パー',
    'num' : hand_num
  }
}

"""
フィールド定義
  キー =そのフィールドを表す簡潔な表記
    'player-{n}_'で始まるフィールドは'turn-player_', 'prev-player_'
    , 'next-player_'もデフォルトで定義される
  
    name: 名称
    size: 最大サイズ
    scope: スコープ =public/private/hiddenのいずれか
      public =公開情報。全てのプレイヤーがいつでも知ることができる情報
      private =秘匿情報。本人のみいつでも知ることができる、主にプレイヤー自身の情報
      hidden =非公開情報。基本的に誰も知ることができない情報。ただし、ルール効果により
              確認することが可能な場合もある
    ref:  参照フィールドのキー
      これが指定されている場合、size, scopeは無効(参照先フィールドと同じになる)
"""
fields = {
  'player-{n}_hand': {
    'name'  : 'プレイヤーnの手札',
    'size'  : hand_num,
    'scope' : 'private'
  },
  'player-{n}_used': {
    'name'  : 'プレイヤーnの使用済みカード',
    'size'  : hand_num,
    'scope' : 'public'
  },
}

"""
ゲーム固有のコンテキスト定義
"""
context = [
]

"""
ゲームの種類
"""
type = "to_win" # 勝ち抜け

"""
ルール定義
"""

"""
プレイ前の準備
"""
setup = [
  ['deal_cards', ['all', each_card]]
]

"""
プレイの流れ
"""
on_play = [
  ['/', 'common.round_start'],
  ['/round:[0-9]*_0', 'common.set_turn_order', 'clockwise'],
  ['/round:[0-9]*_[0-9]+', 'common.turn_start'],
  ['.*/turn:[0-9]*_0','common.phase_start', 'set'],
  ['.*/phase:set_0',  'action?', [
    ['common.move_card', ['player-{tn}_hand[{any}]', 'player-{tn}_used[{next}]']]
    ], '_tp'],
  ['.*/phase:set_1',  'action?', [
    ['common.move_card', ['player-{nn}_hand[{any}]', 'player-{nn}_used[{next}]']]
    ], '_np'],
  ['.*/phase:set.*',  'common.phase_end'],
  ['.*/turn:[0-9]*_1','common.phase_start', 'open'],
  ['.*/phase:open_0', 'open_card'],
  ['.*/phase:open.*', 'common.phase_end'],
  ['.*/turn:[0-9]*.*','common.turn_end'],
  ['/round:[0-9]*.*', 'common.round_end'],
]

"""
終了条件

勝ち抜けゲームのとき、終了条件＝勝利条件でもある。
"""
def is_end(data):
  turn_pno = data.get_context('_turn-p.-no')
  if np.isnan(turn_pno):
    return False
  pno, highscore = data.get_highest(top=turn_pno)
  if highscore >= 5:
    return True
  return False

"""
終了時の処理
"""
on_ending = [
]

"""
プレイヤーにカード(手札)を配る
"""
def deal_cards(data, args):
  player_num = int(data.get_context('_player-num'))
  each_card = args[1]
  for n in range(each_card):
    for m in range(player_num):
      i = 0
      for c in ['G', 'C', 'P']:
        field = 'player-{0}_hand[{1}]'.format(m + 1, n * player_num + i)
        card = '{0}[{1}]'.format(c, n * player_num + m)
        #print 'field:',field,', card:',card
        data.set_component(card, field)
        i += 1
  print ' -> OK'

"""
ジャンケンを行い、結果に応じたスコアを返す
"""
def janken(card1, card2):
  #print card1[0], card2[0] #debug
  scores = {
    'G': {'G':[1,1], 'C':[3,0], 'P':[0,3]},
    'C': {'G':[0,3], 'C':[1,1], 'P':[3,0]},
    'P': {'G':[3,0], 'C':[0,3], 'P':[1,1]}
  }
  return scores[card1[0]][card2[0]]

"""
カードをオープンし、勝負する
"""
def open_card(data, args):
  tp_cardfield = data.resolve('player-{tn}_used[{last}]', as_list=False)
  tp_card = data.get_component(tp_cardfield)
  np_cardfield = data.resolve('player-{nn}_used[{last}]', as_list=False)
  np_card = data.get_component(np_cardfield)
  tp_score, np_score = janken(tp_card, np_card)
  print ' open -> tp_score:', tp_score, ', np_score:', np_score
  
  tpno = data.get_context('_turn-p.-no')
  tp_scorefield = '_player-{tp}_score'.format(tp=tpno)
  def tp_score_add(value):
    return value + tp_score
  data.calc_context_value(tp_scorefield, tp_score_add)
  
  npno = data.get_context('_next-p.-no')
  np_scorefield = '_player-{np}_score'.format(np=npno)
  def np_score_add(value):
    return value + np_score
  data.calc_context_value(np_scorefield, np_score_add)


