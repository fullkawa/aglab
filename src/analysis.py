# -*- coding: utf-8 -*-

"""
ゲーム解析ツール

プレイデータを機械学習させることにより、ゲームを解析する。

@author fullkawa
"""

import numpy as np
import os
import tensorflow as tf

# データディレクトリ
DATA_DIR = os.path.join('..', 'data')

# 学習データディレクトリ
SVDATA_DIR = os.path.join(DATA_DIR, 'supervisor')

# 学習データファイル
SVDATA_FILE = os.path.join(SVDATA_DIR, 'data.csv')

# データの列数
DATA_NUM = 63

# 学習データの割合
TRAIN_DATA_RATIO = .9

# FIXME:未使用→隠れ層のノード数
HIDDEN_UNIT_SIZE = 62


data = np.genfromtxt(open(SVDATA_FILE), delimiter=',', filling_values=0)
[params, scores] = np.hsplit(data, [DATA_NUM])
[train_params, test_params] = np.vsplit(params, [len(params) * TRAIN_DATA_RATIO])
[train_scores, test_scores] = np.vsplit(scores, [len(scores) * TRAIN_DATA_RATIO])
print 'test_params:'
print test_params # debug
print 'test_scores:'
print test_scores # debug

with tf.Graph().as_default():
  def inference(input_, W, b):
    with tf.name_scope('inference') as scope:
      y = tf.nn.softmax(tf.matmul(input_, W) + b)
    return y

  def loss(output_, supervisor_):
    with tf.name_scope('loss') as scope:
      cross_entropy = -tf.reduce_sum(supervisor_ * tf.log(output_))
      tf.scalar_summary('cross_entropy', cross_entropy)
    return cross_entropy

  def training(loss_):
    with tf.name_scope('training') as scope:
      train_step = tf.train.GradientDescentOptimizer(0.01).minimize(loss_)
    return train_step
  
  param_placeholder = tf.placeholder('float', [None, DATA_NUM], name='params')
  score_placeholder = tf.placeholder('float', [None, 1], name='scores')
  feed_dict_train = {
    param_placeholder: train_params,
    score_placeholder: train_scores
  }
  feed_dict_test = {
    param_placeholder: test_params,
    score_placeholder: test_scores
  }

  W = tf.Variable(tf.zeros([DATA_NUM, 1]), name='w1')
  b = tf.Variable(tf.zeros([1]), name='b1')

  output_ = inference(param_placeholder, W, b)
  loss_ = loss(output_, score_placeholder)
  training_op = training(loss_)

  summary_op = tf.merge_all_summaries()

  with tf.Session() as sess:
    summary_writer = tf.train.SummaryWriter('data', graph_def=sess.graph_def)
    tf.initialize_all_variables().run()
    
    best_loss = float('inf')
    for step in range(10000):
      sess.run(training_op, feed_dict=feed_dict_train)
      loss_test = sess.run(loss_, feed_dict=feed_dict_test)
      if loss_test < best_loss:
        best_loss = loss_test
        best_match = sess.run(output_, feed_dict=feed_dict_test)
      if step % 100 == 0:
        summary_str = sess.run(summary_op, feed_dict=feed_dict_train)
        #summary_str += sess.run(summary_op, feed_dict=feed_dict_test)
        summary_writer.add_summary(summary_str, step)
        print 'loss_test:', loss_test, ', best_loss:', best_loss

    print 'w1:', sess.run(W), ', b1:', sess.run(b)
    print 'best_match:', best_match


