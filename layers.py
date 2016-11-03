import tensorflow as tf
import numpy as np

def get_weights(shape, name, mask=None):
    weights_initializer = tf.contrib.layers.xavier_initializer()
    W = tf.get_variable(name, shape, tf.float32, weights_initializer)

    if mask:
        filter_mid_x = shape[0]//2
        filter_mid_y = shape[1]//2
        mask_filter = np.ones(shape, dtype=np.float32)
        mask_filter[filter_mid_x, filter_mid_y+1:, :, :] = 0.
        mask_filter[filter_mid_x+1:, :, :, :] = 0.

        if mask == 'a':
            mask_filter[filter_mid_x, filter_mid_y, :, :] = 0.
            
        W *= mask_filter 
    return W

def get_bias(shape, name):
    return tf.get_variable(name, shape, tf.float32, tf.zeros_initializer)

def conv_op(x, W):
    return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')

class GatedCNN():
    def __init__(self, W_shape, fan_in, gated=True, payload=None, mask=None, activation=True):
        self.fan_in = fan_in
        in_dim = self.fan_in.get_shape()[-1]
        self.W_shape = [W_shape[0], W_shape[1], in_dim, W_shape[2]]  
        self.b_shape = W_shape[2]

        self.payload = payload
        self.mask = mask
        self.activation = activation
        

        if gated:
            self.gated_conv()
        else:
            self.simple_conv()

    def gated_conv(self):
        W_f = get_weights(self.W_shape, "v_W", mask=self.mask)
        b_f = get_bias(self.b_shape, "v_b")
        W_g = get_weights(self.W_shape, "h_W", mask=self.mask)
        b_g = get_bias(self.b_shape, "h_b")
      
        conv_f = conv_op(self.fan_in, W_f)
        conv_g = conv_op(self.fan_in, W_g)
       
        if self.payload is not None:
            conv_f += self.payload
            conv_g += self.payload

        self.fan_out = tf.mul(tf.tanh(conv_f + b_f), tf.sigmoid(conv_g + b_g))

    def simple_conv(self):
        W = get_weights(self.W_shape, "W", mask=self.mask)
        b = get_bias(self.b_shape, "b")
        conv = conv_op(self.fan_in, W)
        if self.activation: 
            self.fan_out = tf.nn.relu(tf.add(conv, b))
        else:
            self.fan_out = tf.add(conv, b)

    def output(self):
        return self.fan_out 

