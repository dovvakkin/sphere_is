# -*- coding: utf-8 -*-
import sys
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')


class BORtree:
    class TreeItself:
        def __init__(self):
            self.lit = "~"  # literal of current node
            self.is_word_end = False  # is there words ends in this node
            self.children = {}

    def __init__(self):
        self.root = self.TreeItself()

    def fill_BORtree(self, set_of_words):
        def add_word_to_bor(literals, bor):
            lt = literals.pop(0)
            if lt not in bor.children:
                bor.children[lt] = self.TreeItself()

            bor.children[lt].is_word_end = not literals or bor.children[lt].is_word_end
            bor.children[lt].lit = lt

            if literals:
                add_word_to_bor(literals, bor.children[lt])

        for word in set_of_words:
            literals = list(word)
            add_word_to_bor(literals, self.root)

    # def find_closest_words_in_bor(word, bor, N_closest, alpha = 0.001):
    #     words  = {}  # "global" variable
    #     def go_down_the_bor(word_to_append, bor, error):
    #         pass
    #
    #     threshold = len(word) * alpha
    #     i = 0
    #     cur = bor
    #     while i < len(word):


lm = LanguageModel()
lm.create_model("test.txt")
for word in lm.get_most_relevant_after_word("ая≥"):
    print word
