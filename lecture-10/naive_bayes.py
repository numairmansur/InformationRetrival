"""
Copyright 2015, University of Freiburg.

Elmar Haussmann <haussmann@cs.uni-freiburg.de>
"""

import re
import numpy as np
from scipy.sparse import csr_matrix
import operator
from collections import Counter


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


class NaiveBayes:

    def train(self, X, y):
        """Train on the sparse document-term matrix X and associated labels y.
        """
        print("Training . . .")
        print()
        Tc = dict() # Number of documnets in a class
        Tc = Counter(y) # counts how many documents belong to each class
        # print(Counter(y).keys())
        # print(Counter(y).values())
        total_number_of_documents = len(y)
        Pc = dict() # The probablity of a class 
        for classs in Tc.keys():
            Pc[classs] = Tc[classs]/total_number_of_documents
        print(Pc)
        #print(list(set(y)))

        # Make a class-term matrix
        row, col , value = [], [], []
        
        for row_val in sorted(set(y)):
            y_index = 0
            for val in y:
                if(row_val == val):
                    row.append(row_val)
                    col.append(y_index)
                    value.append(1)
                y_index+=1
        #print(row)
        #print(col)
        #print(value)
        class_term_matrix = csr_matrix((value, (row,col)), shape=(len(sorted(set(y))), total_number_of_documents))
        #print(class_term_matrix.todense())

        # Count Matrix
        count_matrix = class_term_matrix * X
        print()
        print(count_matrix.todense())
        print("******")
        print(count_matrix[0,:].data)
        print(count_matrix.sum(axis=1))
        a = np.divide(count_matrix[0,:].data, count_matrix.sum(axis=1)[0,:])
        print(a)
        print("*****")
        row_indices, col_indices = count_matrix.nonzero()
        print(count_matrix.sum(axis=1)[row_indices,0])
        count_matrix[row_indices,col_indices] /= count_matrix.sum(axis=1)[row_indices,0]
        print(count_matrix.todense())

        #Make a probability Dictionary




        print("DONE !")
        print(row_indices)
        print(col_indices)
        print()

    def predict(self, X):
        """Predicts a label for each example in the document-term matrix.
        Return a list of predicted labels.
        """

    def evaluate(self, X, y):
        """Predict the labels of X and print evaluation statistics.
        """



if __name__ == "__main__":
    print("Generating vocabulary . .")
    word_vocab, class_vocab = generate_vocab("example.txt")
    print("DONE")
    print(sorted(word_vocab.items(), key=operator.itemgetter(1)))
    print(class_vocab)
    print()
    print("Readign labeled data . .")
    x,y = read_labeled_data("example.txt", class_vocab, word_vocab)
    print("Done")
    print(x.todense())
    print(y)
    print()
    # Passing the document-term matrix and other things to the class object
    nb = NaiveBayes()
    nb.train(x,y)
