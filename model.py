import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.multiprocessing as mp
import torch.nn.init as init

from utils import *

class Model(nn.Module):
    def __init__(self, num_inputs, num_outputs):
        super(Model, self).__init__()
        self.params = Params()
        self.h_size_1 = 20
        self.h_size_2 = 20
        self.spatial_res = self.params.num_outputs
        h_size_1 = self.h_size_1
        h_size_2 = self.h_size_2
        self.total_input = num_inputs["self_input"] + num_inputs["ally_input"]

        self.p_input_1 = nn.Linear(self.total_input,h_size_2)
        self.p_input_2 = nn.Linear(h_size_2,h_size_2)
        self.p_input_3 = nn.Linear(h_size_2,h_size_2)
        self.p_input_4 = nn.Linear(h_size_2,h_size_2)

        self.init_layer(self.p_input_1)
        self.init_layer(self.p_input_2)
        self.init_layer(self.p_input_3)
        self.init_layer(self.p_input_4)

        self.v_input_1 = nn.Linear(self.total_input,h_size_2)
        self.v_input_2 = nn.Linear(h_size_2,h_size_2)
        self.v_input_3 = nn.Linear(h_size_2,h_size_2)
        self.v_input_4 = nn.Linear(h_size_2,h_size_2)

        self.init_layer(self.v_input_1)
        self.init_layer(self.v_input_2)
        self.init_layer(self.v_input_3)
        self.init_layer(self.v_input_4)

        self.v = nn.Linear(h_size_2,1)
        self.init_layer(self.v)

        if self.params.use_lstm:
            self.lstm = nn.LSTM(h_size_2,h_size_2)

        self.spatial = nn.Linear(h_size_2, self.spatial_res ** 2)
        self.init_layer(self.spatial)
        self.init_lstm()

        # mode
        self.train()
    
    def init_layer(self,layer):
        init.xavier_uniform(layer.weight, gain=np.sqrt(2))
        init.constant(layer.bias, 0.01)

    def init_lstm(self):
        self.lstm_hidden = (Variable(torch.zeros(1,1,self.h_size_2)),
                           Variable(torch.zeros(1,1,self.h_size_2)))

    def forward(self,inputs):
        p = inputs
        p = F.relu(self.p_input_1(p)).view(-1,self.h_size_2)
        p = F.relu(self.p_input_2(p)).view(-1,self.h_size_2)
        p = F.relu(self.p_input_3(p)).view(-1,self.h_size_2)
        p = F.relu(self.p_input_4(p)).view(-1,self.h_size_2)

        v = inputs
        v = F.relu(self.v_input_1(v)).view(-1,self.h_size_2)
        v = F.relu(self.v_input_2(v)).view(-1,self.h_size_2)
        v = F.relu(self.v_input_3(v)).view(-1,self.h_size_2)
        v = F.relu(self.v_input_4(v)).view(-1,self.h_size_2)

        
        if self.params.use_lstm:
            p_input_out,self.lstm_hidden = self.lstm(p_input_out,self.lstm_hidden)
        
        spatial_out = self.spatial(p)
        #import pdb
        #pdb.set_trace()
        softmax = nn.Softmax()
        _sp = (spatial_out).view(-1,self.spatial_res**2)
        spatial_act_out = softmax(_sp)
        v_out = self.v(v)
        return spatial_act_out,v_out, F.log_softmax(_sp)

class Shared_grad_buffers():
    def __init__(self, model):
        self.grads = {}
        for name, p in model.named_parameters():
            self.grads[name+'_grad'] = torch.ones(p.size()).share_memory_()

    def add_gradient(self, model):
        for name, p in model.named_parameters():
            self.grads[name+'_grad'] += p.grad.data

    def reset(self):
        for name,grad in self.grads.items():
            self.grads[name].fill_(0)
