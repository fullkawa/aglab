# -*- coding: utf-8 -*-
import numpy as np
import operator
import os
import pandas as pd
import random
import re
import string
from pandas.core.index import MultiIndex

from src import util
from src.exception import InvalidActionException

class Game(object):
    """ゲーム
    定義にしたがってゲームを構築し、実行するためのクラス。
    @see testplay.ipynb
    """
    
    max_steps = 99 #TEST:99999;
    """最大実行ステップ数
    無限ループから抜けるためのリミッター
    """
    
    def __init__(self, definition, controller=None):
        """初期化
        プレイごとにリセット *されない* パラメータの設定など
        @param definition: dict ゲーム定義
        """
        assert definition != None
        self.definition = definition
        self.controller = controller
        
        self.num_players_list = []
        self.num_players = self.min_players = definition.num_players['min']
        self.max_players = definition.num_players['max']
        
        self.on_setup = []
        if hasattr(definition, 'on_setup'):
            self.on_setup = self._build_procs(definition.on_setup)
        
        self.on_play = []
        if hasattr(definition, 'on_play'):
            self.on_play = self._build_procs(definition.on_play)
        
        self.is_end = None
        if hasattr(definition, 'is_end'):
            self.is_end = definition.is_end
            
        self.on_ending = []
        if hasattr(definition, 'on_ending'):
            self.on_ending = self._build_procs(definition.on_ending)
        
        self.state = State(definition)
        self.observation = Observation(self.state)
        
        self.output_contextpath = None
        if hasattr(definition, 'output_contextpath'):
            self.output_contextpath = definition.output_contextpath
        
        self._output_state = None
        if hasattr(definition, 'output_state'):
            self._output_state = definition.output_state
        
    def output_state(self, player=None):
        """状態の文字列表現を取得する
        TODO:リファクタリング？
        """
        output = self.state.output(player)
        if self._output_state is not None:
            output = self._output_state(self.state, output, player=player)
        return output
        
    def _build_procs(self, def_procs):
        """ゲーム定義から処理を生成する
        """
        procs = []
        for def_proc in def_procs:
            #print 'def_proc:', def_proc #DEBUG
            names = def_proc['key'].split('.', 1)
            if len(names) == 1:
                module  = self.definition
                name    = names[0]
            else:
                module = getattr(self.definition, names[0])
                name    = names[1]
            
            #print 'module:', module #DEBUG
            proc = {
                'key':  '{0}.{1}'.format(module.__name__, name),
                'command': name,
                'proc': getattr(module, name)}
            if 'match' in def_proc:
                proc['match'] = def_proc['match']
            if 'args' in def_proc:
                proc['args'] = def_proc['args']
                if (self.controller is not None) and isinstance(def_proc['args'][0], list):
                    params = {
                        'actions': len(def_proc['args'][0])}
                    proc['controller'] = self.controller(params)
            else:
                proc['args'] = None
            if 'then' in def_proc:
                proc['then'] = def_proc['then']
                
            #print 'proc:', proc #DEBUG
            procs.append(proc)
        
        return procs
        
    def rand_params(self):
        """ランダムでプレイパラメータを取得する
        """
        num_players = self._rand_num_players();
        player = random.randint(1, num_players);
        params = {
            'num_players':  num_players,
            'player':       player}
        return params
        
    def _rand_num_players(self):
        """ランダムでプレイ人数を取得する
        """
        if len(self.num_players_list) == 0:
            _list = range(self.min_players, self.max_players + 1)
            random.shuffle(_list)
            self.num_players_list = _list
        return self.num_players_list.pop(0)
    
    def setup(self, params=None):
        """プレイ前の準備(初期化)を行う。
        @param params: dict
            プレイ条件パラメータ
            'num_players': プレイ人数
        """
        # 初期化
        self.step_no = 0
        self.command = None
        self.act = None
        self.done = False
        self.reward = Reward()
        self.report = {}
        
        # 設定
        if params is None:
            params = self.rand_params()
        self.num_players = params['num_players']
        self.player = params['player']
        self.state.set_context('$player-num', self.num_players)
        self.state.set_context('$player', self.player)
        
        if self.num_players >= 3:
            self.state.set_context('$player-3', 1)
        if self.num_players >= 4:
            self.state.set_context('$player-4', 1)
        
        for proc in self.on_setup:
            self._process(proc)
        
    def get_info(self):
        """プレイに関する情報を取得する
        """
        info = '[{title}]{br}'.format(title=self.definition.title, br=os.linesep)
        info += '- Player:{0} in {1} players'.format(self.player, self.num_players)
        return info
        
    def get_contextpath(self):
        """コンテキストパスを取得する
        コンテキストパスとはプレイの状況(≠状態)をURLに似た階層構造で表現したものである。
        """
        if self.output_contextpath is not None:
            return self.output_contextpath(self.state)
        return '*** No def output_contextpath(state)'
        
    def get_header(self):
        """(状態の)ヘッダを取得する
        """
        return self.state.get_header()
        
    def get_state(self, player=None):
        """ゲームの状態を配列(≒ベクトル)で取得する
        """
        return self.state.to_array()
    
    def get_obs_header(self):
        """観察結果のヘッダを取得する
        """
        return self.observation.get_header()
    
    def get_observation(self, observer=None):
        """ゲームの観察結果を配列(≒ベクトル)で取得する
        """
        return self.observation.to_array(observer)
        
    def collect_reward(self):
        """獲得した報酬を取得する
        """
        return self.reward.collect()
    
    def get_prompt(self):
        """プレイヤー入力
        """
        return '? '
    
    def step(self, command=None):
        """ゲームを1ステップ進行する
        @param command: dict コマンド
        """
        self.step_no += 1
        print 'STEP:', self.step_no, '-' * 32
        
        if command is None:
            self.command, self.act = self._matched_command(self.get_contextpath())
            if self.act is None:
                self._process(self.command, reward=self.reward, report=self.report)
            
        else:
            self.command = command
            self._step_command()
        
        if self.is_end is not None:
            self.done = self.done or self.is_end(self.state)
        return
        
    def _step_command(self):
        """コマンド実行の前処理
        * 簡易入力形式の変換
        * 定義不要コマンド(set, move, end)の実装
        を含む。
        """
        cmds = string.split(self.command)
        assert cmds is not None
        assert len(cmds) > 0
        
        if (len(cmds) > 1) and (cmds[1] == '>'):
            cmds[1] = cmds[0]
            cmds[0] = 'move'
        proc = util.dict_search(self.on_play, ('command', cmds[0]))
        #print 'proc:', proc #DEBUG
        if len(proc) > 0:
            if len(cmds) > 1:
                proc[0]['args'] = cmds[1:]
            self._process(proc[0], reward=self.reward, report=self.report)
        elif 'move' == cmds[0]:
            assert len(cmds) == 3
            self.state.move_component(cmds[1], cmds[2])
        elif 'set' == cmds[0]:
            assert len(cmds) == 3
            self.state.set_component(cmds[1], cmds[2])
        elif 'end' == cmds[0]:
            self.done = True
        else:
            print 'No command;', cmds
            #print 'on_play:', self.on_play #DEBUG
        
    def _matched_command(self, contextpath):
        """条件にマッチする最初のコマンドを取得する
        """
        #print 'contextpath:', contextpath #DEBUG
        command = None
        for proc in self.on_play:
            matched = re.match(proc['match'], contextpath)
            if matched is not None:
                #print 'match:', proc #DEBUG
                command = proc
                break
        if command is None:
            raise exception.NoMatchedProcess(contextpath)
            
        act = None
        if 'controller' in command:
            act = command['controller']
        return command, act
        
    def perform_action(self, action):
        """アクションを実行する
        """
        try:
            self._process(self.command, action=action, reward=self.reward, report=self.report)
        except InvalidActionException as e:
            print e
            self.reward.add(-1)
            self.done = True
        
    def _process(self, proc, action=None, reward=None, report=None):
        """定義された処理を実行する
        これにより、ゲームの状態が変化する。
        @param proc: dict 実行したい処理
        """
        args = proc['args']
        if (args is not None) and isinstance(args[0], list) and (action is not None):
            args[0] = args[0][action]
        print 'PROCESS:{0} {1}'.format(proc['key'], '' if (args is None) else args)
        proc['proc'](self.state, args, reward=reward, report=report)
        if 'then' in proc:
            for key, value in proc['then'].items():
                self.state.set_context(key, value)
        
    def get_result(self):
        """プレイ結果を取得する
        """
        result = '=' * 40 + '{br}'
        result += '[Result]{br}'
        result += ' step:{step}{br}'
        return result.format(step=self.step_no, br=os.linesep)

class State(object):
    """ゲーム状態
    ゲームの状態を示すすべてのデータを表す。
    """
    
    INDEX_KEY = 0
    INDEX_COMPONENT_INDEX = 1
    INDEX_PROPERTY_NAME = 2
    INDEX_FIELD_KEY = 3
    INDEX_FIELD_INDEX = 4
    INDEX_SCOPE = 5
    
    VALUE_KNOWN = 0
    VALUE_UNKNOWN = 1
    
    VALUE_EXISTENT = 1
    VALUE_NON_EXISTENT = 0
    
    def __init__(self, definition):
        """初期化
        """
        self.fields = self._build_fields(definition.fields)
        
        self.components = []
        self.values = []
        s_index_names = ['ckey', 'cindex', 'propname', 'fkey', 'findex', 'scope']
        s_ckeys, s_cindexes, s_propnames, s_fkeys, s_findexes, s_scopes, s_values = self._build_state(definition)
        s_multi = MultiIndex.from_arrays([s_ckeys, s_cindexes, s_propnames, s_fkeys, s_findexes, s_scopes], names=s_index_names)
        self.data = pd.DataFrame(data=s_values, index=s_multi, columns=['unknown', 'value'])
    
    def _build_fields(self, fields):
        """フィールド情報を抽出する
        """
        _fields = []
        for key, field in sorted(fields.iteritems()):
            items = []
            if ('size' in field) and (field['size'] > 1):
                for i in range(field['size']):
                    items.append(self._build_fields_field(key, field, index=i))
            else:
                items.append(self._build_fields_field(key, field))
            _fields.extend(items)
            
        """DEBUG
        print 'State.fields:', len(_fields)
        print _fields[0]
        """
        
        return _fields
        
    def _build_fields_field(self, key, field, index=None):
        """フィールド情報を構築する
        """
        item = {
            'key':   key,
            'scope': field['scope'],
            'shorten': field['shorten'],
            'distinguishable':field['distinguishable']}
        if index is None:
            item['index'] = float('nan')
            item['header'] = key
        else:
            item['index'] = index
            item['header'] = '{0}[{1:0>2}]'.format(key, index)
            
        return item
        
    def _build_state(self, definition):
        """state生成に必要な情報をゲーム定義ファイルから抽出する
        """
        ckeys = []
        cindexes = []
        propnames = []
        fkeys = []
        findexes = []
        scopes = []
        values = []
        
        self._build_state_context(definition.contexts, ckeys, cindexes, propnames, fkeys, findexes, scopes, values)
        self._build_state_component(definition.components, ckeys, cindexes, propnames, fkeys, findexes, scopes, values)
        return (ckeys, cindexes, propnames, fkeys, findexes, scopes, values)
    
    def _build_state_context(self, contexts, ckeys, cindexes, propnames, fkeys, findexes, scopes, values):
        """コンテキスト情報を抽出する
        """
        for key, context in sorted(contexts.iteritems()):
            size = 1
            if 'size' in context:
                size = context['size']
            for i in range(size):
                ckeys.append(key)
                if size > 1:
                    cindexes.append(i)
                else:
                    cindexes.append(0)
                propnames.append('')
                fkeys.append('')
                findexes.append(0)
                scopes.append(context['scope'])
                if context['scope'] in ['public', 'private']:
                    known = self.VALUE_KNOWN
                else:
                    known = self.VALUE_UNKNOWN
                if 'value' in context:
                    value = context['value']
                else:
                    value = float('nan')
                values.append([known, value])
        """DEBUG
        print 'State.contexts:', len(ckeys)
        print ' ckeys:', ckeys
        print 'cindexes:', cindexes
        print 'propnames:', propnames
        print 'fkeys:', fkeys
        print 'findexes:', findexes
        print 'scopes:', scopes
        """
        
    def _build_state_component(self, components, ckeys, cindexes, propnames, fkeys, findexes, scopes, values):
        """コンポーネント情報を抽出する
        """
        for key, component in sorted(components.iteritems()):
            num = 1
            if 'num' in component:
                num = component['num']
            for i in range(num):
                _component = {
                    'key':  key,
                    'index':i}
                if 'str' in component:
                    _component['str'] = component['str']
                else:
                    _component['str'] = key
                if 'rstr' in component:
                    _component['rstr'] = component['rstr']
                else:
                    _component['rstr'] = key
                self.components.append(_component)
            for propkey, property in component.iteritems():
                if propkey.find('_') != 0:
                    continue
                # '_'から始まる＝プロパティ名
                for i in range(num):
                    for field in self.fields:
                        ckeys.append(key)
                        cindexes.append(i)
                        propnames.append(propkey)
                        fkeys.append(field['key'])
                        findexes.append(field['index'])
                        scopes.append(field['scope'])
                        if field['scope'] in ['public']:
                            known = self.VALUE_KNOWN
                        else:
                            known = self.VALUE_UNKNOWN
                        values.append([known, float('nan')])
                        
        """DEBUG
        print 'State.components:', len(self.components)
        print self.components[0]
        print 'State.values:', len(values)
        print ckeys[0], cindexes[0], propnames[0], fkeys[0], findexes[0], scopes[0], values[0]
        """
        
    def __str__(self, *args, **kwargs):
        #return object.__str__(self, *args, **kwargs)
        return self.data.to_string()
    
    def get_header(self):
        """全プロパティのヘッダを取得する。
        """
        print 'TODO:get_header()'
        
    def to_array(self):
        """全プロパティの値を配列で取得する。
        """
        print 'TODO:State.to_array()'
    
    def set_context(self, key, value):
        """コンテキストを設定する
        """
        self.set_value(value, context=key)
        
    def get_context(self, key):
        """コンテキストを取得する
        """
        return self.get_value(context=key)
    
    def get_islicer(self, key=None, cindex=None, propname=None, fkey=None, findex=None, scope=None):
        """インデックス絞り込み条件(?)を取得する
        """
        if key is None:
            key = slice(None)
        if cindex is None:
            cindex = slice(None)
        if propname is None:
            propname = slice(None)
        if fkey is None:
            fkey = slice(None)
        if findex is None:
            findex = slice(None)
        if scope is None:
            scope = slice(None)
        return (key, cindex, propname, fkey, findex, scope)
    
    def set_value(self, 
                  value, 
                  context=None, component=None, field=None,
                  key=None, cindex=None, propname=None, fkey=None, findex=None, scope=None, 
                  column='value'):
        """値を設定する
        コンポーネント/コンテキストのキー(key), コンポーネントのインデックス(cindex), プロパティ名(propname), 
        フィールドのキー(fkey), フィールドのインデックス(findex), スコープ(scope)を適切に設定することにより、
        複数の値を一度に設定することができる。
        """
        if context is not None:
            key, cindex = util.get_key_and_index(context)
        if component is not None:
            key, cindex = util.get_key_and_index(component)
        if field is not None:
            fkey, findex = util.get_key_and_index(field)
        
        key = self._conv_key(key)
        fkey = self._conv_key(fkey)
        slicer = self.get_islicer(key=key, cindex=cindex, propname=propname, fkey=fkey, findex=findex, scope=scope)
        try:
            self.data.loc[slicer, column] = value
        except KeyError:
            pass
        
    def get_value(self, 
                  context=None, component=None, field=None,
                  key=None, cindex=None, propname=None, fkey=None, findex=None, scope=None, 
                  column='value', 
                  return_list=False):
        """値を取得する
        コンポーネント/コンテキストのキー(key), コンポーネントのインデックス(cindex), プロパティ名(propname), 
        フィールドのキー(fkey), フィールドのインデックス(findex), スコープ(scope)を適切に設定することにより、
        複数の値を一度に取得することができる。
        return_list=False のとき、取得した値が1つの場合は値(のみ)を直接取得することができる。
        それ以外の場合、値はリストで取得される。
        """
        if context is not None:
            key, cindex = util.get_key_and_index(context)
        if component is not None:
            key, cindex = util.get_key_and_index(component)
        if field is not None:
            fkey, findex = util.get_key_and_index(field)
            
        key = self._conv_key(key)
        fkey = self._conv_key(fkey)
        slicer = self.get_islicer(key=key, cindex=cindex, propname=propname, fkey=fkey, findex=findex, scope=scope)
        values = self.data.loc[slicer, column].values
        if (len(values) == 1) and (return_list == False):
            return values[0]
        else:
            return values
    
    def get_value_reshaped(self,
                           context=None, component=None, field=None,
                           key=None, cindex=None, propname=None, fkey=None, findex=None, scope=None, 
                           column='value', 
                           return_list=False):
        """二次元配列で値を取得する
        """
        values = self.get_value(context=context, component=component, field=field,
                                key=key, cindex=cindex, propname=propname, fkey=fkey, findex=findex, scope=scope,
                                column=column,
                                return_list=return_list)
        #print 'len(values):', len(values) #DEBUG
        
        num_components = len(self.components)
        #print 'num_components:', num_components #DEBUG
        if (key is not None) and (cindex is None):
            key = self._conv_key(key)
            num_components = len(util.dict_search(self.components, ('key', key)))
            #print ' ->', num_components #DEBUG
        
        size_fields = len(self.fields)
        #print 'size_fields:', size_fields #DEBUG
        if (fkey is not None) and (findex is None):
            fkey = self._conv_key(fkey)
            size_fields = len(util.dict_search(self.fields, ('key', fkey)))
            #print ' ->', size_fields #DEBUG
        
        return values.reshape(num_components, size_fields)
    
    def set_player(self, name, context_key='$player'):
        """プレイヤー(ここではアクションを選択するプレイヤーを指す)を設定する
        """
        _fkeys = [] #対象プレイヤーに関連するfkey
        fkeys = self.data.index.get_level_values(self.INDEX_FIELD_KEY).values
        for fkey in np.unique(fkeys):
            if 'player-{0}'.format(name) in fkey:
                _fkeys.append(fkey)
        self.set_value(self.VALUE_KNOWN, fkey=_fkeys, scope='private', column='unknown')
        
        self.set_value(name, key=context_key)
        
    def last(self, fkey):
        """指定されたフィールドを先頭から走査し、最後にセットされているコンポーネントのインデックスを取得する
        コンポーネントが一つもセットされていない場合は-1を返す。
        """
        values = self.get_value_reshaped(fkey=fkey)
        
        _last = -1
        for i, value in enumerate(np.sum(values, axis=0)):
            if np.isnan(value):
                return _last
            _last = i
    
    def _conv_key(self, key):
        """keyが短縮形(shorten)だったとき、それを通常のキーに変換する
        """
        if len(util.dict_search(self.fields, ('key', key))) == 0:
            ref = util.dict_search(self.fields, ('shorten', key))
            if (len(ref) > 0) and ('key' in ref[0]):
                return ref[0]['key']
        return key
        
    def set_component(self, component, _to):
        """1つのコンポーネントを1つのフィールドにセットする
        このメソッドはunknownとvalueを一組で設定します。すなわち、unknownなフィールドにあったコンポーネントを
        移動するとき、同じフィールドがunknownとなっていた別コンポーネントも同様に処理されるということです。
        """
        assert component is not None
        assert _to is not None
        
        ckey, cindex = util.get_key_and_index(component)
        fkey, findex = util.get_key_and_index(_to)
        
        self.set_value(self.VALUE_NON_EXISTENT, fkey=fkey, findex=findex)
        self.set_value(self.VALUE_EXISTENT, key=ckey, cindex=cindex, fkey=fkey, findex=findex)
        
    def move_component(self, _from, _to):
        """フィールドからフィールドへ1つのコンポーネントを移動する
        """
        assert _from is not None
        assert _to is not None
        
        fkey, findex = util.get_key_and_index(_from)
        #fkey = self._conv_key(_fkey)
        tkey, tindex = util.get_key_and_index(_to)
        #tkey = self._conv_key(_tkey)
        
        values = self.get_value(fkey=fkey, findex=findex)
        self.set_value(values, fkey=tkey, findex=tindex)
        self.set_value(float('nan'), fkey=fkey, findex=findex)
        
    def index_component(self, component, _in):
        """指定コンポーネントがセットされているフィールド内の位置を返す。
        フィールド内に1つもなければ-1, 
        フィールド内に複数あれば始めに見つかった位置を返す。
        """
        values = self.get_value_reshaped(key=component, fkey=_in)
        for i, value in enumerate(np.sum(values, axis=0)):
            if value > 0:
                return i
        return -1
        
    def output_component(self, field=None, fkey=None, findex=None):
        """指定されたフィールドにセットされているコンポーネントの出力形式を取得する
        """
        output = ' ' #何もセットされてない場合の出力形式
        strs = []
        
        if field is not None:
            fkey, findex = util.get_key_and_index(field)
        fkey = self._conv_key(fkey)
        slicer = self.get_islicer(propname='_placed', fkey=fkey, findex=findex)
        unknown = self.data.loc[slicer, 'unknown'][0]
        #print 'unknown:', unknown #DEBUG
        value = self.data.loc[slicer, 'value']
        #print 'value:', value #DEBUG
        for _key, _value in value.iteritems():
            #print '_key:', _key, ', _value:', _value #DEBUG
            if _value > 0:
                ckey = _key[0]
                str_key = 'rstr' if unknown == 1 else 'str'
                _str = util.dict_value(self.components, str_key, search=('key', ckey))
                strs.append(_str)
        strs = np.unique(strs)
        #print 'strs:', strs, ', len=', len(strs) #DEBUG
        if len(strs) > 0:
            output = "/".join(strs)
        return output
    
    def output_components(self, fkey):
        """指定されたフィールドにセットされているコンポーネントの出力形式をまとめて取得する
        """
        output = []
        fields = util.dict_search(self.fields, ('key', fkey))
        for field in fields:
            _output = self.output_component(fkey=fkey, findex=field['index'])
            output.append(_output)
        return output
    
    def output(self, player=None):
        """デフォルトの文字列表現を取得する
        ゲーム定義ファイルに`def output_state(state, player=None)`を定義することで、本処理を上書きすることができる。
        """
        outdict = {}
        for field in self.fields:
            outdict[field['shorten']] = self.output_components(field['key'])
        output = ''
        for key in sorted(outdict):
            output += '{key}: {value}{br}'.format(key=key, value=outdict[key], br=os.linesep)
        return output

class Observation(object):
    """ゲーム観測結果
    プレイヤーから観測したゲームの状態を表す。
    それはすなわち、プレイヤーが知り得ない情報は取得できない/あいまいな形でしか取得できない
    ことを意味する。
    """
    def __init__(self, state):
        """初期化
        """
        self.state = state
        self.fields = self._build_fields(state.fields)
        
    def _build_fields(self, s_fields):
        """フィールド情報を構築する
        """
        o_fields_dict = {}
        for s_field in s_fields:
            if s_field['distinguishable']:
                o_field = s_field['header']
            else:
                o_field = s_field['key']
            
            # 'turn-player'は常にobserve可能
            o_field = o_field.replace('player-1', 'turn-player')
            # プレイ人数が2名以上の場合は'prev-player'がobserve可能
            o_field = o_field.replace('player-2', 'prev-player')
            # プレイ人数が3名以上の場合は'next-player'がobserve可能
            o_field = o_field.replace('player-3', 'next-player')
            # プレイ人数がそれより多い場合は'other-player'がobserve可能
            o_field = re.sub(r'player-[4-9]{1}', 'other-player', o_field)
            s_field['mapping_to'] = o_field
            o_fields_dict[o_field] = True # 値はダミー
            
        _fields = sorted(o_fields_dict)
        
        """DEBUG
        print 'Observation.fields:', len(_fields)
        #print _fields
        """
        
    def __str__(self, *args, **kwargs):
        return object.__str__(self, *args, **kwargs)
    
    def get_header(self):
        """全プロパティのヘッダを取得する。
        """
        print 'TODO:get_header()'
        
    def to_array(self, observer=None):
        """全プロパティの値を配列で取得する。
        """
        print 'TODO:Observation.to_array()'
        return []

class Reward(object):
    """報酬
    強化学習でいうところの“報酬”を管理する。
    
    ゲーム中でスコアを獲得することが勝利に繋がるのであればそれは報酬の一つであるが、それが全てではない。
    言うまでもなく、ゲームに勝利することは最大の報酬である。
    また、ルール違反となるアクションを選択すること≒反則負けとみなせば、それは負の報酬であるとも言える。
    勝利に関連する/しない以外にも、プレイヤーが楽しいと感じる目標を達成したとき(特定のチップを獲得する等)
    にも報酬を発行するようにすれば、「感情を持ったエージェント」になることが期待される。
    """
    
    def __init__(self, player = 1, num_players = 1, negative_ratio = 0.1):
        """初期化
        1より大きい num_players が与えられた場合は他プレイヤーの報酬も合わせて管理する。
        @param player: int 管理対象プレイヤー番号
        @param num_players: int 管理対象プレイヤー数
        @param negative_ratio: float 打ち消し率
            他プレイヤーの報酬を合わせて管理するとき、その増加分を対象プレイヤーの報酬から差し引く
            ことができる。そのときの割合。
            対象プレイヤーの報酬が 1, 他プレイヤーの報酬が合計 2, 打ち消し率が 0.1の場合、取得
            される報酬は 1-2*0.1 = 0.8 となる。
        """
        assert player <= num_players
        
        self.player = player
        self.num_players = num_players
        self.negative_ratio = negative_ratio
        
        self.rewards = [0.0] * (num_players + 1)
        """報酬を管理する配列
            0 -> 管理対象プレイヤーの累積報酬値
            0以外 -> 管理対象プレイヤーごとの獲得報酬値
            @see collect()
        """
    
    def add(self, reward, player = 1):
        """獲得した報酬を加算する
        @param reward: int 報酬値
        @param player: int 獲得したプレイヤーの番号
        """
        self.rewards[player] += reward
        
    def collect(self):
        """獲得した報酬を取得する
        打ち消しについては @see __init__()
        本メソッド実行時に報酬は累積に加算され、各プレイヤーの獲得報酬値は0にリセットされる。
        """
        negative = 0
        for i in range(self.num_players + 1):
            if (i != 0) and (i != self.player):
                negative += self.rewards[i]
        reward = self.rewards[self.player] - negative * self.negative_ratio
        
        for i in range(self.num_players + 1):
            if i == 0:
                self.rewards[0] += reward
            else:
                self.rewards[i] = 0
        return reward
    
    def __str__(self, *args, **kwargs):
        return "Reward:" + str(self.rewards)

