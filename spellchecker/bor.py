# -*- coding: utf-8 -*-
import json
import pickle
import sys
import numpy as np
import copy
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print ('\n%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

class TreeItself:
    def __init__(self):
        self.lit = "~"  # literal of current node
        self.is_word_end = False  # is there words ends in this node
        self.children = {}

class BORtree:
    def __init__(self, bin_stats, default_prob):
        self.root = TreeItself()
        self.root.lit = "^"
        self.bin_stats = bin_stats  # {2gram : {f_f : {f_s : prob}}}
        self.default_prob = default_prob

    def store_tree(self):
        with open("tree_root.pickle", "wb") as f:
            pickle.dump(self.root, f)
        with open("tree.json", "w") as f:
            f.write(json.dumps((self.bin_stats, self.default_prob)))

    def load_tree(self):
        with open("tree_root.pickle", "rb") as f:
            self.root = pickle.load(f)
        with open("tree.json", "r") as f:
            self.bin_stats, self.default_prob = json.loads(f.read())

    def fill_BORtree(self, set_of_words):
        def add_word_to_bor(literals, bor):
            lt = literals.pop(0)
            if lt not in bor.children:
                bor.children[lt] = TreeItself()

            bor.children[lt].is_word_end = not literals or bor.children[lt].is_word_end
            bor.children[lt].lit = lt

            if literals:
                add_word_to_bor(literals, bor.children[lt])

        for word in set_of_words:
            literals = list(word)
            if literals:
                add_word_to_bor(literals, self.root)

    # sorted(a.items(), key=lambda kv: (kv[1], kv[0]))
    @timeit
    def indistrinct_search(self, word, threshold=10000000, N_to_go=3):
        def go_down(node, word_as_list, res, err):
            if word_as_list:
                c = word_as_list.pop(0)
                if err < threshold:
                    for child in node.children:
                        err_delta = 0
                        if child != c:
                            bigram = node.lit + c
                            if bigram in self.bin_stats:
                                if node.lit in self.bin_stats[bigram]:
                                    if child in self.bin_stats[bigram][node.lit]:
                                        err_delta = 1 / self.bin_stats[bigram][node.lit][child]
                                    else:
                                        err_delta = 100 / self.default_prob
                                else:
                                    err_delta = 100 / self.default_prob
                        else:
                            err_delta = 1 / self.default_prob
                        go_down(node.children[child], copy.deepcopy(word_as_list), res + child, err + err_delta)
            if not word_as_list and node.is_word_end:
                result[res] = err

        result = {}
        go_down(self.root, list(word), "",0)
        print(sorted(result.items(), key=lambda kv: (kv[1], kv[0]))[0:20])
