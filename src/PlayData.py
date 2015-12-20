# -*- coding: utf-8 -*-

from pandas import DataFrame

import numpy as np
import re

"""
プレイデータ

ゲームにおける1局面の状況を保持するクラス。
pandas.DataFrameのラッパー

制限事項
* プレイヤー数の上限は 9
* 同一コンポーネントの最大数は 99
"""
class PlayData(DataFrame):

  """
  基本的なコンテキスト
  """
  context = [
     'play',    # プレイ番号
     'round',   # 現在のラウンド数
     'turn',    # 現在のターン数
     'phase',   # 現在のフェイズ名
     'step',    # 現在のステップ数
     'level',   # 処理中のレベル
     'level-step',  # 同一レベル内でのステップ数
     'level-path',  # 現在のレベルパス
     'status',  # プレイの状態 =setup/on_play/on_ending/is_overのいずれか
     'player-num',  # プレイヤー数
     'alive-players', # プレイ中のプレイヤー番号
     'player-{n}_score',  # プレイヤーnのスコア。nはプレイヤー番号
     'player-{n}_type',   # プレイヤーnの種別 =human/randomのいずれか
     'turn-order',    # ターンの行動順
     'turn-p.-no',    # ターンプレイヤーのプレイヤー番号
     'prev-p.-no',    # 前プレイヤーのプレイヤー番号
     'next-p.-no',    # 次プレイヤーのプレイヤー番号
     'err-message', # 発生したエラーメッセージ
  ]
  
  CONTEXT_INDEX = '_context'
  SCOPE_INDEX = '_scope'
  
  def _append_to(self, list, key, num):
    if num > 0:
      for i in range(num):
        label = "{key}[{index}]"
        list.append(label.format(key=key, index=i))
    else:
      list.append(key)

    return list

  """
  ゲーム定義に従って初期化する
  @param params ≒ゲーム定義
  """
  def __init__(self, params):
    try:
      fields = []
      for key, config in params.fields.iteritems():
        if '{n}' in key:
          for i in range(params.max_players):
            fields = self._append_to(fields, key.format(n=i+1), config['size'])
        else:
          fields = self._append_to(fields, key, config['size'])
      
      components = []
      for key, config in params.components.iteritems():
        components = self._append_to(components, key, config['num'])

      DataFrame.__init__(self, index=sorted(fields), columns=sorted(components))
  
    except AttributeError: # 上記__init__時に発生するエラー
      DataFrame.__init__(self, params)

  """
  スコープを設定する
  """
  def set_scope(self, game):
    for field in self.index:
      try:
        fielddef = re.sub('-[0-9]+_', '-{n}_', field)
        fielddef = re.sub(r'\[[0-9]+\]', '', fielddef)
        self.ix[field, self.SCOPE_INDEX] = game.fields[fielddef]['scope']
      except KeyError:
        self.ix[field, self.SCOPE_INDEX] = '*ERROR*'

  """
  コンテキストを初期化する
  @param game ゲーム定義
  """
  def init_context(self, game):
    self.context.extend(game.context)
    for key in self.context:
      if '{n}' in key:
        for i in range(game.max_players):
          self.ix[key.format(n=i+1), self.CONTEXT_INDEX] = float('nan')
      else:
        self.ix[key, self.CONTEXT_INDEX] = float('nan')

  """
  コンポーネントをフィールドにセットする
  """
  def set_component(self, name, field):
    scope = self.ix[field, self.SCOPE_INDEX]
    
    if name is None:
      if scope == 'public':
        self[name] = float('nan')
      self.ix[field] = float('nan')
    else:
      if scope == 'public':
        self[name] = 0
      self.ix[field] = 0
      self.ix[field, name] = 1
      self.ix[field, self.CONTEXT_INDEX] = 1
    
    self.ix[field, self.SCOPE_INDEX] = scope

  """
  フィールドにセットされているコンポーネントを取得する
  """
  def get_component(self, field):
    values = self.ix[field].copy()
    values = values.drop(self.SCOPE_INDEX).drop(self.CONTEXT_INDEX)
    return values.idxmax()
  
  """
  あるフィールドにセットされているコンポーネントを別のフィールドへ移動する
  """
  def move_component(self, _from, _to):
    component = self.get_component(_from)
    self.set_component(component, _to)
    self.set_component(None, _from)

  """
  コンテキストの値を設定する
  """
  def set_context(self, key, value):
    try:
      self.ix[key, self.CONTEXT_INDEX] = value
    except ValueError: # listの要素数が2のとき発生する場合あり
      self[self.CONTEXT_INDEX] = self[self.CONTEXT_INDEX].astype(list)
      self.set_value(key, self.CONTEXT_INDEX, value)
  
  """
  コンテキストの値を取得する
  """
  def get_context(self, key):
    return self.ix[key, self.CONTEXT_INDEX]

  """
  リスト内の要素を、指定された値を先頭にして並べ替える
  """
  def _reorder_from(self, top, list_):
    if top is None:
      ordered = list_
    else:
      ordered = []
      i, doinsert = [0, False]
      for o in list_:
        if o == top:
          doinsert = True
        if doinsert:
          ordered.insert(i, o)
          i += 1
        else:
          ordered.append(o)
    return ordered

  """
  ハイスコアのプレイヤー番号、スコアを取得する
  """
  def get_highest(self, order=None, top=None):
    if order is None:
      order = list(self.get_context('alive-players'))
    ordered = self._reorder_from(top, order)

    pn = None
    highest = 0
    for od in ordered:
      score = self.get_context('player-{n}_score'.format(n=od))
      #print 'od:', od, ', score:', score, ', pn:', pn, ', highest:', highest # debug
      if score > highest:
        pn, highest = od, score
        
    return [pn, highest]

  """
  コンテキストの値に対して演算を行う
  @param calc: 引数を1つ(value)持つ演算式
  """
  def calc_context_value(self, key, calc):
    value = self.get_context(key)
    if np.isnan(value):
      value = 0
    self.set_context(key, calc(value))

  """
  コンテキストの値を＋１する
  """
  def increment_context(self, key):
    def increment(value):
      return value + 1
    self.calc_context_value(key, increment)

  """
  コンテキストの値をー１する
  """
  def decrement_context(self, key):
    def decrement(value):
      return value - 1
    self.calc_context_value(key, decrement)

  """
  レベルを1段深くする
  """
  def push_level(self):
    level = list(self.get_context('level'))
    level_step = self.get_context('level-step')
    if np.isnan(level_step):
      level_step = 0

    level.append(level_step)
    self.set_context('level', level)
    self.set_context('level-step', 0)
    #print 'pushed level:', level, ', level-step:', 0

  """
  レベルを1段浅くする
  """
  def pull_level(self):
    level = list(self.get_context('level'))
    level_step = level.pop()

    self.set_context('level', level)
    self.set_context('level-step', level_step)
    #print 'pulled level:', level, ', level-step:', level_step

  """
  プレイスホルダ(プレイヤー番号)を解決する
   {n}, {tn} -> turn-p.-no
   {pn} -> prev-p.-no
   {nn} -> next-p.-no
  """
  def _resolve_player_num(self, arg):
    #print ' arg in _resolve_player_num:', arg # debug
    resolved = None
    formatter = EFormatter()
    
    if '{n}' in arg:
      resolved = [formatter.format(arg, n=self.get_context('turn-p.-no'))]
    elif '{tn}' in arg:
      resolved = [formatter.format(arg, tn=self.get_context('turn-p.-no'))]
    elif '{pn}' in arg:
      resolved = [formatter.format(arg, pn=self.get_context('prev-p.-no'))]
    elif '{nn}' in arg:
      resolved = [formatter.format(arg, nn=self.get_context('next-p.-no'))]

    #print ' -> resolved:', resolved # debug
    return resolved

  """
  プレイスホルダ(any:いずれかのインデックス)を解決する
   hoge[0]=1, hoge[1]=1, hoge[2]=NaN
   {any} -> [0, 1] # NaNでないインデックスを一通り
  """
  def _resolve_any(self, arg):
    #print 'arg in _resolve_next:', arg # debug
    
    if not '{any}' in arg:
      #print ' -> notmatched' # debug
      return None
    
    resolved = []
    formatter = EFormatter()
    i = 0
    try:
      while True:
        field = formatter.format(arg, any=i)
        value = self.get_context(field)
        if np.isnan(value) == False:
          resolved.append(field)
        i += 1
    except Exception:
      #print 'i:', i # debug
      pass
    
    #print ' ->resolved:', resolved # debug
    return resolved
  
  """
  プレイスホルダ(last:値が入っている最後のインデックス)を解決する
  hoge[0]=1, hoge[1]=1, hoge[2]=NaN
  {last} -> 1
  """
  def _resolve_last(self, arg):
    #print 'arg in _resolve_last:', arg # debug
    
    if not '{last}' in arg:
      #print ' -> notmatched' # debug
      return None
    
    resolved = []
    formatter = EFormatter()
    i = 0
    try:
      while True:
        field = formatter.format(arg, last=i)
        value = self.get_context(field)
        if np.isnan(value):
          i -= 1
          break
        i += 1
    except Exception:
      #print 'i:', i # debug
      pass
    
    resolved.append(formatter.format(arg, last=i))
    #print ' ->resolved:', resolved # debug
    return resolved

  """
  プレイスホルダ(next:次のインデックス)を解決する
   hoge[0]=1, hoge[1]=1, hoge[2]=NaN
   {next} -> 2
  """
  def _resolve_next(self, arg):
    #print 'arg in _resolve_next:', arg # debug
    
    if not '{next}' in arg:
      #print ' -> notmatched' # debug
      return None
    
    resolved = []
    formatter = EFormatter()
    i = 0
    try:
      while True:
        field = formatter.format(arg, next=i)
        value = self.get_context(field)
        if np.isnan(value):
          break
        i += 1
    except Exception:
      #print 'i:', i # debug
      pass
    
    resolved.append(formatter.format(arg, next=i))
    #print ' ->resolved:', resolved # debug
    return resolved

  """
  プレイスホルダを解決する
  """
  def resolve(self, arg, as_list=True):
    resolver = Resolver(arg)
    resolver.resolve(self._resolve_player_num)
    resolver.resolve(self._resolve_last)
    resolver.resolve(self._resolve_next)
    resolver.resolve(self._resolve_any)

    resolved = resolver.get_resolved()
    if as_list:
      return resolved
    else:
      if len(resolved) > 0:
        return resolved[0]
      else:
        return ''

"""
プレイスホルダ解決クラス
"""
class Resolver:
  def __init__(self, str):
    self.resolved = [str]

  """
  funcにstring型の引数を与えて解決させる
  @return array
  """
  def _resolve(self, func, str):
    #print '_resolve', str, 'by', func.__name__ # debug

    resolved = func(str)
    #print '-> resolved:', resolved # debug
    return resolved
  
  """
  プレイスホルダを解決する
  """
  def resolve(self, func, str=None):
    #print 'resolve', str, 'by', func.__name__ # debug
    
    if str is None:
      str = [self.resolved]
    
    resolved = []
    if isinstance(str, list):
      for s in str:
        results = self.resolve(func, s)
        resolved.extend(results)
      #print 'resolved:', resolved # debug
      if len(resolved) > 0:
        self.resolved = resolved
    
    else:
      result = self._resolve(func, str)
      if result is not None:
        resolved.extend(result)
    
    return resolved

  """
  解決された結果を取得する
  """
  def get_resolved(self):
    return self.resolved


import string

"""
keyがない場合は置き換えを行わないFormatter
@see http://stackoverflow.com/questions/17215400/python-format-string-unused-named-arguments
"""
class EFormatter(string.Formatter):
  def __init__(self, default='{{{0}}}'):
    self.default = default

  def get_value(self, key, args, kwds):
    if isinstance(key, str):
      return kwds.get(key, self.default.format(key))
    else:
      Formatter.get_value(key, args, kwds)


