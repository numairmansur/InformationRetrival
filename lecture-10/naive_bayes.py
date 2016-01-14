"""
Copyright 2015, University of Freiburg.

Elmar Haussmann <haussmann@cs.uni-freiburg.de>
"""

import re
import numpy as np
from scipy.sparse import csr_matrix


def generate_vocab(filename):
    """Read from the provided file name and return vocabularies mapping from
    string to ID for words and classes/labels.

    You should call this ONLY on the training part of your data.
    """
    next_class_id = 0
    next_feature_id = 0
    # Map from label/class to label id.
    class_vocab = dict()
    # Map from word to word id.
    word_vocab = dict()
    with open(filename, "r") as f:
        for line in f:
            cols = line.strip().split('\t')
            label, text = cols[0], cols[1]
            if label not in class_vocab:
                class_vocab[label] = next_class_id
                next_class_id += 1
            words = split_into_words(text)
            for w in words:
                if w not in word_vocab:
                    word_vocab[w] = next_feature_id
                    next_feature_id += 1
    return word_vocab, class_vocab


def split_into_words(text):
    """Split the given text into words. Returns a list of words.
    """
    text = re.sub("\W+", " ", text)
    words = text.lower().split()
    return words


def read_labeled_data(filename, class_vocab, word_vocab):
    """Read the file and return a sparse document-term matrix as well as a list
    of labels of each document. You need to provide a class and word
    vocabulary. Words not in the vocabulary are ignored.

    The returned document-term matrix X has size n x m, where n is the number
    of documents and m the number of features (i.e. word ids). The value at
    i, j denotes the number of times word id j is present in document i.

    The returned labels vector y has size n (one label for each document). The
    value at index j denotes the label (class id) of document j.
    """
    labels = []
    row, col, value = [], [], []
    num_examples = 0
    num_cols = len(word_vocab)
    with open(filename, "r") as f:
        for i, line in enumerate(f):
            num_examples += 1
            cols = line.strip().split('\t')
            label, text = cols[0], cols[1]
            labels.append(class_vocab[label])
            words = split_into_words(text)
            for w in words:
                if w in word_vocab:
                    w_id = word_vocab[w]
                    row.append(i)
                    col.append(w_id)
                    # Duplicate values are summed.
                    value.append(1.0)
    X = csr_matrix((value, (row, col)), shape=(num_examples, num_cols))
    y = np.array(labels)
    return X, y


class NaiveBayes(object):

    def train(self, X, y):
        """Train on the sparse document-term matrix X and associated labels y.
        """

    def predict(self, X):
        """Predicts a label for each example in the document-term matrix.
        Return a list of predicted labels.
        """

    def evaluate(self, X, y):
        """Predict the labels of X and print evaluation statistics.
        """
