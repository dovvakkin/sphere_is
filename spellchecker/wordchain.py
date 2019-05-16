import copy
from timeit_decorator import timeit

class WordChain:
    def __init__(self, lm, bor):
        self.bor = bor
        self.lm = lm

    def make_words_variants(self, query):
        split = query.split(" ")
        words_vars = []
        for word in split:
            fix = self.bor.indistrict_search(word)
            words_vars.append(fix)
        return words_vars

    @timeit
    def make_chains(self, words_vars):
        chains = {}

        def go_down(res, ind, length):
            for i in range(len(words_vars[ind])):
                res_ad = res + u' ' + words_vars[ind][i]
                if ind < length - 1:
                    go_down(copy.deepcopy(res_ad), ind + 1, length)
                else:
                    # result[res_ad] = self.lm.get_P_for_query(res_ad)
                    result[res_ad] = 1

        result = dict()
        go_down(copy.deepcopy(u""), 0, len(words_vars))
        return result

    def fix_query(self, query):
        # TODO switch layout
        word_vars = self.make_words_variants(query)
        result = self.make_chains(word_vars)
        for query in sorted(result, key=result.get, reverse=True):
            print query