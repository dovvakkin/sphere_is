# -*- coding: utf-8 -*-
import sys
import json
import numpy as np


EMPTY_LEX = "~"
MAX_WORD_LEN = 15
SPECIAL_LEX = {"_", "-", "—", "'"}


def split(string):
    word_list = []
    string = string.lower()
    word = str()
    for char in string:
        if ("A" <= char <= "Z") or \
                ("a" <= char <= "z") or \
                ("А" <= char <= "Я") or \
                ("а" <= char <= "я") or \
                (char in SPECIAL_LEX):
            word += char
        elif word:
            if len(word) < MAX_WORD_LEN:
                word_list.append(word)
            word = str()
    if word:
        word_list.append(word)
    return word_list


class ErrorModel:
    def __init__(self):
        self.statistics = dict()  # {"origin" : {"fix" : number}}
        self._statistics_size = 0

        self.bin_stats = dict()
        self.bin_size = 0

    def bi_symbols(string):
        if not string:
            return ["^_"]
        new_string = ["^" + string[0]]
        for i in range(len(string) - 1):
            new_string += [string[i:i + 2]]
        new_string += [string[-1:] + "_"]
        return new_string

    def load_json(self, json_path):
        (size, stat) = json.loads(open(json_path, "r").read())
        self.bin_size, self.bin_stats = size, stat

    def store_json(self, json_path):
        file = open(json_path, "w")
        file.write(json.dumps((self.bin_size, self.bin_stats)))
        file.close()

    def fit(self, a, b):
        levenshtein_matrix = self._get_levenshtein_matrix(a, b)
        self._fill_statistics(a, b, levenshtein_matrix)

    def prichesat_statistiku(self):
        for orig in self.statistics.keys():
            for fix in self.statistics[orig].keys():
                self.statistics[orig][fix] /= self._statistics_size

    def get_weighted_distance(self, a, b):
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n

        current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
        # matrix = np.array([current_row])
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = (previous_row[j] + 1) / self._get_statistics(EMPTY_LEX, b[i - 1]), \
                                      (current_row[j - 1] + 1) / self._get_statistics(a[j - 1], EMPTY_LEX), \
                                      (previous_row[j - 1] + int(a[j - 1] != b[i - 1])) / self._get_statistics(a[j - 1],
                                                                                                               b[i - 1])
                current_row[j] = min(add, delete, change)
            # matrix = np.vstack((matrix, [current_row]))
        return current_row[n]

    def _get_statistics(self, orig, fit):
        if orig in self.statistics and fit in self.statistics[orig]:
            return self.statistics[orig][fit]
        return 1 / 1000  # TODO flexible (newer sow this case)

    def _add_statistics(self, orig, fix):
        self.statistics.setdefault(orig, dict())
        self.statistics[orig].setdefault(fix, 0)
        self.statistics[orig][fix] += 1
        self._statistics_size += 1

    def _fill_statistics(self, a, b, matrix):
        n, m = len(a), len(b)
        MAX_DISTANCE = (n + 1) * (m + 1)

        position = [n, m, matrix[m, n]]  # [x, y, distance]
        while position[2] != 0:  # пока distance не станет 0
            x, y = position[0], position[1]
            iter = True

            # только один из возможных путей изменения. можно сделать лучше
            possible_actions = [matrix[y - 1][x - 1] if (x > 0) and (y > 0) else MAX_DISTANCE,  # change
                                matrix[y - 1][x] if y > 0 else MAX_DISTANCE,  # add
                                matrix[y][x - 1] if x > 0 else MAX_DISTANCE]  # delete
            action = np.argmin(possible_actions)

            if action == 0:  # change
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1
                    self._add_statistics(a[x - 1], b[y - 1])
                    # print(a[x - 1] + " -> " + b[y - 1])
                position[0] -= 1
                position[1] -= 1
            elif action == 1:  # add
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1
                    # self._add_statistics(EMPTY_LEX, b[y - 1])
                    if not iter:
                        self._add_statistics(EMPTY_LEX + a[x - 1][1], b[y - 1])  # for bigram
                    else:
                        self._add_statistics(a[x - 1][1] + EMPTY_LEX, b[y - 1])  # for bigram
                    # print("~ -> " + b[y - 1])
                position[1] -= 1
            else:  # delete
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1
                    # self._add_statistics(a[x - 1], EMPTY_LEX)
                    if not iter:
                        self._add_statistics(a[x - 1], EMPTY_LEX + b[y - 1][1])  # for bigram
                    else:
                        self._add_statistics(a[x - 1], b[y - 1][1] + EMPTY_LEX)  # for bigram
                    # print(a[x - 1] + " -> ~")
                position[0] -= 1
            iter = not iter

    @staticmethod
    def _get_levenshtein_matrix(a, b):
        n, m = len(a), len(b)
        inverse = False
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n
            inverse = True

        current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
        matrix = np.array([current_row])
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, \
                                      current_row[j - 1] + 1, \
                                      previous_row[j - 1] + int(a[j - 1] != b[i - 1])
                current_row[j] = min(add, delete, change)
            matrix = np.vstack((matrix, [current_row]))
        return matrix if not inverse else matrix.T

    def make_bin_stats(self, file_name):
        self.statistics = dict()
        self._statistics_size = 0
        with open(file_name) as f:
            for line in f:
                delimiter = line.find("\t")
                if delimiter == -1:
                    continue
                wrong = split(line[:delimiter].lower())
                right = split(line[delimiter + 1:-1].lower())
                if len(wrong) != len(right):  # произошел join или split
                    continue
                for i in range(len(wrong)):  # для каждого слова
                    self.fit(bi_symbols(wrong[i]), bi_symbols(right[i]))

            self.prichesat_statistiku()
            self.bin_stats = self.statistics
            self.bin_size = self._statistics_size

    def print_bin(self):
        for i in self.bin_stats:
            for ii in self.bin_stats[i]:
                if ii[0] == i[0]:
                    print ("{} -> {} : {}".format(i, ii, self.bin_stats[i][ii]))


# represent word as bigrams
def bi_symbols(string):
    if not string:
        return ["^_"]
    new_string = ["^" + string[0]]
    for i in range(len(string) - 1):
        new_string += [string[i:i + 2]]
    new_string += [string[-1:] + "_"]
    return new_string


if __name__ == "__main__":
    error = ErrorModel()
    # error.make_bin_stats("queries_all.txt")
    # error.store_json("bin_stats.json")

    error.load_json("bin_stats.json")
    error.print_bin()