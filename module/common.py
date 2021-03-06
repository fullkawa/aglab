# -*- coding: utf-8 -*-

import numpy as np

from src import util

"""共通ゲーム定義ファイル
"""

"""基本コンテキスト
"""
contexts = {
    '$player-num':{
        'desc': 'プレイ人数',
        'scope':'public'},
    '$player':{
        'desc': 'アクションを行うプレイヤー名',
        'scope':'public'},
    '$phase-no':{
        'desc': 'フェイズ番号',
        'scope':'public',
        'value':0},
    '$turn-no':{
        'desc': 'ターン番号',
        'scope':'public',
        'value':0},
    '$turn-order':{
        'desc': '手番順を示すプレイヤー番号',
        'size': 36, #デフォルト値
        'scope':'public'},
    '$turn-player':{
        'desc': 'ターンプレイヤーのプレイヤー番号',
        'scope':'public'},
    '$prev-player':{
        'desc': '前プレイヤーのプレイヤー番号',
        'scope':'public'},
    '$next-player':{
        'desc': '次プレイヤーのプレイヤー番号',
        'size': 2, #デフォルト値
        'scope':'public'}}

"""基本アクション
"""

def set(state, args, reward=None, report=None):
    """コンポーネントを指定された位置にセットする
    @param args[0]: string セットするオブジェクトのkey
    @param args[1]: int    セットするオブジェクトのindex
    @param args[2]: string セット先フィールドのkey
    @param args[3]: int    セット先フィールドのindex
    """
    assert(len(args) == 4)
    
    state.set_component((args[0], args[1]), (args[2], args[3]))
    """DEBUG
    print 'SET', args[0], args[1], 'to', args[2], args[3]
    """

def set_deck(state, args, reward=None, report=None):
    """すべてのコンポーネントをデッキにセットする
    """
    #print 'components:', state.components #DEBUG
    for component in state.components:
        pos = state.get_context('$deck-count')
        args = [
            component['key'],
            component['index'],
            'deck',
            pos]
        set(state, args)
        state.set_context('$deck-count', pos+1)

def shuffle(state, args, reward=None, report=None):
    """対象フィールド内のコンポーネントをシャッフルする
    @param arg: string 対象フィールドのキー
    """
    assert isinstance(args[0], str)
    fkey = args[0]
    
    pointer = int(state.get_context('${0}-pointer'.format(fkey)))
    indexes = range(pointer)
    np.random.shuffle(indexes)
    islicer = state.get_islicer(fkey=fkey)
    csize = len(state.components)
    fsize = state.data.loc[islicer, 'value'].index.levels[4].size #levels[4]=findex
    values = state.data.loc[islicer, 'value'].values.reshape(csize, fsize)
    shuffled = np.ndarray(shape=(csize, fsize))
    for i in range(pointer):
        shuffled[:][i] = values[:][indexes[i]]
    state.data.loc[islicer, 'value'] = shuffled.flatten()
    #print state.data.loc[islicer, 'value'].values.reshape(csize, fsize) #DEBUG

def move(state, args, reward=None, report=None):
    """コンポーネントを移動する
    @param args[0]: tuple 移動元フィールドのkey, index
    @param args[1]: tuple 移動先フィールドのkey, index
    """
    assert len(args) > 1
    _from = args[0]
    _to = args[1]
    
    state.move_component(_from, _to)

def case(state, args, reward=None, report=None):
    print 'TODO:case()'

def set_turn_order(state, args, reward=None, report=None):
    """プレイヤーの行動順を設定する
    @param args: list/int/str argsがNoneの場合、数字1つの場合はプレイヤー人数とみなす。  
        カンマで連結された文字列であれば行動順を示すプレイヤー番号とみなす。
    """
    turn_order = list(state.get_context('$turn-order'))
    
    if args is None:
        args = int(state.get_context('$player-num'))
    
    #print 'args(in set_turn_order):', args #DEBUG
    if isinstance(args, int):
        for i in range(args):
            turn_order[i] = i + 1
    elif isinstance(args, str):
        _order = args.split(',')
        #print '_order:', _order #DEBUG
        for i in range(len(_order)):
            turn_order[i] = int(_order[i])
    else:
        print '[WARN] Illegal args:', args
    #print 'turn_order:', turn_order #DEBUG
    state.set_context('$turn-order', turn_order)

def turn_start(state, args, reward=None, report=None):
    """ターン開始処理
    @param args: list/str argsがあるとき、それを手番順(turn_order)としてセットする
    """
    if (args is not None) and isinstance(args, list) and (len(args) > 0):
        if isinstance(args[0], str):
            set_turn_order(state, args[0])
    
    turn = int(state.get_context('$turn-no'))
    if turn > 0:
        turn += 1
    else:
        turn = 1
    turn_order = state.get_context('$turn-order')
    prev_player = state.get_context('$turn-player')
    turn_player = turn_order[turn-1]
    next_player = state.get_context('$next-player')
    for i in range(len(next_player)):
        if turn+i < len(turn_order):
            next_player[i] = turn_order[turn+i]
        else:
            next_player[i] = float('nan')
    """DEBUG
    print 'turn:', turn #DEBUG
    print 'turn_order:', turn_order #DEBUG
    print 'turn_player:', turn_player #DEBUG
    print 'prev_player:', prev_player #DEBUG
    print 'next_player:', next_player #DEBUG
    """
    state.set_context('$turn-no', turn)
    state.set_context('$prev-player', prev_player)
    state.set_context('$turn-player', turn_player)
    state.set_context('$next-player', next_player)

def turn_end(state, args, reward=None, report=None):
    """ターン終了処理
    @param args: list/int/str argsがあるとき、それを手番順(turn_order)の最後にセットする
    """
    state.set_context('$phase-no', 0)
    
    player = None
    if isinstance(args, list) and len(args) > 0:
        try:
            player = int(args[0])
        except ValueError: # intに変換できなかった場合
            if args[0].startswith('$'):
                player = int(state.get_context(args))
        
    if player is not None:
        turn_order = state.get_context('$turn-order')
        util.append_value(turn_order, player)
        state.set_context('$turn-order', turn_order)


