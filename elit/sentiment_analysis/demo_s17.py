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
from elit.tokenizer import english_tokenizer
from elit.sentiment_analysis.decode import S17Model
import os

__author__ = 'Bonggun Shin'


os.environ["CUDA_VISIBLE_DEVICES"] = '2'
sentences = ["I feel a little bit tired today, but I am really happy!",
             "Although the rain stopped, I hate this thick cloud in the sky."]

tokenized_sentences = []
for s in sentences:
    tokenized_sentences.append(english_tokenizer.tokenize(s, False))

sa = S17Model()
y, att, raw_att = sa.decode(tokenized_sentences)

print(y)

