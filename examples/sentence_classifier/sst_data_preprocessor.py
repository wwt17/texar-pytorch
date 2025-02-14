# Copyright 2019 The Texar Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Preparing the SST2 dataset.
"""

from typing import Tuple

import argparse
import os
import re

import texar.torch as tx

parser = argparse.ArgumentParser()
parser.add_argument(
    '--data-path', type=str, default='./data',
    help="E.g., ./data/sst2.train.sentences.txt. If not exists, the directory "
         "will be created and SST raw data will be downloaded.")
args = parser.parse_args()


def clean_sst_text(text: str) -> str:
    """Cleans tokens in the SST data, which has already been tokenized.
    """
    text = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip().lower()


def transform_raw_sst(data_path: str, raw_filename: str, new_filename: str) -> \
        Tuple[str, str]:
    """Transforms the raw data format to a new format.
    """
    fout_x_name = os.path.join(data_path, new_filename + '.sentences.txt')
    fout_x = open(fout_x_name, 'w', encoding='utf-8')
    fout_y_name = os.path.join(data_path, new_filename + '.labels.txt')
    fout_y = open(fout_y_name, 'w', encoding='utf-8')

    fin_name = os.path.join(data_path, raw_filename)
    with open(fin_name, 'r', encoding='utf-8') as fin:
        for line in fin:
            parts = line.strip().split()
            label = parts[0]
            sent = ' '.join(parts[1:])
            sent = clean_sst_text(sent)
            fout_x.write(sent + '\n')
            fout_y.write(label + '\n')

    return fout_x_name, fout_y_name


def prepare_data():
    """Preprocesses SST2 data.
    """
    train_path = os.path.join(args.data_path, "sst.train.sentences.txt")
    if not os.path.exists(train_path):
        url = ('https://raw.githubusercontent.com/ZhitingHu/'
               'logicnn/master/data/raw/')
        files = ['stsa.binary.phrases.train', 'stsa.binary.dev',
                 'stsa.binary.test']
        for fn in files:
            tx.data.maybe_download(url + fn, args.data_path, extract=True)

    fn_train, _ = transform_raw_sst(
        args.data_path, 'stsa.binary.phrases.train', 'sst2.train')
    transform_raw_sst(args.data_path, 'stsa.binary.dev', 'sst2.dev')
    transform_raw_sst(args.data_path, 'stsa.binary.test', 'sst2.test')

    vocab = tx.data.make_vocab(fn_train)
    fn_vocab = os.path.join(args.data_path, 'sst2.vocab')
    with open(fn_vocab, 'w', encoding='utf-8') as f_vocab:
        for v in vocab:
            f_vocab.write(v + '\n')

    print('Preprocessing done: {}'.format(args.data_path))


def main():
    """Entrypoint.
    """
    prepare_data()


if __name__ == '__main__':
    main()
