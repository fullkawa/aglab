# -*- coding: utf-8 -*-

class GameendException(Exception):
    def __str__(self, *args, **kwargs):
        #print args #DEBUG
        return "ゲーム終了"
