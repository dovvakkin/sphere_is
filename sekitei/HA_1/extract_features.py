# coding: utf-8

import sys

# you may add imports if needed (and if they are installed)
from urllib import unquote_plus
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


def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
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

    LINKS = 1000
    n = 0
    f = open(INPUT_FILE_1, "r")
    # for url in f:
    #     u = url.replace('\n', '')
    #     get_features_from_url(u)
    #     i += 1
    #     n += 1
    #     if i == LINKS:
    #         break
    # f.close()
    line_counter = 0
    for url in f:
        line_counter += 1
    f.seek(0)
    lines = np.sort(np.random.choice(line_counter, LINKS, replace=False))
    line = 0
    for num, url in enumerate(f):
        if num == lines[line]:
            u = url.replace('\n', '')
            get_features_from_url(u)
            n += 1
            line += 1
            if line == LINKS:
                break
    f.close()

    line_counter = 0
    f = open(INPUT_FILE_2, "r")
    for url in f:
        line_counter += 1
    f.seek(0)
    lines = np.sort(np.random.choice(line_counter, LINKS, replace=False))
    line = 0
    for num, url in enumerate(f):
        if num == lines[line]:
            u = url.replace('\n', '')
            get_features_from_url(u)
            n += 1
            line += 1
            if line == LINKS:
                break
    f.close()

    tr = n * 0.051
    # tr = 0
    f.close()
    l = create_features_list()
    l = cut_list_by_treshhold(l, tr)
    write_feature_list_to_file(l, OUTPUT_FILE)
