"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Evgeny Anatskiy <evgeny.anatskiy@jupiter.uni-freiburg.de>
Numair Mansur <numair.mansur@gmail.com>
"""

import re
import sys
import logging
from math import log
# from time import time

import numpy as np
from scipy.sparse import csr_matrix

logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def norm_row_l2(matrix):
    """ L2 normalize rows of a dense matrix.
    >>> m = np.matrix([[1, 2], [2, 3]], dtype=float)
    >>> norm_row_l2(m)
    >>> m
    matrix([[ 0.4472136 ,  0.89442719],
            [ 0.5547002 ,  0.83205029]])
    """
    sq = np.multiply(matrix, matrix)
    row_sums = np.array(sq.sum(axis=1))[:, 0]
    row_sums = np.sqrt(row_sums)
    matrix /= row_sums[:, None]


def norm_sp_row_l2(matrix):
    """ L2 normalize rows of a sparse csr_matrix.
    >>> m = np.matrix([[0, 1, 2], [0, 2, 3]], dtype=float)
    >>> m = csr_matrix(m)
    >>> norm_sp_row_l2(m)
    >>> m[0, 0]
    0.0
    >>> m[0, 1]
    0.44721359549995793
    >>> m[0, 2]
    0.89442719099991586
    >>> m[1, 0]
    0.0
    >>> m[1, 1]
    0.55470019622522915
    >>> m[1, 2]
    0.83205029433784372
    """
    sq = matrix.multiply(matrix)
    row_sums = np.array(sq.sum(axis=1))[:, 0]
    row_sums = np.sqrt(row_sums)
    row_indices, col_indices = matrix.nonzero()
    matrix.data /= row_sums[row_indices]


def norm_sp_row_l1(matrix):
    """ L1 normalize rows of a dense matrix.
    >>> m = np.matrix([[1, 2], [3, 3]], dtype=float)
    >>> m = csr_matrix(m)
    >>> norm_sp_row_l1(m)
    >>> m.todense()
    matrix([[ 0.33333333,  0.66666667],
            [ 0.5       ,  0.5       ]])
    """
    row_sums = np.array(matrix.sum(axis=1))[:, 0]
    row_indices, col_indices = matrix.nonzero()
    matrix.data /= row_sums[row_indices]


class InvertedIndex:
    """ A simple inverted index as explained on the lecture. """

    def __init__(self):
        """ Creates an empty inverted index and additional dicts. """

        self.inverted_lists = dict()
        self.record_lengths = dict()
        self.terms = []
        self.A = None       # Sparse term-document matrix

    def read_from_file(self, file_name):
        """
        Constructs the inverted index from the given file. The format is: one
        record per line.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file('example.txt')
        >>> ii.terms
        ['internet', 'web', 'surfing', 'beach']
        >>> sorted(ii.inverted_lists.items())
        [('beach', {4: 1, 5: 1, 6: 1}), ('internet', {1: 1, 2: 1, 4: 1}), \
('surfing', {1: 1, 2: 1, 3: 1, 4: 2, 5: 1}), ('web', {1: 1, 3: 1, 4: 1})]
        """

        with open(file_name, 'r', encoding='utf-8') as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                words = re.split('\W+', line)
                self.record_lengths[doc_id] = len(words)
                for term in words:
                    term = term.lower()
                    if any(term):
                        # If a word is seen for the first time, create an empty
                        # inverted list for it
                        if term not in self.inverted_lists:
                            self.terms.append(term)
                            self.inverted_lists[term] = dict()

                        if doc_id in self.inverted_lists[term].keys():
                            self.inverted_lists[term][doc_id] += 1
                        else:
                            self.inverted_lists[term][doc_id] = 1

    def bm25_score(self, tf, df, N, AVDL, DL, bm25k=0.75, bm25b=0.0):
        return tf * (bm25k + 1) / (bm25k * (1 - bm25b + bm25b * DL / AVDL) +
                                   tf) * log((N / df), 2)

    def build_td_matrix(self, m=10000):
        """
        Computes the sparse term-document matrix using the (already built)
        inverted index.
        """
        logger.info('Computing term-document matrix A...')

        N = len(self.record_lengths)
        AVDL = sum(self.record_lengths.values()) / float(N)
        terms = sorted(self.terms,
                       key=lambda t: len(self.inverted_lists[t]),
                       reverse=True)[:m]

        nz_vals, row_inds, col_inds = [], [], []
        for i, term in enumerate(terms):
            for doc_id, tf in self.inverted_lists[term].items():
                df = len(self.inverted_lists[term])
                DL = self.record_lengths[doc_id]
                score = self.bm25_score(tf, df, N, AVDL, DL)
                self.inverted_lists[term][doc_id] = score
                nz_vals.append(score)
                row_inds.append(i)
                col_inds.append(doc_id - 1)
        self.A = csr_matrix((nz_vals, (row_inds, col_inds)), dtype=float)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python3 inverted_index.py <records_file>')
        sys.exit()

    ii = InvertedIndex()
    file_name = sys.argv[1]
    logger.info('Loading "%s"...' % file_name)
    ii.read_from_file(file_name)
    ii.build_td_matrix()
