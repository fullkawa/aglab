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
import os

from module import common
from src import util
from src.exception import InvalidActionException

"""ゲームタイトル
"""
title = 'じゃんけんカードゲーム'

"""パラメータ：カード枚数
    1プレイヤーが同じカードを何枚ずつ持つか？
"""
card_num = 2;

"""パラメータ：勝利条件(獲得得点)
"""
winner_score = 5;

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
    '$turn-order':{
        'desc': '手番順を示すプレイヤー番号',
        'size': 3 * card_num * num_players['max'] / 2, #サイズ上書き
        'scope':'public'},
    '$player-1_score':{
        'desc': 'プレイヤー1の得点',
        'scope':'public',
        'value': 0},
    '$player-2_score':{
        'desc': 'プレイヤー2の得点',
        'scope':'public',
        'value': 0},
    '$player-3_score':{
        'desc': 'プレイヤー3の得点',
        'scope':'public',
        'value': 0},
    '$player-4_score':{
        'desc': 'プレイヤー4の得点',
        'scope':'public',
        'value': 0}})

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
    'G':{
        'name': 'グー',
        'str':  'G',
        'rstr': 'g',
        'num':  card_num * num_players['max'],
        '_placed':{
            'type':'stochastic'}},
    'T':{
        'name': 'チョキ',
        'str':  'T',
        'rstr': 't',
        'num':  card_num * num_players['max'],
        '_placed':{
            'type':'stochastic'}},
    'P':{
        'name': 'パー',
        'str':  'P',
        'rstr': 'p',
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
        'name': 'プレイヤー1が使用したカード',
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
        'name': 'プレイヤー2が使用したカード',
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
        'name': 'プレイヤー3が使用したカード',
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
        'name': 'プレイヤー4が使用したカード',
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
    {'key':'common.set_turn_order'},
    {'key':'init_hand'}]

"""プレイの流れ(ゲーム内処理)
    * match: 正規表現が利用可能。これがコンテキストパスと一致する最初の処理が自動プレイ時に実行される。
    * key: 他モジュールを参照する場合はファイルをimportし(commonのみimport済み)、
        モジュール名とキーをピリオドで連結する。例) common.turn_start　
        手動プレイ時はこれ(モジュール名、ピリオドを除く)がコマンドとなる。
    - args: 自動プレイ時に与えられる引数
    - then: 処理後に変更するコンテキストのキー、値
    凡例) *=必須, -=任意
"""
on_play = [
    {'match':'.*/phase:1',
     'key':'set_card',
     'args':[
        [{'ckey':'G'}, {'ckey':'T'}, {'ckey':'P'}],
        'P{turn_player}.p'],
     'then':{
         '$phase-no':2}},
    {'match':'.*/phase:2',
     'key':'set_card',
     'args':[
        [{'ckey':'G'}, {'ckey':'T'}, {'ckey':'P'}],
        'P{next_player}.p'],
     'then':{
         '$phase-no':3}},
    {'match':'.*/phase:3',
     'key':'judge',
     'then':{
         '$phase-no':4}},
    {'match':'.*/phase:4',
     'key':'common.turn_end',
     'args':[
         '$turn-player']},
    {'match':'.*/',
     'key':'common.turn_start',
     'then':{
         '$phase-no':1}}]

"""ゲーム終了条件
"""
def is_end(state):
    turn_no = int(state.get_context('$turn-no'))
    turn_index = turn_no - 1
    #print 'turn_no:', turn_no #DEBUG
    turn_order = state.get_context('$turn-order')
    for i in range(turn_index, len(turn_order)):
        if np.isnan(turn_order[i]):
            break
        player = int(turn_order[i])
        score = state.get_context('$player-{0}_score'.format(player))
        if score >= winner_score:
            print os.linesep, 'player-{0} win!'.format(player)
            return True
    return False
    
"""ゲーム終了(ゲーム終了時処理)
"""
#on_ending = []



def output_contextpath(state):
    """コンテキストパスを取得する
    コンテキストパスとはプレイの状況(≠状態)をURLに似た階層構造で表現したものである。
    """
    path = '//'
    paths = []
    turn = int(state.get_context('$turn-no'))
    if turn > 0:
        paths.append(('turn', str(turn)))
    phase = int(state.get_context('$phase-no'))
    if phase > 0:
        paths.append(('phase', str(phase)))
    path += util.build_urlpath(paths)
    
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

def output_state(state, output, player=None):
    """文字列表現のカスタマイズ
    @param self: Game
    """
    score_section = '[score]'
    for i in range(num_players['max']):
        score = int(state.get_context('$player-{0}_score'.format(i+1)))
        score_section += ' player-{0}:{1},'.format(i+1, score)
    #print 'score_section:', score_section #DEBUG
    output += str.rstrip(score_section) + os.linesep
    return output

def init_hand(state, args, reward=None, report=None):
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

def set_card(state, args, reward=None, report=None):
    """手札からカードを出す
    """
    assert len(args) > 0 and (len(args[0]) == 1)
    ckey = args[0]['ckey']
    _to_key = args[1]
    
    if 'turn_player' in _to_key:
        player = int(state.get_context('$turn-player'))
        _to_key = _to_key.format(turn_player=player)
    elif 'next_player' in _to_key:
        player = int(state.get_context('$next-player')[0])
        _to_key = _to_key.format(next_player=player)
    
    _from_key = 'P{0}.h'.format(player)
    _from_index = state.index_component(ckey, _from_key)
    _to_index = state.last(_to_key) + 1
    """DEBUG
    print '_from_key:', _from_key
    print '_from_index:', _from_index
    print '_to_key:', _to_key
    print '_to_index:', _to_index
    """
    if _from_index < 0:
        message = '"{0}"のカードは手札にないため出せません。'.format(ckey)
        raise InvalidActionException(message)
    else:
        state.move_component((_from_key, _from_index), (_to_key, _to_index))
        state.set_value(state.VALUE_UNKNOWN, fkey=_to_key, findex=_to_index, column='unknown')

def judge(state, args, reward=None, report=None):
    """カードを表向きにして勝敗を判定する
    """
    turn_player = int(state.get_context('$turn-player'))
    next_player = int(state.get_context(('$next-player', 0)))
    tp_played = 'P{0}.p'.format(turn_player)
    np_played = 'P{0}.p'.format(next_player)
    tp_last = state.last(tp_played)
    np_last = state.last(np_played)
    
    # 表向きにする
    state.set_value(state.VALUE_KNOWN, fkey=tp_played, findex=tp_last, column='unknown')
    state.set_value(state.VALUE_KNOWN, fkey=np_played, findex=np_last, column='unknown')
    
    # 勝敗判定
    tp = state.output_component(fkey=tp_played, findex=tp_last)
    np = state.output_component(fkey=np_played, findex=np_last)
    print 'turn-player:', tp, ' vs next-player:', np
    if tp == np:
        print ' -> draw'
        add_score(state, [1, turn_player], reward=reward, report=report)
        add_score(state, [1, next_player], reward=reward, report=report)
    elif (tp=='G' and np=='T') or (tp=='T' and np=='P') or (tp=='P' and np=='G'):
        print ' -> turn-player win'
        add_score(state, [3, turn_player], reward=reward, report=report)
    elif (tp=='G' and np=='P') or (tp=='T' and np=='G') or (tp=='P' and np=='T'):
        print ' -> next-player win'
        add_score(state, [3, next_player], reward=reward, report=report)
    else:
        print 'Illegal hand; turn-player:', tp, ', next-player:', np

def add_score(state, args, reward=None, report=None):
    """得点を加算する
    @param args[0]: 得点
    @param args[1]: 加算対象プレイヤー番号
    """
    if len(args) == 2:
        score = int(args[0])
        player = int(args[1])
    
    key = '$player-{0}_score'.format(player)
    state.set_context(key, state.get_context(key) + score)
    
    if (reward is not None) and (player == int(state.get_context('$player'))):
        r = float(score) / winner_score
        reward.add(r)

