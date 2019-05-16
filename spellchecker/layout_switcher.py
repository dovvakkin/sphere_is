#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import sys
reload(sys)
sys.setdefaultencoding('UTF8')

from string import maketrans
from timeit_decorator import timeit

class LayoutSwitcher:
    def __init__(self):
        self.ru_trigrams = set()
        self.en_trigrams = set()
        en_qwerty = u"qwertyuiop[]asdfghjkl;'zxcvbnm,."
        ru_qwerty = u"йцукенгшщзхъфывапролджэячсмитьбю"
        self.ru_to_en = {ord(c): ord(t) for c, t in zip(ru_qwerty, en_qwerty)}
        self.en_to_ru = {ord(c): ord(t) for c, t in zip(en_qwerty, ru_qwerty)}

    def store_pickle(self):
        with open('pretrained_models/ls_ru.pickle', 'wb') as f:
            pickle.dump(self.ru_trigrams, f)
        with open('pretrained_models/ls_en.pickle', 'wb') as f:
            pickle.dump(self.en_trigrams, f)

    def load_pickle(self):
        with open('pretrained_models/ls_ru.pickle', 'rb') as f:
            self.ru_trigrams = pickle.load(f)
        with open('pretrained_models/ls_en.pickle', 'rb') as f:
            self.en_trigrams = pickle.load(f)

    def word_to_trigrams(self, word):
        trigrams = set()
        if type(word) != unicode:
            word = unicode(word, "utf-8")
        for i in range(len(word)):
            if i < len(word) - 2:
                trigram = word[i] + word[i + 1] + word[i + 2]
                trigrams.add(trigram)
        return trigrams

    def create_ru_trigrams(self, file_name):
        with open(file_name) as f:
            # TODO жопа
            trigrams = dict()
            for line in f:
                all_words = line.split(" ")
                for word in all_words:
                    for trigram in self.word_to_trigrams(word):
                        if trigram in trigrams:
                            trigrams[trigram] += 1
                        else:
                            trigrams[trigram] = 1
            i=0
            for tr in sorted(trigrams, key=trigrams.get, reverse=True):
                if i < 100:
                    self.ru_trigrams.add(tr)
                    i+=1
                else:
                    break

    def create_en_trigrams(self, file_name):
        with open(file_name) as f:
            # TODO жопа
            trigrams = dict()
            for line in f:
                all_words = line.split(" ")
                for word in all_words:
                    for trigram in self.word_to_trigrams(word):
                        if trigram in trigrams:
                            trigrams[trigram] += 1
                        else:
                            trigrams[trigram] = 1
            i = 0
            for tr in sorted(trigrams, key=trigrams.get, reverse=True):
                if i < 100:
                    self.en_trigrams.add(tr)
                    i += 1
                else:
                    break

    # @timeit
    def switch_layout(self, string):
        if type(string) != unicode:
            string = unicode(string, "utf-8")
        if 'a' <= string[0] <= 'z':
            en = string
            ru = string.translate(self.en_to_ru)
        else:
            ru = string
            en = string.translate(self.ru_to_en)

        ru_split = ru.split(" ")
        en_split = en.split(" ")

        ru_trigrams = set()
        en_trigrams = set()

        for word in ru_split:
            ru_trigrams |= self.word_to_trigrams(word)
        for word in en_split:
            en_trigrams |= self.word_to_trigrams(word)

        if len(ru_trigrams & self.ru_trigrams) > len(en_trigrams & self.en_trigrams):
            return ru
        else:
            return en
