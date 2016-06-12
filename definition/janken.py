# -*- coding: utf-8 -*-

"""ゲーム定義ファイル
以下のような じゃんけんゲームを想定し、定義する。
* ゲーム開始時に各プレイヤーはグー/チョキ/パーのカードをそれぞれn枚ずつ持つ。
 * nはパラメータ(card_num)によって変更可能
* ターンプレイヤーの次のプレイヤーが手札から裏向きでカードを1枚出す。
* その後、ターンプレイヤーも手札から裏向きでカードを1枚出す。
* 同時にカードを表向きにする。
 * じゃんけんに勝ったプレイヤーは3点、負けたプレイヤーは0点、あいこの場合はお互い1点ずつを獲得する。
* 一番最初に5点以上獲得したプレイヤーをゲームの勝者とする。
 * 同時に2名のプレイヤーが5点以上となった場合はターンプレイヤーを勝者とする。

パラメータ(カード枚数)が十分に大きい場合、出されるカードに制限がないためほぼ運ゲーになる。
逆にパラメータが小さい場合、使い切ったカードは出てこないため読みや戦略が発生するゲームになると期待される。

@author: fullkawa
"""

import numpy as np

from module import common
from src import util

"""ゲームタイトル
"""
title = 'じゃんけんカードゲーム'

"""パラメータ：カード枚数
    1プレイヤーが同じカードを何枚ずつ持つか？
"""
card_num = 2;

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
    '$turn-no':{
        'desc': 'ターン番号',
        'scope':'public',
        'value':0},
    '$turn-order':{
        'desc': '手番順を示すプレイヤー番号',
        'size': 3 * card_num * num_players['max'] / 2,
        'scope':'public'},
    '$turn-player':{
        'desc': 'ターンプレイヤーのプレイヤー番号',
        'scope':'public'},
    '$prev-player':{
        'desc': '前プレイヤーのプレイヤー番号',
        'scope':'public'},
    '$next-player':{
        'desc': '次プレイヤーのプレイヤー番号',
        'size': 2,
        'scope':'public'}})

"""コンポーネント定義
    * キー: コンポーネントのキー
        [設定項目] "_"で始まる項目はプロパティとして扱われます。
        - name: 項目名
        * str:  公開状態(カードがオープンされたとき等)の表示文字
        * rstr: 非公開状態(カードが裏向きのとき等)での表示文字
        - num:  数量。省略時は`num:1`
        * _placed: 配置場所
    凡例) *=必須, -=任意
"""
components = {
    'Gu':{
        'name': 'グー',
        'str':  'G',
        'rstr': '#',
        'num':  card_num * num_players['max'],
        '_placed':{
            'type':'stochastic'}},
    'Tyoki':{
        'name': 'チョキ',
        'str':  'T',
        'rstr': '#',
        'num':  card_num * num_players['max'],
        '_placed':{
            'type':'stochastic'}},
    'Pa':{
        'name': 'パー',
        'str':  'P',
        'rstr': '#',
        'num':  card_num * num_players['max'],
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
    'player-1_hand':{
        'name': 'プレイヤー1の手札',
        'size': 3 * card_num,
        'shorten':'P1.h',
        'distinguishable': False,
        'scope':'private'},
    'player-1_played':{
        'name': 'プレイヤー1の手札',
        'size': 3 * card_num,
        'shorten':'P1.p',
        'distinguishable': True,
        'scope':'public'},
    'player-2_hand':{
        'name': 'プレイヤー2の手札',
        'size': 3 * card_num,
        'shorten':'P2.h',
        'distinguishable': False,
        'scope':'private'},
    'player-2_played':{
        'name': 'プレイヤー2の手札',
        'size': 3 * card_num,
        'shorten':'P2.p',
        'distinguishable': True,
        'scope':'public'},
    'player-3_hand':{
        'name': 'プレイヤー3の手札',
        'size': 3 * card_num,
        'shorten':'P3.h',
        'distinguishable': False,
        'scope':'private'},
    'player-3_played':{
        'name': 'プレイヤー3の手札',
        'size': 3 * card_num,
        'shorten':'P3.p',
        'distinguishable': True,
        'scope':'public'},
    'player-4_hand':{
        'name': 'プレイヤー4の手札',
        'size': 3 * card_num,
        'shorten':'P4.h',
        'distinguishable': False,
        'scope':'private'},
    'player-4_played':{
        'name': 'プレイヤー4の手札',
        'size': 3 * card_num,
        'shorten':'P4.p',
        'distinguishable': True,
        'scope':'public'}}

"""
ルール定義
"""

"""プレイ前の準備(ゲーム開始時処理)
"""
on_setup = [
    ['/setup:1', 'common.set_turn_order'],
    ['/setup:2', 'init_hand']]

"""プレイの流れ(ゲーム内処理)
"""
on_play = [
  ['.*/', 'common.turn_start'],
  ['.*/turn:[0-9]*.*', 'common.turn_end']]

"""ゲーム終了条件
"""
#def is_end(state):
#    return True    
    
"""ゲーム終了(ゲーム終了時処理)
"""
#on_ending = []



def output_contextpath(state):
    """コンテキストパスを取得する
    コンテキストパスとはプレイの状況(≠状態)をURLに似た階層構造で表現したものである。
    """
    path = '//'
    turn = state.get_context('$turn-no')
    if turn > 0:
        path += util.build_urlpath([('turn', str(int(turn)))])
    
    qslist = []
    tp = state.get_context('$turn-player')
    if not np.isnan(tp):
        qslist.append(('turn', str(int(tp))))
    pp = state.get_context('$prev-player')
    if not np.isnan(pp):
        qslist.append(('prev', str(int(pp))))
    nps = state.get_context('$next-player')
    for _np in nps:
        if not np.isnan(_np):
            qslist.append(('next', str(int(_np))))
    qs = util.build_urlqs(qslist)
    if len(qs) > 0:
        path += '?' + qs
    return path

def init_hand(state, *args, **kwargs):
    """手札を初期配置する
    """
    player_num = int(state.get_context('$player-num'))
    for n in range(player_num):
        fkey = 'player-{0}_hand'.format(n+1)
        findex = 0
        for ckey, cdef in components.iteritems():
            for i in range(card_num):
                cindex = n * card_num + i
                state.set_component((ckey, cindex), (fkey, findex))
                findex += 1
