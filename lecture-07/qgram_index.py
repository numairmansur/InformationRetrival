"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Evgeny Anatskiy <evgeny.anatskiy@jupiter.uni-freiburg.de>
Numair Mansur <numair.mansur@gmail.com>
"""

import re


class QgramIndex:
    """ A simple q-gram index as explained on the lecture. """

    def __init__(self, q):
        """ Create an empty q-gram index. """

        self.inverted_lists = dict()
        self.records = dict()
        self.q = q

    def read_from_file(self, file_name):
        """
        Construct index from the given file. The format is one record per line.

        >>> qi = QgramIndex(3)
        >>> qi.read_from_file('example.txt')
        >>> sorted(qi.inverted_lists.items())
        [('$$l', {3: 1}), ('$$m', {2: 1}), ('$$z', {1: 1}), ('$lo', {3: 1}), \
('$mu', {2: 1}), ('$zu', {1: 1}), ('che', {2: 1}), ('don', {3: 1}), \
('hen', {2: 1}), ('ich', {1: 1}), ('lon', {3: 1}), ('mun', {2: 1}), \
('nch', {2: 1}), ('ndo', {3: 1}), ('ond', {3: 1}), ('ric', {1: 1}), \
('unc', {2: 1}), ('uri', {1: 1}), ('zur', {1: 1})]

        """

        with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
            record_id = 0
            for line in file:
                record_id += 1

                splitted = line.replace('\n', '').split('\t')
                city = splitted[0]
                city_normalized = re.sub('\W+', '', city).lower()
                country_code = splitted[1] if len(splitted) > 1 else ''
                population = splitted[3] if len(splitted) > 3 else ''

                self.records[record_id] = {
                    'city': city,
                    'normlzd': city_normalized,
                    'country_code': country_code,
                    'population': population
                }

                for qgram in self.qgrams(city_normalized):
                    if len(qgram) > 0:
                        # If a q-gram is seen for the first time, create an
                        # empty inverted list for it.
                        if qgram not in self.inverted_lists:
                            self.inverted_lists[qgram] = dict()

                        if record_id in self.inverted_lists[qgram].keys():
                            self.inverted_lists[qgram][record_id] += 1
                        else:
                            self.inverted_lists[qgram][record_id] = 1

    def qgrams(self, record):
        """ All q-grams of the given record.

        >>> qi = QgramIndex(3)
        >>> qi.qgrams('bana')
        ['$$b', '$ba', 'ban', 'ana']
        """

        record = "$" * (self.q - 1) + record
        return [record[i:i + self.q]
                for i in range(0, len(record) - self.q + 1)]

    @staticmethod
    def merge(lists):
        """ Merge the q-gram index lists and return a list of tuples (record_id,
        count).

        >>> QgramIndex.merge([[[1, 1], [2, 1], [3, 1]], [[2, 1], [3, 1], \
[4, 1]], [[3, 1], [4, 1], [5, 1]]])
        [[1, 1], [2, 2], [3, 3], [4, 2], [5, 1]]
        """

        merged_list = list()
        for l2 in lists:
            l1 = merged_list
            merged_list = list()
            i, j = 0, 0
            while i < len(l1) and j < len(l2):
                if l1[i][0] < l2[j][0]:
                    merged_list.append(l1[i])
                    i += 1
                elif l1[i][0] == l2[j][0]:
                    merged_list.append([l1[i][0], l1[i][1] + l2[j][1]])
                    i += 1
                    j += 1
                else:
                    merged_list.append(l2[j])
                    j += 1
            if i < len(l1):
                merged_list.extend(l1[i:])
            if j < len(l2):
                merged_list.extend(l2[j:])

        return merged_list

    @staticmethod
    def compute_ped(p, s):
        """ Compute the prefix edit distance PED(p, s).

        >>> QgramIndex.compute_ped('shwartz', 'schwarzenegger')
        2
        """

        n, m = len(p), len(s)
        bound = m + 1

        current_row = list(range(bound))
        for i in list(range(1, n + 1)):
            previous_row = current_row
            current_row = [i] + [0] * (bound - 1)
            for j in list(range(1, bound)):
                insert = previous_row[j] + 1
                delete = current_row[j - 1] + 1
                replace = previous_row[j - 1]
                if s[j - 1] != p[i - 1]:
                    replace += 1
                current_row[j] = min(insert, delete, replace)

        return min(current_row)

    def find_matches(self, prefix, delta, k=5):
        """ Find all matches for the given prefix with PED at most delta. Return
        the top-k matches.

        >>> qi = QgramIndex(3)
        >>> qi.read_from_file('example.txt')
        >>> qi.find_matches('zur', 0)
        [('Zurich', 'CH', '12321', 0)]
        """

        result = list()

        all_qgrams = self.inverted_lists.keys()
        lists = [sorted(list(
            zip(self.inverted_lists[qgram].keys(),
                self.inverted_lists[qgram].values())
        )) for qgram in self.qgrams(prefix) if qgram in all_qgrams]

        for lst in self.merge(lists):
            if lst[1] >= len(prefix) - self.q * delta:
                ped = self.compute_ped(prefix, self.records[lst[0]]['normlzd'])
                if ped <= delta:
                    result.append((self.records[lst[0]]['city'],
                                   self.records[lst[0]]['country_code'],
                                   self.records[lst[0]]['population'],
                                   ped))

        return sorted(result, key=lambda x: x[3], reverse=False)[:k]
