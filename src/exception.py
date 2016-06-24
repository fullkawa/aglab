# -*- coding: utf-8 -*-

class NoMatchedProcess(Exception):
    def __init__(self, contextpath):
        self.contextpath = contextpath
        
    def __str__(self, *args, **kwargs):
        #print args #DEBUG
        return "適用可能な処理がありません; " + self.contextpath
    
class InvalidActionException(Exception):
    def __init__(self, message=''):
        self.message = message
        
    def __str__(self, *args, **kwargs):
        return "無効なアクションを実行しようとしました。; " + self.message
        
class GameendException(Exception):
    def __str__(self, *args, **kwargs):
        #print args #DEBUG
        return "ゲーム終了"
