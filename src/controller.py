# -*- coding: utf-8 -*-

"""コントローラ
本ライブラリにおけるコントローラとは人間に代わってアクション選択を行うプログラムを指す。
"""

import random

class Randomizer(object):
    """選択可能なアクションからランダムに選択を行うコントローラ
    """

    def __init__(self, params):
        """初期化
        @param params: dict パラメータ
            'actions': 選択可能なアクションの数
            'seed':    乱数シード
        """
        self.actions = 1
        if 'actions' in params:
            self.actions = int(params['actions'])
        
        if 'seed' in params:
            random.seed(params['seed'])
        
    def action(self, observation):
        """アクション選択を行う
        @param observation: 観測結果(本コントローラでは使用しない)
        @return: 選択されたアクションのインデックス[0-(actions-1)]
        """
        return random.randint(0, self.actions - 1)
