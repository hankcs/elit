import fasttext
import logging

'''
path = '/home/ubuntu/gdrive/public/word-embeddings/corpus.friends+nyt+wiki+amazon.fasttext.skip.d200.bin'
print(path)
v = fasttext.load_model(path)

print(type(v))
print(v[''])
print(v['@#r$%'])
'''
import mxnet as mx
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

xs = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], dtype=np.float32)
ys = np.array([0,1,2,3], dtype=np.float32)

net = mx.sym.Variable('data')
net = mx.sym.FullyConnected(net, name='fc1', num_hidden=4)
net = mx.sym.SoftmaxOutput(net, name='softmax')
mod = mx.mod.Module(symbol=net)

dat = mx.io.NDArrayIter(data=xs, label=ys, batch_size=4)
mod.fit(train_data=dat, num_epoch=10)

xxs = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], dtype=np.float32)
dat = mx.io.NDArrayIter(xxs, None, batch_size=8)
mod.bind(dat.provide_data, None, for_training=False, force_rebind=True)
ys = mod.predict(dat).asnumpy()
print(ys[0].shape)
