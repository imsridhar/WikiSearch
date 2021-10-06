#!/usr/bin/python

import sys
import os
import re
import xml.sax
from nltk import tokenize
import time
import threading

from collections import Counter
from nltk.stem.porter import *
from Stemmer import Stemmer

from nltk.corpus import stopwords
from spacy.lang.en.stop_words import STOP_WORDS
from datetime import datetime
import math
stemmer = Stemmer('porter')
stopWords = set(stopwords.words('english'))
InvIndex = {}
totalTokens = 0
tmr = 0
output_dir = ""
c_size = 10000


def index_docs(data, docID):

    global InvIndex
    for f in data:
        Count = Counter()
        for word in data[f]:
            Count[word] += 1
        for word in Count:
            tmr = 5
            if word in InvIndex:
                if f in InvIndex[word]:
                    InvIndex[word][f].append((docID, Count[word]))
                else:
                    InvIndex[word][f] = [(docID, Count[word])]
            else:
                InvIndex[word] = {}
                InvIndex[word][f] = [(docID, Count[word])]
    return


def WriteToFile(file_count):
    filename = os.path.join(output_dir, str(file_count)+'.txt')
    with open(filename, 'w') as f:
        tokens = sorted(InvIndex.keys())
        for token in tokens:
            f.write(token)
            f.write(" ")
            field_keys = sorted(InvIndex[token].keys())

            for field in field_keys:
                f.write(field)
                f.write("-")
                for page, counttt in InvIndex[token][field]:
                    tmr = 1
                    f.write(str(page))
                    f.write(":")
                    f.write(str(counttt)+',')
                f.write(' ')
            f.write("\n")
    InvIndex.clear()


def store_titles(titles, file_count):
    title_file = os.path.join('title', str(file_count)+'.txt')
    with open(title_file, 'w', encoding="utf-8") as f:
        for t in titles:
            f.write(t + '\n')


def merge_files():
    index_fls = os.listdir(output_dir)
    while len(index_fls) > 1:
        merge_2_files(index_fls[0], index_fls[1])
        index_fls.append(index_fls[0])
        index_fls = index_fls[2:]
    final_file = os.path.join(output_dir, 'tmp.txt')
    last_file = os.path.join(output_dir, index_fls[0])
    os.rename(last_file, final_file)
    return final_file


def merge_2_files(file_1, file_2):
    file_1 = os.path.join(output_dir, file_1)
    file_2 = os.path.join(output_dir, file_2)
    new_fl = os.path.join(output_dir, 'tmp.txt')
    file_1_ptr = open(file_1, 'r')
    file_2_ptr = open(file_2, 'r')
    f3 = open(new_fl, 'w+')
    line_1 = file_1_ptr.readline().strip()
    line_2 = file_2_ptr.readline().strip()
    while line_1 and line_2:
        line_1 = line_1.strip()
        line_2 = line_2.strip()
        w2 = line_2.split(' ', 1)[0]
        w1 = line_1.split(' ', 1)[0]
        if(w1 < w2):
            f3.write(line_1 + '\n')
            line_1 = file_1_ptr.readline()
        elif(w2 < w1):
            f3.write(line_2 + '\n')
            line_2 = file_2_ptr.readline()
        else:
            f3.write(merge_2_lines(line_1, line_2) + '\n')
            line_1 = file_1_ptr.readline()
            line_2 = file_2_ptr.readline()
    while line_1:
        line_1 = line_1.strip()
        f3.write(line_1 + '\n')
        line_1 = file_1_ptr.readline()
    while line_2:
        line_2 = line_2.strip()
        f3.write(line_2 + '\n')
        line_2 = file_2_ptr.readline()
    file_1_ptr.close()
    file_2_ptr.close()
    f3.close()
    os.remove(file_1)
    os.remove(file_2)
    os.rename(new_fl, file_1)
    return


def merge_2_lines(line_1, line_2):
    line_1 = line_1.split()
    line_2 = line_2.split()
    word = line_1[0]
    if(len(line_1) > 0):
        line_1 = line_1[1:]
    if(len(line_2) > 0):
        line_2 = line_2[1:]
    l3 = word
    while line_1 and line_2:
        if(line_1[0][0] < line_2[0][0]):
            l3 = l3 + ' ' + line_1[0]
            line_1 = line_1[1:]
        elif(line_2[0][0] < line_1[0][0]):
            l3 = l3 + ' ' + line_2[0]
            line_2 = line_2[1:]
        else:
            l3 = l3 + ' ' + line_1[0] + line_2[0][2:]
            line_1 = line_1[1:]
            line_2 = line_2[1:]
    while line_1:
        l3 = l3 + ' ' + line_1[0]
        line_1 = line_1[1:]
    while line_2:
        l3 = l3 + ' ' + line_2[0]
        line_2 = line_2[1:]
    return l3


field_wts = {'b': 3, 'l': 2, 'i': 6, 't': 10, 'c': 2, 'r': 2}


def calc_tf_idf(line, num_pages):
    line = line.split()
    token = line[0]
    line = line[1:]
    new_ln = token
    for fd in line:
        splited = fd.split('-')
        fld = splited[0]
        lst = splited[1].split(',')
        num_d = len(lst)
        idf = math.log(num_pages/num_d) + 1
        new_ln += ' ' + fld + '-'
        if not lst[-1]:
            lst.pop()
        for doc in lst:
            splitted = doc.split(":")
            cnt = int(splitted[1])
            tf = math.log(cnt) + 1
            tf_idf = tf*idf*field_wts[fld]
            new_ln += splitted[0] + ':' + str(int(tf_idf)) + ','
    return new_ln


def split_files(index_path, temp_file, num_pages,  top_file):
    f_counter = 1
    l_counter = 0
    top = open(top_file, 'w')
    with open(temp_file, 'r') as f:
        l = f.readline().strip()
        while l:
            l = l.strip()
            if l_counter % c_size == 0:
                l_counter = 0
                top.write(l.split()[0] + '\n')
                f2 = os.path.join(index_path, str(f_counter) + '.txt')
                f_counter += 1
                f2w = open(f2, 'w+')
            f2w.write(calc_tf_idf(l, num_pages) + '\n')
            l = f.readline()
            l_counter += 1
            if l_counter % c_size == 0:
                f2w.close()
    os.remove(temp_file)


class DocTweek():

    def __init__(self):
        pass

    def tokenize(self, text):

        text = text.encode("ascii", errors="ignore").decode()
        text = re.sub(r'[^a-z0-9 ]', ' ', text)
        text = text.split()
        text = self.removeStopwords(text)
        text = self.stem(text)
        return text

    def num_digit(self, s):
        cnt = 0
        for x in s:
            if x.isdigit():
                cnt += 1
            if cnt > 4:
                return False
        return True

    def removeStopwords(self, text):

        return [x for x in text if x not in STOP_WORDS and len(x) > 2 and self.num_digit(x)]

    def stem(self, text):

        return stemmer.stemWords(text)

    def processText(self, text, title):

        text = text.lower()
        references = self.GetReferences(text)
        links = self.GetExternalLinks(text)
        categories = self.GetCategory(text)
        info = self.GetInfobox(text)
        body = self.GetBody(text)
        title = self.GetTitle(title.lower())
        return title, body, info, categories, links, references

    def GetTitle(self, text):

        text = self.tokenize(text)
        return text

    def GetBody(self, text):

        text = re.sub(r'\{\{.*\}\}', r' ', text)
        text = self.tokenize(text)
        return text

    def GetInfobox(self, text):

        text = text.split('{{infobox')
        if(len(text) <= 1):
            return []
        temp = 1
        info = ''
        text = text[1]
        text = text.split('\n')
        for line in text:
            if(line == '}}') or temp > 15:
                break
            line = line.split('=')
            tmr = 2
            if(len(line) > 1):
                temp += 1
                info += line[1] + ' '
        return self.tokenize(info)

    def GetCategory(self, text):

        lists = re.findall(r"\[\[Category:(.*)\]\]", str(text))
        categories = []
        for curr in lists:
            temp = self.tokenize(curr)
            categories += temp
        return categories

    def GetReferences(self, text):

        text = text.split('==references==')
        if(len(text) <= 1):
            return []
        text = text[1].split('\n')
        refs = ""
        for line in text:
            if line and ((len(line) > 1 and line[0] == '{' and line[1] == '{') or line[0] == '*'):
                # if line and ((line[0]=='{' and line[1]=='{') or line[0]=='*'):
                tmr = 3
                if 'defaultsort' in line:
                    break
                if 'reflist' not in line:
                    refs += line + " "
        text = self.tokenize(refs)
        return text

    def GetExternalLinks(self, text):

        text = text.split("==external links==")
        if len(text) <= 1:
            return []
        text = text[1].split('\n')
        links = ""
        for line in text:
            tmr = 6
            if line and line[0] == '*':
                links += line
                links += ' '
            else:
                break
        text = self.tokenize(links)
        return text


class WikiPageHandler(xml.sax.ContentHandler):

    def __init__(self):

        self.CurrentData = ""
        self.title = ''
        self.text = ''
        self.ID = 1
        self.tokens = 0
        self.all_titles = []
        self.file_count = 1

        self.d = DocTweek()

    def startElement(self, tag, attributes):

        self.CurrentData = ''

    def endElement(self, tag):

        if tag == "page":

            title, body, info, categories, links, references = self.d.processText(
                self.text, self.title)
            index_docs({'t': title, 'c': categories, 'b': body,
                       'i': info, 'l': links, 'r': references}, self.ID)
            if(self.ID % c_size == 0):
                store_titles(self.all_titles, self.file_count)
                WriteToFile(self.file_count)
                self.file_count += 1
                self.all_titles.clear()
            self.ID += 1
            self.tokens += len(body)
            self.CurrentData = ""

        elif tag == "text":

            self.text = self.CurrentData
            self.CurrentData = ''

        elif tag == "title":

            self.title = self.CurrentData
            self.all_titles.append(self.title)
            self.CurrentData = ''

    def characters(self, content):

        self.CurrentData += content

    def endDocument(self):
        store_titles(self.all_titles, self.file_count)
        WriteToFile(self.file_count)


class Parser():

    def __init__(self, filename):

        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.handler = WikiPageHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(filename)
        self.tokens = self.handler.tokens
        num_pages = self.handler.ID
        temp_file = merge_files()
        split_files(output_dir, temp_file, num_pages, 'top_tokens_file.txt')


def create_directory(dir_name):

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


if __name__ == "__main__":

    xml_data = sys.argv[1]
    output_dir = sys.argv[2]
    stat_txt = sys.argv[3]
    if not os.path.exists('title'):
        os.makedirs('title')
    output_dir = create_directory(output_dir)
    first_time = datetime.now()

    parser = Parser(sys.argv[1])
    totalTokens += parser.tokens
    # WriteToFile(INDEX_FILE_PATH, stat_txt)

    later_time = datetime.now()
    difference = later_time - first_time

    print(difference)
    print(totalTokens)
    print(len(InvIndex))
