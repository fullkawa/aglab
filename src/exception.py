# -*- coding: utf-8 -*-

class NoMatchedProcess(Exception):
    def __init__(self, contextpath):
        self.contextpath = contextpath
        
    def __str__(self, *args, **kwargs):
        #print args #DEBUG
        return "適用可能な処理がありません; " + self.contextpath
    
class GameendException(Exception):
    def __str__(self, *args, **kwargs):
        #print args #DEBUG
        return "ゲーム終了"
