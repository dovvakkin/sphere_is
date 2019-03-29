# coding: utf-8


import sys
import os
import time
# from sklearn.cluster import <any cluster algorithm>
from sklearn.cluster import MeanShift
from urlparse import urlsplit, parse_qs, unquote
import re
import random
import numpy as np

param_name = {}

param_key_value = {}

#######################################################

segments = {}

segment_name = {}

segment_num = {}

segment_substr_num = {}

# dict in dict
segment_ext = {}

# dict in dict
segment_ext_substr_num = {}

# dict in dict
segment_len = {}


#######################################################


def randomLine(file_object):
    "Retrieve a random line from a file, reading through the file once"
    lineNum = 0
    selected_line = ''

    while 1:
        aLine = file_object.readline()
        if not aLine: break
        lineNum = lineNum + 1
        # How likely is it that this is the last line of the file?
        if random.uniform(0, lineNum) < 1:
            selected_line = aLine
    file_object.close()
    return selected_line


def fill_param_name(name):
    if name in param_name:
        param_name[name] += 1
    else:
        param_name[name] = 1


def fill_param_key_value(key_value):
    if key_value in param_key_value:
        param_key_value[key_value] += 1
    else:
        param_key_value[key_value] = 1


#######################################################


def fill_segments(len):
    if len in segments:
        segments[len] += 1
    else:
        segments[len] = 1


def fill_segment_name(index, string):
    if string.find("\n") != -1:
        string = string[:-1]
    if index in segment_name:
        if string in segment_name[index]:
            segment_name[index][string] += 1
        else:
            segment_name[index][string] = 1
    else:
        segment_name[index] = {string: 1}


def fill_segment_num(index, string):
    if not string.isdigit():
        return

    if index in segment_num:
        segment_num[index] += 1
    else:
        segment_num[index] = 1


def fill_segment_substr_num(index, string):
    try:
        string = unquote(string).decode("cp1251")
    except Exception:
        try:
            string = unquote(string).decode("utf8")
        except Exception:
            pass
    if string.isdigit():
        return
    if len(re.findall(r'\d+', string)) != 1:
        return
    if index in segment_substr_num:
        segment_substr_num[index] += 1
    else:
        segment_substr_num[index] = 1


def fill_segment_ext(index, seg_name):
    dot = seg_name.rfind('.')
    if dot == -1:
        return

    if seg_name.find("\n") != -1:
        ext = seg_name[dot + 1:-1]
    else:
        ext = seg_name[dot + 1:]

    ext = ext.lower()
    if index in segment_ext:
        if ext in segment_ext[index]:
            segment_ext[index][ext] += 1
        else:
            segment_ext[index][ext] = 1
    else:
        segment_ext[index] = {ext: 1}


def fill_segment_ext_substr_num(index, seg_name):
    dot = seg_name.rfind('.')
    if dot == -1:
        return
    ext = seg_name[dot + 1:]
    if len(re.findall(r'\d+', ext)) != 1:
        return
    ext = ext.lower()

    if index in segment_ext_substr_num:
        if ext in segment_ext_substr_num[index]:
            segment_ext_substr_num[index][ext] += 1
        else:
            segment_ext_substr_num[index][ext] = 1
    else:
        segment_ext_substr_num[index] = {ext: 1}


def fill_segment_len(index, seg_name):
    length = len(seg_name)
    if index in segment_len:
        if length in segment_len[index]:
            segment_len[index][length] += 1
        else:
            segment_len[index][length] = 1
    else:
        segment_len[index] = {length: 1}


#######################################################


def get_features_from_url(url):
    split = urlsplit(url)
    path = filter(None, split.path.split('/'))

    fill_segments(len(path))
    for idx, seg_name in enumerate(path):
        fill_segment_name(idx, seg_name)
        fill_segment_num(idx, seg_name)
        fill_segment_substr_num(idx, seg_name)
        fill_segment_ext(idx, seg_name)
        fill_segment_ext_substr_num(idx, seg_name)
        fill_segment_len(idx, seg_name)

    q = parse_qs(split.query)
    for key in q:
        fill_param_name(key)
        for val in q[key]:
            fill_param_key_value(key + "=" + val)


def create_features_list():
    l = []
    for seg in segments:
        l.append(("segments:{}\t".format(seg), segments[seg]))
    for name in param_name:
        l.append(("param_name:{}\t".format(name), param_name[name]))
    for key_val in param_key_value:
        l.append(("param:{}\t".format(key_val), param_key_value[key_val]))
    for index in segment_name:
        for string in segment_name[index]:
            l.append(("segment_name_{}:{}\t".format(index, string), segment_name[index][string]))
    for index in segment_num:
        l.append(("segment_[0-9]_{}:1\t".format(index), segment_num[index]))
    for index in segment_substr_num:
        l.append(("segment_substr[0-9]_{}:1\t".format(index), segment_substr_num[index]))
    for index in segment_ext:
        for ext in segment_ext[index]:
            l.append(("segment_ext_{}:{}\t".format(index, ext), segment_ext[index][ext]))
    for index in segment_ext_substr_num:
        for ext in segment_ext_substr_num[index]:
            l.append(("segment_ext_substr[0-9]_{}:{}\t".format(index, ext), segment_ext_substr_num[index][ext]))
    for index in segment_len:
        for length in segment_len[index]:
            l.append(("segment_len_{}:{}\t".format(index, length), segment_len[index][length]))
    return l


def write_feature_list_to_file(l, file):
    f = open(file, "w")
    for p in l:
        f.write(p[0] + str(p[1]) + "\n")


def cut_list_by_treshhold(l, treshhold):
    l.sort(key=lambda x: x[1], reverse=True)
    # filter(lambda x: x[1] <= treshhold, l)
    return [x for x in l if x[1] > treshhold]


# def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
def extract_features(INPUT_FILE_1, INPUT_FILE_2):
    global param_name
    global param_key_value
    global segments
    global segment_name
    global segment_num
    global segment_substr_num
    global segment_ext
    global segment_ext_substr_num
    global segment_len

    param_name = {}
    param_key_value = {}
    segments = {}
    segment_name = {}
    segment_num = {}
    segment_substr_num = {}
    segment_ext = {}
    segment_ext_substr_num = {}
    segment_len = {}

    # LINKS = 1000
    # n = 0
    # f = open(INPUT_FILE_1, "r")
    # line_counter = 0
    # for url in f:
    #     line_counter += 1
    # f.seek(0)
    # lines = np.sort(np.random.choice(line_counter, LINKS, replace=False))
    # line = 0
    # for num, url in enumerate(f):
    #     if num == lines[line]:
    #         u = url.replace('\n', '')
    #         get_features_from_url(u)
    #         n += 1
    #         line += 1
    #         if line == LINKS:
    #             break
    # f.close()
    #
    # line_counter = 0
    # f = open(INPUT_FILE_2, "r")
    # for url in f:
    #     line_counter += 1
    # f.seek(0)
    # lines = np.sort(np.random.choice(line_counter, LINKS, replace=False))
    # line = 0
    # for num, url in enumerate(f):
    #     if num == lines[line]:
    #         u = url.replace('\n', '')
    #         get_features_from_url(u)
    #         n += 1
    #         line += 1
    #         if line == LINKS:
    #             break
    # f.close()

    n = 0
    for url in INPUT_FILE_1:
        get_features_from_url(url)
        n += 1

    for url in INPUT_FILE_2:
        get_features_from_url(url)
        n += 1

    tr = n * 0.051
    # tr = 0
    l = create_features_list()
    l = cut_list_by_treshhold(l, tr)
    # write_feature_list_to_file(l, OUTPUT_FILE)
    return l


#######################################################


def create_segments_checker(length):
    def check_segments(path, query):
        return len(path) == length

    return check_segments


def create_segment_name_checker(index, name):
    def check_segment_name(path, query):
        if index >= len(path):
            return False
        if path[index] != name:
            return False
        return True

    return check_segment_name


def create_segment_num_checker(index):
    def check_segment_num(path, query):
        if index >= len(path):
            return False
        return path[index].isdigit()

    return check_segment_num


def create_segment_substr_num_checker(index):
    def check_segment_substr_num(path, query):
        if index >= len(path):
            return False
        string = path[index]
        try:
            string = unquote(string).decode("cp1251")
        except Exception:
            try:
                string = unquote(string).decode("utf8")
            except Exception:
                pass
        if string.isdigit():
            return False
        if len(re.findall(r'\d+', string)) != 1:
            return False
        return True

    return check_segment_substr_num


def create_segment_ext_checker(index, ext):
    def check_segment_ext(path, query):
        if index >= len(path):
            return False
        seg_name = path[index]
        dot = seg_name.rfind('.')
        if dot == -1:
            return False
        seg_ext = seg_name[dot + 1:]
        seg_ext = seg_ext.lower()
        return seg_ext == ext

    return check_segment_ext


def create_segment_ext_substr_num_checker(index, ext):
    def check_segment_ext_substr_num(path, query):
        if index >= len(path):
            return False
        seg_name = path[index]
        dot = seg_name.rfind('.')
        if dot == -1:
            return False
        seg_ext = seg_name[dot + 1:]
        seg_ext = seg_ext.lower()
        return seg_ext == ext


def create_segment_len_checker(index, length):
    def check_segment_len(path, query):
        if index >= len(path):
            return False
        return len(path[index]) == length

    return check_segment_len


def create_param_name_checker(name):
    def check_param_name(path, query):
        return name in query

    return check_param_name


def create_param_checker(name, value):
    def check_param(path, query):
        if name not in query:
            return False
        return query[name][0] == value

    return check_param


class Sekitei:
    def __init__(self):
        # list of feature names
        self.feature_list = []
        # number of features
        self.number_of_features = 0
        # list of functions
        self.features_extractors = []
        # clusters
        self.clustering = None
        self.quota = None

    def create_feature_list(self, qlinks, unknown):
        self.feature_list = extract_features(qlinks, unknown)
        self.number_of_features = len(self.feature_list)

    def create_functions_list(self):
        for feature in self.feature_list:
            if feature[0].startswith("segments:"):
                length = int(feature[0][9:])
                self.features_extractors.append(create_segments_checker(length))

            elif feature[0].startswith("segment_name_"):
                index_end = feature[0].rfind(":")
                index = int(feature[0][13:index_end])
                string = feature[0][index_end + 1:-1]
                self.features_extractors.append(create_segment_name_checker(index, string))

            elif feature[0].startswith("segment_[0-9]_"):
                index_end = feature[0].rfind(":")
                index = int(feature[0][14:index_end])
                self.features_extractors.append(create_segment_num_checker(index))

            elif feature[0].startswith("segment_substr[0-9]_"):
                index_end = feature[0].rfind(":")
                index = int(feature[0][20:index_end])
                self.features_extractors.append(create_segment_substr_num_checker(index))

            elif feature[0].startswith("segment_ext_"):
                index_end = feature[0].find(":")
                index = int(feature[0][12:index_end])
                ext = feature[0][index_end + 1: -1]
                self.features_extractors.append(create_segment_ext_checker(index, ext))

            elif feature[0].startswith("segment_ext_substr[0-9]_"):
                index_end = feature[0].find(":")
                index = int(feature[0][24:index_end])
                ext = feature[0][index_end + 1: -1]
                self.features_extractors.append(create_segment_ext_substr_num_checker(index, ext))

            elif feature[0].startswith("segment_len_"):
                index_end = feature[0].find(":")
                index = int(feature[0][12:index_end])
                length = int(feature[0][index_end + 1: -1])
                self.features_extractors.append(create_segment_len_checker(index, length))

            elif feature[0].startswith("param_name:"):
                name = feature[0][11:-1]
                self.features_extractors.append(create_param_name_checker(name))

            elif feature[0].startswith("param:"):
                name_end = feature[0].find("=")
                name = feature[0][6: name_end]
                value = feature[0][name_end + 1: -1]
                self.features_extractors.append(create_param_checker(name, value))

    def get_url_coordinates(self, url):
        split = urlsplit(url)
        path = filter(None, split.path.split('/'))
        query = parse_qs(split.query)
        vector = np.zeros(self.number_of_features)
        i = 0
        for checker in self.features_extractors:
            vector[i] = checker(path, query)
            i += 1
        return vector.astype(int)

    def make_clusterization(self, qlinks, unknown, quota):
        def normalize(ar):
            s = np.sum(ar)
            return ar / s

        X = np.empty((1000, self.number_of_features))
        i = 0
        for url in qlinks:
            X[i] = self.get_url_coordinates(url)
            i += 1
        for url in unknown:
            X[i] = self.get_url_coordinates(url)
            i += 1

        self.clustering = MeanShift(bandwidth=1.5).fit(X)
        labels = self.clustering.labels_
        number_of_clusters = self.clustering.cluster_centers_.shape[0]
        self.quota = np.zeros(number_of_clusters)
        i = 0
        for label in labels:
            self.quota[label] += 1
            i += 1
            if i == 500:
                break
        self.quota = (normalize(self.quota) * quota).astype(int)
        # todo

    def fetch_url(self, url):
        coordinates = np.array([self.get_url_coordinates(url)])

        label = self.clustering.predict(coordinates)[0]
        if self.quota[label] > 0:
            self.quota[label] -= 1
            return True
        return False


sekitei = None


def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
    global sekitei
    sekitei = Sekitei()
    sekitei.create_feature_list(QLINK_URLS, UNKNOWN_URLS)
    sekitei.create_functions_list()
    sekitei.make_clusterization(QLINK_URLS, UNKNOWN_URLS, QUOTA)


#
# returns True if need to fetch url
#
def fetch_url(url):
    global sekitei
    return sekitei.fetch_url(url)

# sekitei = Sekitei()
# list = ["https://vk.com/im?peers=437616556"]
# sekitei.create_feature_list(list, list)
# sekitei.create_functions_list()
# sekitei.fetch_url("https://vk.com/im?peers=437616558")
