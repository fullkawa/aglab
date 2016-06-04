# -*- coding: utf-8 -*-
import numpy as np
import re

def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    :see https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], dict)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
            
def dict_search(lst, search):
    """リストに入っているdict型の値のうち、searchに一致するものだけを取得する
    """
    searched = []
    skey, svalue = search
    for item in lst:
        if item[skey] == svalue:
            searched.append(item)
    return searched

def dict_value(lst, key, search=None):
    """リストに入っているdict型の値を取得する
    """
    value = None
    if search is not None:
        lst = dict_search(lst, search)
    if len(lst) > 0:
        value = lst[0][key]
    return value

def append_value(lst, value):
    """リストのサイズを変更せずに値を追加する
    つまり、リスト内の最初のNaNに値を上書きする。
    それがなければ最後の要素に値を上書きする。
    """
    lst[get_lastindex(lst)] = value

def get_lastindex(lst):
    """リスト「内」の最後のインデックスを取得する
    """
    for index, item in enumerate(lst):
        if np.isnan(item):
            break
    return index

def get_key_and_index(item):
    """itemをパースし、キーとインデックスを取得する
    @return: key, index
    """
    if isinstance(item, tuple) and (len(item) > 1):
        return item[0], item[1]
    if isinstance(item, str):
        matched = re.match(r'([-.\w]+)\[(\d+)\]', item)
        if matched:
            return matched.group(1), int(matched.group(2))
    return item, None

def build_urlpath(lst):
    """リストからURLパス形式の文字列を構築する
    リスト内の各アイテムは文字列かタプルであること。
    タブルの場合はそれを文字列に展開((key, value)->'key:value')した上で変換される。
    @see utiltest.py
    """
    for i, item in enumerate(lst):
        if isinstance(item, tuple):
            lst[i] = ':'.join(item)
            
    path = '/'.join(lst)
    return path

def build_urlqs(lst):
    """URLクエリストリングを構築する
    リスト内の各アイテムはタプルであること。
    逆(パース)は urlparse.parse_qs() を使うこと。
    @see utiltest.py
    """
    _lst = []
    for item in lst:
        key, value = item
        _lst.append('{0}={1}'.format(key, value))
        
    qs = '&'.join(_lst)
    return qs


