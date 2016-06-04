# -*- coding: utf-8 -*-

"""ゲーム定義ファイル
"""

from module import common
import util

"""ゲームタイトル
"""
title = '(ゲームタイトル)'

"""プレイ人数(最小〜最大)
"""
num_players = {
    'min':  2,
    'max':  4}

"""コンテキスト定義
"""
contexts = common.contexts
util.dict_merge(contexts, {
    '$value-1':{
        'desc': 'ここに説明文を入力します。',
        'scope':'public',
        'value':1}})

"""コンポーネント定義
"""
components = {
    'C1':{
        'name': 'カード1',
        'str':  '1',
        'num':  1,
        '_placed':{
            'type':'stochastic'}},
    'C2':{
        'name': 'カード2',
        'str':  '2',
        'num':  3,
        '_placed':{
            'type':'stochastic'}}}

"""フィールド定義
"""
fields = {
    'field-1':{
        'name': 'フィールド1',
        'size': 4,
        'shorten':'F1',
        'distinguishable': False,
        'scope':'hidden'},
    'field-2':{
        'name': 'フィールド2',
        'size': 4,
        'shorten':'F2',
        'distinguishable': True,
        'scope':'public'},
    'player-1_hand':{
        'name': 'プレイヤー1の手札',
        'size': 2,
        'shorten':'P1.h',
        'distinguishable': False,
        'scope':'private'}}

"""
ルール定義
"""

"""プレイ前の準備(ゲーム開始時処理)
"""
#on_setup = []

"""プレイの流れ(ゲーム内処理)
"""
#on_play = []

"""ゲーム終了条件
"""
#def is_end(state):
#    return True    
    
"""ゲーム終了(ゲーム終了時処理)
"""
#on_ending = []

