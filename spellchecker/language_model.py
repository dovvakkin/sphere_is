# -*- coding: utf-8 -*-
import sys
import numpy as np
import json
from error_model import split

class LanguageModel:
    def __init__(self):
        self.un_prop = {}  # {word : prop}
        self.un_count = 0.0
        self.bin_prop = {}  # {first_word : {second_word : prop}}
        self.bin_count = 0.0

        self.default_un_prop = 0
        self.default_bin_prop = 0

        self.all_words = set()

    def load_json(self, json_path):
        un_p, un_c, bin_p, bin_c, words = json.loads(open(json_path, "r").read())
        self.un_prop, self.un_count, self.bin_prop, self.bin_count, self.all_words = un_p, un_c, bin_p, bin_c, words

    def store_json(self, json_path):
        file = open(json_path, "w")
        file.write(json.dumps((self.un_prop, self.un_count, self.bin_prop, self.bin_count, self.all_words)))
        file.close()

    def create_model(self, file_name):
        with open(file_name) as file:
            for line in file:
                tab_ind = line.find('\t')
                if tab_ind != -1:
                    line = line[tab_ind + 1:]
                words = split(line)

                ###
                # if 'крк' in words:
                #     print (line)
                ###

                self.all_words.update(set(words))

                len_words = len(words)
                for i in range(len_words):
                    self.un_count += 1
                    if words[i] in self.un_prop:
                        self.un_prop[words[i]] += 1
                    else:
                        self.un_prop[words[i]] = 1

                    if i < len_words - 1:
                        self.bin_count += 1

                        if words[i] in self.bin_prop:
                            if words[i + 1] in self.bin_prop[words[i]]:
                                self.bin_prop[words[i]][words[i + 1]] += 1
                            else:
                                self.bin_prop[words[i]][words[i + 1]] = 1
                        else:
                            self.bin_prop[words[i]] = {words[i + 1]: 1}
            for ind in self.un_prop:
                self.un_prop[ind] = self.un_prop[ind] / self.un_count
            for ind in self.bin_prop:
                for i_ind in self.bin_prop[ind]:
                    self.bin_prop[ind][i_ind] = self.bin_prop[ind][i_ind] / self.bin_count

            self.default_un_prop = 1 / self.un_count
            self.default_bin_prop = 1 / self.bin_count

    def get_un_prop(self, word):
        word = word.encode("utf8")
        if word in self.un_prop:
            return self.un_prop[word]
        else:
            return self.default_un_prop

    def get_bin_prop(self, first, second):
        if first in self.bin_prop:
            if second in self.bin_prop[first]:
                return self.bin_prop[first][second]
            else:
                return self.default_bin_prop
        else:
            return self.default_bin_prop

    # print probabilities for all words
    def print_all_un(self):
        for ind in self.un_prop:
            print ("{}:\t{}".format(ind, self.un_prop[ind]))

    # print probabilities for all words pairs
    def print_all_bin(self):
        for ind in self.bin_prop:
            for i_ind in self.bin_prop[ind]:
                print ("({}, {}):\t{}".format(ind, i_ind, self.bin_prop[ind][i_ind]))

    def get_P_for_query(self, query):
        query = query.lower()
        words = query.split(" ")
        len_words = len(words)
        probs = np.zeros(len_words + (len_words - 1))
        probs_ind = 0
        for i in range(len_words):
            probs[probs_ind] = self.get_un_prop(words[i])
            probs_ind += 1
            if i < len_words - 1:
                probs[probs_ind] = self.get_bin_prop(words[i], words[i + 1])
                probs_ind += 1
        return np.prod(probs)

    def get_most_relevant_after_word(self, word):
        if word not in self.bin_prop:
            return []
        l = list(self.bin_prop[word].items())
        l.sort(key=lambda x: x[1], reverse=True)
        return [item[0].decode() for item in l]

    def get_all_words(self):
        return self.all_words

if __name__ == "__main__":
    lm = LanguageModel()
    lm.create_model("queries_all.txt")
    lm.store_json("language_model.json")
