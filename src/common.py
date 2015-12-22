# -*- coding: utf-8 -*-

"""
標準ゲームライブラリ

多くのゲームで一般的に見られるメカニクスを集めている。

@author fullkawa
"""

"""
ラウンド開始処理
"""
def round_start(data, args):
  round = data.get_context('round')
  if round > 0:
    data.set_context('round', round + 1)
  else:
    data.set_context('round', 1)

  data.push_level()
  print ' Round:{0} start'.format(data.get_context('round'))

"""
ラウンド終了処理
"""
def round_end(data, args):
  data.set_context('phase', '')
  data.set_context('turn', float('nan'))
  
  data.pull_level()
  print ' Round:{0} end'.format(data.get_context('round'))

"""
プレイヤーの行動順を設定する

@param args 'clockwise' =時計回り(1->2->3->...)
"""
def set_turn_order(data, args):
  if args == 'clockwise':
    player_num = int(data.get_context('player-num'))
    order = range(1, player_num + 1)
    data.set_context('turn-order', order)
    print ' ->', order
  else:
    raise Exception('No implementation for %0').format(args)

"""
ターン開始処理
"""
def turn_start(data, args):
  turn = data.get_context('turn')
  if turn > 0:
    data.set_context('turn', turn + 1)
  else:
    data.set_context('turn', 1)

  turn_order = list(data.get_context('turn-order'))
  current = int(turn_order[0])

  try:
    turn_p = int(data.get_context('turn-p.-no'))
  except ValueError:
    turn_p = 0
  if turn_p != current:
    data.set_context('prev-p.-no', turn_p)
    data.set_context('turn-p.-no', current)
    if len(turn_order) > 1:
      data.set_context('next-p.-no', turn_order[1])
    else:
      alive_players = list(data.get_context('alive-players'))
      data.set_context('next-p.-no', alive_players[0])

  data.push_level()
  print ' Turn:{0} start; player-{1}'.format(data.get_context('turn'), current)

"""
ターン終了処理
"""
def turn_end(data, args):
  turn_order = list(data.get_context('turn-order'))
  turn_order.pop(0)
  data.pull_level()
  
  data.set_context('turn-order', turn_order)
  if len(turn_order) == 0:
    # ラウンド終了へ
    data.set_context('phase', '')
    data.set_context('level-step', float('nan'))
  
  print ' Turn:{0} end'.format(data.get_context('turn'))

"""
フェイズ開始処理
"""
def phase_start(data, args):
  data.set_context('phase', args)

  data.push_level()
  print ' Phase:{0} start'.format(data.get_context('phase'))

"""
フェイズ終了処理
"""
def phase_end(data, args):
  phase = data.get_context('phase')
  data.set_context('phase', '')
  
  data.pull_level()
  print ' Phase:{0} end'.format(phase)

"""
コンポーネントを移動する
* 移動元はコンポーネントなしの状態になる
"""
def move_component(data, args):
  _from = args[0]
  _to = args[1]
  data.move_component(_from, _to)

"""
カードを移動する
(ゲーム定義の可読性を上げるためのシンタックスシュガー)
"""
def move_card(data, args):
  return move_component(data, args)

