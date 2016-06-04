# -*- coding: utf-8 -*-

"""ゲーム定義ファイル
"""

from module import common
from src import util

"""ゲームタイトル
"""
title = '(ゲームタイトル)'

"""プレイ人数(最小〜最大)
"""
num_players = {
    'min':  2,
    'max':  4}

"""コンテキスト定義
    * キー: コンテキストのキー。"$"で始めること。
        [設定項目]
        - desc:  説明文
        - size:  サイズ。省略時は`size:1`
        * scope: 情報公開範囲
        - value: 初期値。省略時はNaNが初期値となる
    凡例) *=必須, -=任意
"""
contexts = common.contexts
util.dict_merge(contexts, {
    '$value-1':{
        'desc': 'ここに説明文を入力します。',
        'scope':'public',
        'value':1}})

"""コンポーネント定義
    * キー: コンポーネントのキー
        [設定項目] "_"で始まる項目はプロパティとして扱われます。
        - name: 項目名
        * str:  表示文字
        - num:  数量。省略時は`num:1`
        * _placed: 配置場所
    凡例) *=必須, -=任意
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
    * キー: フィールドのキー
        [設定項目]
        - name: 項目名
        - size: サイズ。コンポーネントを配置できる数。省略時は`size:1`
        - shorten: 短縮表記
        * distinguishable: 区別可能性
        * scope: 情報公開範囲
    凡例) *=必須, -=任意
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

