# ========================================================================
# Copyright 2017 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================
import abc
import logging

import mxnet as mx
import numpy as np
from mxnet import gluon

from elit.nlp.util import process_online, reshape_conv2d

__author__ = 'Jinho D. Choi'


class LabelMap:
    """
    LabelMap gives the mapping between class labels and their unique IDs.
    """
    def __init__(self):
        self.index_map = {}
        self.labels = []

    def __len__(self):
        return len(self.labels)

    def index(self, label):
        """
        :param label: the class label.
        :type label: str
        :return: the ID of the class label if exists; otherwise, -1.
        :rtype: int
        """
        return self.index_map[label] if label in self.index_map else -1

    def get(self, index):
        """
        :param index: the ID of the class label.
        :type index: int
        :return: the index'th class label.
        :rtype: str
        """
        return self.labels[index]

    def add(self, label):
        """
        Adds the class label to this map if not already exist.
        :param label: the class label.
        :type label: str
        :return: the ID of the class label.
        :rtype int
        """
        idx = self.index(label)
        if idx < 0:
            idx = len(self.labels)
            self.index_map[label] = idx
            self.labels.append(label)
        return idx


class NLPModel(gluon.Block, metaclass=abc.ABCMeta):
    def __init__(self, params, **kwargs):
        """
        NLPModel defines the statistical model for the NLP component.
        :param params: a namespace containing parameters to build this model.
        :type params: argparse.Namespace
        :param kwargs: parameters for gluon.Block
        :type kwargs: dict
        """
        super(NLPModel, self).__init__(**kwargs)
        self.label_map = params.label_map
        self.trainer = None

    @abc.abstractmethod
    def create_state(self, document):
        """
        :param document: the input document.
        :type document: list of elit.util.structure.Sentence
        :return: the state to process the input document.
        :rtype: elit.nlp.state.NLPState
        """
        return

    @abc.abstractmethod
    def x(self, state):
        """
        :param state: the input state.
        :type state: elit.nlp.state.NLPState
        :return: the feature vector given the current state.
        :rtype: numpy.array, elit.nlp.state.NLPState
        """
        return

    @abc.abstractmethod
    def y(self, state):
        """
        :param state: the input state.
        :type state: elit.nlp.state.NLPState
        :return: the ID of the gold-standard label.
        :rtype: int
        """
        return

    @abc.abstractmethod
    def eval(self, state, counts):
        """
        Evaluates the predictions in the state.
        :param state: the input state.
        :type state: elit.nlp.state.NLPState
        :param counts: the evaluation counts.
        :type counts: argparse.Namespace
        :return: the evaluation score.
        :rtype: float
        """
        return

    @abc.abstractmethod
    def set_labels(self, state):
        """
        Sets the string labels to each sentence using the predicted output.
        :param state: the input state.
        :type state: elit.nlp.state.NLPState
        """
        pass

    def trim_output(self, state):
        """
        Trims the output of the state with respect to the size of the label map.
        :param state: the input state.
        :type state: elit.nlp.state.NLPState
        """
        num_class = len(self.label_map)

        if state.output and num_class < len(state.output[0]):
            state.output = [[o[:num_class] for o in output] for output in state.output]


X_FST = np.array([1, 0]).astype('float32')  # the first word
X_LST = np.array([0, 1]).astype('float32')  # the last word
X_ANY = np.array([0, 0]).astype('float32')  # any other word


def x_position(tok_id, window, size):
    """
    :param window: the context window.
    :type window: int
    :return: the position embedding of the (self.tok_id + window)'th word.
    :rtype: numpy.array
    """
    i = tok_id + window
    return X_FST if i == 0 else X_LST if i+1 == size else X_ANY


def x_extract(tok_id, window, size, emb, zero):
    """
    :param window: the context window.
    :type window: int
    :param emb: the list of embeddings.
    :type emb: numpy.array
    :param zero: the vector for zero-padding.
    :type zero: numpy.array
    :return: the (self.tok_id + window)'th embedding if exists; otherwise, the zero-padded embedding.
    """
    i = tok_id + window
    return emb[i] if 0 <= i < size else zero