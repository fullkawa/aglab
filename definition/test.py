# -*- coding: utf-8 -*-

"""ゲーム定義ファイル
これはユニットテスト用の定義ファイルです。
※とりあえずStateクラスに必要な項目だけ
"""

contexts = {
    '$player':{
        'desc': 'アクションを行うプレイヤー名(player-1/2/3/4)',
        'scope':'public'},
    '$cxt-1':{
        'desc': 'コンテキスト1',
        'scope':'public',
        'value':1}}

components = {
    'C1':{
        'name': 'カード1',
        'str':  ' 1',
        'rstr': '-1',
        'num':  1,
        '_placed':{
            'type':'stochastic'}},
    'C2':{
        'name': 'カード2',
        'str':  ' 2',
        'rstr': '-2',
        'num':  3,
        '_placed':{
            'type':'stochastic'}}}

fields = {
    'F1':{
        'name': 'フィールド1',
        'size': 4,
        'shorten':'F1',
        'distinguishable': False,
        'scope':'hidden'},
    'F2':{
        'name': 'フィールド2',
        'size': 4,
        'shorten':'F2',
        'distinguishable': False,
        'scope':'public'},
    'player-1_hand':{
        'name': 'プレイヤー1の手札',
        'size': 2,
        'shorten':'P1.h',
        'distinguishable': True,
        'scope':'private'},
    'player-1_played':{
        'name': 'プレイヤー1がプレイしたカード',
        'size': 2,
        'shorten':'P1.p',
        'distinguishable': True,
        'scope':'public'},
    'player-2_hand':{
        'name': 'プレイヤー2の手札',
        'size': 2,
        'shorten':'P2.h',
        'distinguishable': True,
        'scope':'private'},
    'player-2_played':{
        'name': 'プレイヤー2がプレイしたカード',
        'size': 2,
        'shorten':'P2.p',
        'distinguishable': True,
        'scope':'public'}}
