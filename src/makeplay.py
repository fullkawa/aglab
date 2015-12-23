# -*- coding: utf-8 -*-

"""
プレイデータ作成ツール

ゲーム定義からプログラムで自動的にプレイデータを作成する。

@author fullkawa
"""

usage = """
  python makeplay.py [play_num] ['clear']
"""

import itertools
import math
import os
import random
import re
import sys

import common
import game

from PlayData import PlayData

# データを作成するプレイ数の既定値
DEFAULT_PLAY_NUM = 10000

# 不具合、設定不備等により無限ループに入らないようにする制限ステップ数
STEP_GUARD = 9999

# データディレクトリ
DATA_DIR = "..{sep}data".format(sep=os.sep)

# プレイデータディレクトリ
PLAYDATA_DIR = DATA_DIR + "{sep}play".format(sep=os.sep)

"""
CSVファイル名を取得する
@see makelearning.py get_play()
"""
def get_csvfilename(data, suffix=''):
  filename = '{DIR}{sep}data_{play:0>6}_{step:0>8}{suffix}.csv'.format(
    DIR=PLAYDATA_DIR,
    sep=os.sep,
    play=int(data.get_context('_play')),
    step=int(data.get_context('_step')),
    suffix=suffix)
  return filename

"""
アクション引数ごとにプレイスホルダを解決する
"""
def _resolve_args(data, args):
  resolved = []
  for arg in args:
    resolved.append(data.resolve(arg))
  return resolved

"""
アクション定義から実行可能なアクションを生成する
"""
def _get_actions(data, definitions):
  actions = []
  for definition in definitions:
    args = definition[1]
    resolved_args = _resolve_args(data, args)
    if len(resolved_args) == 1:
      selected_args = resolved_args
    elif len(resolved_args) == 2:
      selected_args = []
      for arg1, arg2 in itertools.product(resolved_args[0], resolved_args[1]):
        selected_args.append([arg1, arg2])
    else:
      raise Exception('FIXME:Cannot use over 3 parameters')
    
    command = definition[0]
    for selected in selected_args:
      actions.append([command, selected])
  return actions

"""
実行可能なアクションからランダムで選んで返す
"""
def _select_action(actions):
  selected = random.randint(0, len(actions)-1)
  return actions[selected]

"""
レベル FIXME:定義ここでOK？
"""
_LEVEL_ROOT  = 0
_LEVEL_ROUND = 1
_LEVEL_TURN  = 2
_LEVEL_PHASE = 3

"""
レベルパスを取得する
"""
def get_levelpath(data):
  level = list(data.get_context('_level'))
  try:
    lvstep = int(data.get_context('_level-step'))
  except ValueError: # NaN
    lvstep = ''
  #print 'level:', level, 'lvstep:', lvstep # debug
  
  if len(level) == _LEVEL_ROOT:
    path = '/'

  if len(level) >= _LEVEL_ROUND:
    if len(level) == _LEVEL_ROUND:
      path = '/round:{0}_{1}'.format(data.get_context('_round'), lvstep)
    else:
      path = '/round:{0}'.format(data.get_context('_round'))

  if len(level) >= _LEVEL_TURN:
    if len(level) == _LEVEL_TURN:
      path += '/turn:{0}_{1}'.format(data.get_context('_turn'), lvstep)
    else:
      path += '/turn:{0}'.format(data.get_context('_turn'))

  if len(level) >= _LEVEL_PHASE:
    if len(level) >= _LEVEL_PHASE:
      path += '/phase:{0}_{1}'.format(data.get_context('_phase'), lvstep)
    else:
      path += '/phase:{0}'.format(data.get_context('_phase'))
  
  #print 'path:', path # debug
  return path

"""
プレイデータ作成処理
"""
print '\nSTART makeplay'

if len(sys.argv) > 2:
  files = os.listdir(PLAYDATA_DIR)
  if (files):
    for file in files:
      os.remove(PLAYDATA_DIR + os.sep + file)
  print 'clear PLAYDATA'

play_num = DEFAULT_PLAY_NUM
if len(sys.argv) > 1:
  play_num = int(sys.argv[1])
print 'play_num:', play_num

for play in range(1, play_num + 1):
  player_num = random.randint(game.min_players, game.max_players)
  
  data = PlayData(game)
  data.set_scope(game)
  
  data.init_context(game)
  data.set_context('_play', play)
  data.set_context('_player-num', player_num)
  data.set_context('_alive-players', range(1, player_num + 1))
  data.set_context('_status', 'setup')
  data.set_context('_level', '')
  data.set_context('_level-path', '/')
  #print data # debug
  
  print '\n[setup]'
  for command in game.setup:
    print 'command:', command
    if len(command) > 1:
      args = command[1]
    else:
      args = None
    
    if 'common.' in command[0]:
      command_0 = command[0].replace('common.', '')
      getattr(common, command_0)(data, args)
    else:
      getattr(game, command[0])(data, args)
  data.set_context('_status', 'on_play')

  print '\n[on_play]'
  data.set_context('_step', 1)
  data.set_context('_err-message', 'Over STEP_GUARD')
  while ((data.get_context('_step') < STEP_GUARD)
    & (data.get_context('_status') == 'on_play')):
    step = data.get_context('_step')
    #print 'step:', step # debug
    
    for command in game.on_play:
      #print 'match?->', command[0], data.get_context('_level-path') # debug
      
      matching = re.match('^' + command[0] + '$', data.get_context('_level-path'))
      if matching is None:
        #print ' ->continue' # debug
        continue
      
      print '[{0}] command:'.format(step), command
      
      if command[1] == 'action?':
        actions = _get_actions(data, command[2])
        #print 'actions:', actions # debug
        action = _select_action(actions)
        print ' selected:', action
        cmd = action[0]
        args = action[1]
        
        #print 'data(before) ->', get_csvfilename(data, command[3]) # debug
        data.to_csv(get_csvfilename(data, command[3]))
      else:
        cmd = command[1]
        if len(command) > 2:
          args = command[2]
        else:
          args = ''

      if 'common.' in cmd:
        mod = common
        cmd = cmd.replace('common.', '')
      else:
        mod = game

      getattr(mod, cmd)(data, args)
      #print 'data(after)  ->', get_csvfilename(data, 1) # debug
      data.to_csv(get_csvfilename(data))

      if game.is_end(data):
        data.set_context('_status', 'on_ending')
        data.set_context('_err-message', '') # successed
      
      break

    data.set_context('_level-path', get_levelpath(data))
    data.increment_context('_level-step')
    data.increment_context('_step')
    print
        
  print '\n[on_ending]'

  #print '\ndata in makeplay:', data # debug


print '\nEND makeplay\n'


