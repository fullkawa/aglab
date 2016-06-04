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
    '$player-name':{
        'desc': 'アクションを行うプレイヤー名(player-1/2/3/4)',
        'scope':'public'}}

"""基本アクション
"""

def set(state, args, **kwargs):
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

def set_deck(state, args, **kwargs):
    """すべてのコンポーネントをデッキにセットする
    """
    #print 'components:', state.components #DEBUG
    for component in state.components:
        pos = state.get_context('$deck-pointer')
        args = [
            component['key'],
            component['index'],
            'deck',
            pos]
        set(state, args)
        state.set_context('$deck-pointer', pos+1)

def shuffle(state, args, **kwargs):
    """対象フィールド内のコンポーネントをシャッフルする
    @param arg: string 対象フィールドのキー
    """
    assert isinstance(args, str)
    fkey = args
    
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

def move(state, args, **kwargs):
    """コンポーネントを移動する
    @param args[0]: tuple 移動元フィールドのkey, index
    @param args[1]: tuple 移動先フィールドのkey, index
    """
    assert len(args) > 1
    _from = args[0]
    _to = args[1]
    
    state.move_component(_from, _to)

def case(state, args, **kwargs):
    print 'TODO:case()'

def set_turn_order(state, args, **kwargs):
    """プレイヤーの行動順を設定する
    @param args: int/str argsがNoneの場合、数字1つの場合はプレイヤー人数とみなす。  
        カンマで連結された文字列であれば行動順を示すプレイヤー番号とみなす。
    """
    turn_order = state.get_context('$turn-order')
    
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
            turn_order[i] = _order[i]
    
    #print 'turn_order:', turn_order #DEBUG
    state.set_context('$turn-order', turn_order)

def turn_start(state, args, **kwargs):
    """ターン開始処理
    @param args: str argsがあるとき、それを手番順(turn_order)としてセットする
    """
    if args is not None:
        set_turn_order(state, args)
    
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

def turn_end(state, args, **kwargs):
    """ターン終了処理
    @param args: int/str argsがあるとき、それを手番順(turn_order)の最後にセットする
    """
    turn = state.get_context('$turn-no')
    turn_order = state.get_context('$turn-order')
    if args is not None:
        util.append_value(turn_order, int(args))
        state.set_context('$turn-order', turn_order)


