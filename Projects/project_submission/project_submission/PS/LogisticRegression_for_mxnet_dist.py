import os
import sys
import numpy as np
import mxnet as mx
import logging
import tensorflow as tf
import gc

data = mx.symbol.Variable('data')
fc1  = mx.symbol.FullyConnected(data = data, num_hidden=1)
act1 = mx.symbol.Activation(data = fc1, act_type='sigmoid') 
mlp  = mx.symbol.SVMOutput(data = act1, name = 'softmax')

devices = [mx.cpu(0)]
model = mx.model.FeedForward(ctx=devices, symbol=mlp, num_epoch=1, learning_rate=0.01)
eval_metrics = ['accuracy']
batch_end_callback = []
batch_end_callback.append(mx.callback.Speedometer(1, 10))

num_features = 33762578
g = tf.Graph()
with g.as_default():
    filename_queue = tf.train.string_input_producer([
        "/home/ubuntu/criteo-tfr/tfrecords00",
        "/home/ubuntu/criteo-tfr/tfrecords01",
        "/home/ubuntu/criteo-tfr/tfrecords02",
        "/home/ubuntu/criteo-tfr/tfrecords03",
        "/home/ubuntu/criteo-tfr/tfrecords04",
    ], num_epochs=None)
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(serialized_example, features={
                                        'label': tf.FixedLenFeature([1], dtype=tf.int64),
                                        'index' : tf.VarLenFeature(dtype=tf.int64),
                                        'value' : tf.VarLenFeature(dtype=tf.float32),})
    label = features['label']
    index = features['index']
    value = features['value']
    dense_feature = tf.sparse_to_dense(tf.sparse_tensor_to_dense(index), [num_features,], tf.sparse_tensor_to_dense(value))

    num_points = 1
    dataset = np.ndarray(shape=(num_points,num_features),dtype=float)
    dataset_labels = np.ndarray(shape=(num_points,))

    batch_size = 1
    num_iteration_train = 100
    coord = tf.train.Coordinator()
    sess = tf.Session()
    sess.run(tf.initialize_all_variables())
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)		
    for i in range(num_iteration_train):
        dataset[0,:] = sess.run(dense_feature)
        dataset_labels[0] = sess.run(label)
        if dataset_labels[0] == -1.0:
            dataset_labels[0] = 0
        train = mx.io.NDArrayIter(data=dataset, label=dataset_labels, batch_size=batch_size, shuffle=False)			
        model.fit(X=train, eval_metric=eval_metrics, batch_end_callback=batch_end_callback)
        print "this is vm-38-1, traing{0}".format(i)
    coord.request_stop()
    coord.join(threads)
    sess.close()

    num_iteration_test = 30
    num_correct = 0
    coord_test = tf.train.Coordinator()
    sess_test = tf.Session()
    sess_test.run(tf.initialize_all_variables())
    threads_test = tf.train.start_queue_runners(sess=sess_test, coord=coord_test)		
    for i in range(num_iteration_test):
        print "this is vm-38-1, testing{0}".format(i)
        dataset[0,:] = sess_test.run(dense_feature)
        dataset_labels[0] = sess_test.run(label)
        if dataset_labels[0] == -1.0:
            dataset_labels[0] = 0
        test = mx.io.NDArrayIter(data=dataset, label=dataset_labels, batch_size=batch_size, shuffle=False)
        if model.score(X=test) == 1.0:
            num_correct += 1
    print num_correct
    coord_test.request_stop()
    coord_test.join(threads_test)
    sess_test.close()
		
gc.collect()	  






