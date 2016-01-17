# -*- coding: utf-8 -*-

"""
ゲーム解析ツール

プレイデータを機械学習させることにより、ゲームを解析する。

@see http://qiita.com/syoamakase/items/db883d7ebad7a2220233

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

# 隠れ層のノード数
HIDDEN_UNIT_SIZE = DATA_NUM / 2


data = np.genfromtxt(open(SVDATA_FILE), delimiter=',', filling_values=0)
[params, scores] = np.hsplit(data, [DATA_NUM])
[train_params, test_params] = np.vsplit(params, [len(params) * TRAIN_DATA_RATIO])
[train_scores, test_scores] = np.vsplit(scores, [len(scores) * TRAIN_DATA_RATIO])

print 'test_params:'
print test_params # debug
print 'test_scores:'
print test_scores # debug

with tf.Graph().as_default():
  def inference(input_, W1, b1, W2, b2):
    with tf.name_scope('inference-l1') as scope:
      l1_ = tf.nn.relu(tf.matmul(input_, W1) + b1)
    with tf.name_scope('inference-l2') as scope:
      y = tf.nn.relu(tf.matmul(l1_, W2) + b2)
    return y

  def loss(output_, supervisor_):
    with tf.name_scope('loss') as scope:
      loss = tf.reduce_mean(tf.square(output_ - supervisor_))
      tf.scalar_summary('loss', loss)
    return loss

  def training(loss_):
    with tf.name_scope('training') as scope:
      train_step = tf.train.AdagradOptimizer(0.04).minimize(loss_)
      #train_step = tf.train.AdamOptimizer().minimize(loss_)
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

  """ ゼロで初期化すると学習できない
  W1 = tf.Variable(tf.zeros([DATA_NUM, HIDDEN_UNIT_SIZE]), name='w1')
  b1 = tf.Variable(tf.zeros([HIDDEN_UNIT_SIZE]), name='b1')
  W2 = tf.Variable(tf.zeros([HIDDEN_UNIT_SIZE, 1]), name='w2')
  b2 = tf.Variable(tf.zeros([1]), name='b2')
  """
  W1 = tf.Variable(tf.ones([DATA_NUM, HIDDEN_UNIT_SIZE]), name='w1')
  b1 = tf.Variable(tf.ones([HIDDEN_UNIT_SIZE]), name='b1')
  W2 = tf.Variable(tf.ones([HIDDEN_UNIT_SIZE, 1]), name='w2')
  b2 = tf.Variable(tf.ones([1]), name='b2')

  output_ = inference(param_placeholder, W1, b1, W2, b2)
  loss_op = loss(output_, score_placeholder)
  training_op = training(loss_op)

  summary_op = tf.merge_all_summaries()

  with tf.Session() as sess:
    summary_writer = tf.train.SummaryWriter('data', graph_def=sess.graph_def)
    tf.initialize_all_variables().run()
    
    best_loss = float('inf')
    for step in range(10000):
      loss_train = sess.run(loss_op, feed_dict=feed_dict_train)
      sess.run(training_op, feed_dict=feed_dict_train)
      if loss_train < best_loss:
        best_loss = loss_train
        best_match = sess.run(output_, feed_dict=feed_dict_test)
      if step % 500 == 0:
        summary_str = sess.run(summary_op, feed_dict=feed_dict_train)
        #summary_str += sess.run(summary_op, feed_dict=feed_dict_test)
        summary_writer.add_summary(summary_str, step)
        print 'loss_train:', loss_train, ', best_loss:', best_loss

    print 'w1:', sess.run(W1), ', b1:', sess.run(b1)
    print 'w2:', sess.run(W2), ', b2:', sess.run(b2)
    print 'best_match:', best_match


