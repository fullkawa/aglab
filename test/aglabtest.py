# -*- coding: utf-8 -*-

import unittest

import math
import sys

import aglab
from definition import test

class StateTestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.state = aglab.State(test)
        #print
    
    def test__init(self):
        state = self.state
        self.assertEqual(len(state.fields), 16)
        self.assertEqual(len(state.components), 4)
        self.assertEqual(len(state.data.loc[:, 'value']), 66)
        
        self.assertEqual(state.get_value(key='$cxt-1'), 1)
        self.assertEqual(state.get_value(scope='public', column='unknown')[0], aglab.State.VALUE_KNOWN)
        self.assertEqual(state.get_value(scope='hidden', column='unknown')[0], aglab.State.VALUE_UNKNOWN)
        self.assertEqual(state.get_value(fkey='player-1_hand', column='unknown')[0], aglab.State.VALUE_UNKNOWN) # 初期化時点ではプレイヤーが決定して
        self.assertEqual(state.get_value(fkey='player-2_hand', column='unknown')[0], aglab.State.VALUE_UNKNOWN) # いないので、これでいい
        #print state.data #DEBUG
        #print
        """
                                                             unknown  value
ckey         cindex propname fkey            findex scope                  
$cxt-1                                       NaN    public         0    1.0
$player-name                                 NaN    public         0    NaN
C1           0      _placed  F1              0.0    hidden         1    NaN
                                             1.0    hidden         1    NaN
                                             2.0    hidden         1    NaN
                                             3.0    hidden         1    NaN
                             F2              0.0    public         0    NaN
                                             1.0    public         0    NaN
                                             2.0    public         0    NaN
                                             3.0    public         0    NaN
                             player-1_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-1_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
                             player-2_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-2_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
C2           0      _placed  F1              0.0    hidden         1    NaN
                                             1.0    hidden         1    NaN
                                             2.0    hidden         1    NaN
                                             3.0    hidden         1    NaN
                             F2              0.0    public         0    NaN
                                             1.0    public         0    NaN
                                             2.0    public         0    NaN
                                             3.0    public         0    NaN
                             player-1_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-1_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
...                                                              ...    ...
             1      _placed  F1              2.0    hidden         1    NaN
                                             3.0    hidden         1    NaN
                             F2              0.0    public         0    NaN
                                             1.0    public         0    NaN
                                             2.0    public         0    NaN
                                             3.0    public         0    NaN
                             player-1_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-1_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
                             player-2_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-2_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
             2      _placed  F1              0.0    hidden         1    NaN
                                             1.0    hidden         1    NaN
                                             2.0    hidden         1    NaN
                                             3.0    hidden         1    NaN
                             F2              0.0    public         0    NaN
                                             1.0    public         0    NaN
                                             2.0    public         0    NaN
                                             3.0    public         0    NaN
                             player-1_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-1_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
                             player-2_hand   0.0    private        1    NaN
                                             1.0    private        1    NaN
                             player-2_played 0.0    public         0    NaN
                                             1.0    public         0    NaN
        """
    
    def test_set_player(self):
        state = self.state
        p1_hand = state.get_value(propname='_placed', fkey='player-1_hand', scope='private', column='unknown')
        p2_hand = state.get_value(propname='_placed', fkey='player-2_hand', scope='private', column='unknown')
        player = state.get_value(key='$player')
        assert p1_hand[0] == aglab.State.VALUE_UNKNOWN
        assert p2_hand[0] == aglab.State.VALUE_UNKNOWN
        assert math.isnan(player)
        
        state.set_player(1)
        p1_hand = state.get_value(propname='_placed', fkey='player-1_hand', scope='private', column='unknown')
        p2_hand = state.get_value(propname='_placed', fkey='player-2_hand', scope='private', column='unknown')
        player = state.get_value(key='$player')
        self.assertEqual(p1_hand[0], aglab.State.VALUE_KNOWN) #自分の手札は'known'となる
        self.assertEqual(p2_hand[0], aglab.State.VALUE_UNKNOWN)
        self.assertEqual(player, 1)
    
    def test_last_1(self):
        """last():コンポーネントがセットされていない場合
        """
        index = self.state.last('P1.p')
        self.assertEqual(index, -1)
    
    def test_last_2(self):
        """last():コンポーネントがセットされている場合
        """
        state = self.state
        state.set_component('C1', ('F1', 0))
        self.assertEqual(state.last('F1'), 0)
        
        state.set_component(('C2', 1), ('F1', 1))
        self.assertEqual(state.last('F1'), 1)
    
    def test_set_component_1(self):
        """set_component():テストケース1
        """
        state = self.state
        """どこにも配置されていない状態
        """
        
        state.set_component('C1', ('F1', 0))
        """ -> hiddenフィールドへ配置
        """
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component='C1', field=('F1', 0), column='unknown'))
        self.assertEqual(state.VALUE_EXISTENT,
            state.get_value(component='C1', field=('F1', 0)))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component='C1', field=('F1', 1), column='unknown'))
        self.assertEqual(True,
            math.isnan(state.get_value(component='C1', field=('F1', 1))))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component=('C2', 0), field=('F1', 0), column='unknown'))
        self.assertEqual(state.VALUE_NON_EXISTENT,
            state.get_value(component=('C2', 0), field=('F1', 0)))
        
        state.set_component(('C2', 0), ('F1', 1))
        """ -> さらにもう1枚配置
        """
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component=('C2', 0), field=('F1', 1), column='unknown'))
        self.assertEqual(state.VALUE_EXISTENT,
            state.get_value(component=('C2', 0), field=('F1', 1)))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component=('C2', 0), field=('F1', 2), column='unknown'))
        self.assertEqual(True,
            math.isnan(state.get_value(component=('C2', 0), field=('F1', 2))))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component=('C2', 0), field=('F1', 0), column='unknown'))
        self.assertEqual(state.VALUE_NON_EXISTENT,
            state.get_value(component=('C2', 0), field=('F1', 0)))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component='C1', field=('F1', 1), column='unknown'))
        self.assertEqual(state.VALUE_NON_EXISTENT,
            state.get_value(component='C1', field=('F1', 1)))
    
    def _set_F1_all(self, state):
        state.set_component('C1', ('F1', 0))
        state.set_component(('C2', 0), ('F1', 1))
        state.set_component(('C2', 1), ('F1', 2))
        state.set_component(('C2', 2), ('F1', 3))
    
    def test_move_component_1(self):
        """set_component():テストケース1
        """
        state = self.state
        self._set_F1_all(state)
        """すべてF1にセットされた状態
        """
        
        state.move_component(('F1', 0), ('player-1_hand', 0))
        #print state.data #DEBUG
        """ -> hiddenフィールドへ移動
        """
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component='C1', field=('player-1_hand', 0), column='unknown'))
        self.assertEqual(state.VALUE_EXISTENT,
            state.get_value(component='C1', field=('player-1_hand', 0)))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component=('C2', 0), field=('player-1_hand', 0), column='unknown'))
        self.assertEqual(state.VALUE_NON_EXISTENT,
            state.get_value(component=('C2', 0), field=('player-1_hand', 0)))

        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component='C1', field=('F1', 0), column='unknown'))
        self.assertEqual(True,
            math.isnan(state.get_value(component='C1', field=('F1', 0))))
        
        self.assertEqual(state.VALUE_UNKNOWN,
            state.get_value(component=('C2', 0), field=('F1', 0), column='unknown'))
        self.assertEqual(True,
            math.isnan(state.get_value(component=('C2', 0), field=('F1', 0))))
        
    def test_index_component(self):
        state = self.state
        state.set_component('C1', ('P1.h', 1))
        index = state.index_component('C1', 'P1.h')
        
        self.assertEqual(index, 1)
        
    def test_output_component_case1(self):
        """Case1: プレイヤー指定なし(DEBUG); 非公開状態
        """
        state = self.state
        output = state.output_component(field=('F1', 0))
        self.assertEqual(' ', output)
        
        state.set_component('C1', ('F1', 1))
        output = state.output_component(field=('F1', 1))
        self.assertEqual('-1', output)
        
        state.set_component(('C2', 1), ('F1', 2))
        output = state.output_component(field=('F1', 2))
        self.assertEqual('-2', output)
        
    def test_output_component_case2(self):
        """Case1: プレイヤー指定なし(DEBUG); 公開状態
        """
        state = self.state
        output = state.output_component(field=('F2', 0))
        self.assertEqual(' ', output)
        
        state.set_component('C1', ('F2', 1))
        output = state.output_component(field=('F2', 1))
        self.assertEqual(' 1', output)
        
        state.set_component(('C2', 1), ('F2', 2))
        output = state.output_component(field=('F2', 2))
        self.assertEqual(' 2', output)
        
    def test_output_components_case1(self):
        """Case1: プレイヤー指定なし(DEBUG); 非公開状態
        """
        state = self.state
        output = state.output_components(fkey='F1')
        self.assertEqual(4, len(output))
        self.assertEqual(' ', output[0])
        self.assertEqual(' ', output[3])
        
        state.set_component('C1', ('F1', 1))
        state.set_component(('C2', 1), ('F1', 2))
        output = state.output_components(fkey='F1')
        self.assertEqual(4, len(output))
        self.assertEqual(' ', output[0])
        self.assertEqual('-1', output[1])
        self.assertEqual('-2', output[2])
        self.assertEqual(' ', output[3])
        
    def test_output_components_case2(self):
        """Case2: プレイヤー指定なし(DEBUG); 公開状態
        """
        state = self.state
        output = state.output_components(fkey='F2')
        self.assertEqual(4, len(output))
        self.assertEqual(' ', output[0])
        self.assertEqual(' ', output[3])
        
        state.set_component('C1', ('F2', 1))
        state.set_component(('C2', 1), ('F2', 2))
        output = state.output_components(fkey='F2')
        self.assertEqual(4, len(output))
        self.assertEqual(' ', output[0])
        self.assertEqual(' 1', output[1])
        self.assertEqual(' 2', output[2])
        self.assertEqual(' ', output[3])


class RewardTestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        #print
    
    def testAdd_1(self):
        reward = aglab.Reward()
        reward.add(1)
        
        self.assertEqual(0, reward.rewards[0])
        self.assertEqual(1, reward.rewards[1])
        
    def testAdd_2(self):
        reward = aglab.Reward(player=2, num_players=3)
        reward.add(1, player=1)
        reward.add(2, player=2)
        
        self.assertEqual(0, reward.rewards[0])
        self.assertEqual(1, reward.rewards[1])
        self.assertEqual(2, reward.rewards[2])
        self.assertEqual(0, reward.rewards[3])
        
    def testCollect_1(self):
        reward = aglab.Reward()
        r = reward.collect()
        self.assertEqual(r, 0)
        self.assertEqual(0, reward.rewards[0])
        self.assertEqual(0, reward.rewards[1])
        
        reward.add(1)
        r = reward.collect()
        self.assertEqual(r, 1)
        self.assertEqual(1, reward.rewards[0])
        self.assertEqual(0, reward.rewards[1])
        
        reward.add(2)
        r = reward.collect()
        self.assertEqual(r, 2)
        self.assertEqual(3, reward.rewards[0])
        self.assertEqual(0, reward.rewards[1])
        
    def testCollect_2(self):
        reward = aglab.Reward(player=2, num_players=3)
        reward.add(1, player=1)
        reward.add(2, player=2)
        r = reward.collect()
        self.assertEqual(r, 1.9)
        self.assertEqual(1.9, reward.rewards[0])
        self.assertEqual(0, reward.rewards[1])
        self.assertEqual(0, reward.rewards[2])
        
