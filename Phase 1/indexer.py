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


stemmer = Stemmer('porter')
stopWords = set(stopwords.words('english'))
InvIndex = {}
totalTokens = 0
tmr=0

def index_docs(data, docID):    

    global InvIndex
    for f in data:
        Count = Counter()
        for word in data[f]:
            Count[word]+=1
        for word in Count:
            tmr=5
            if word in InvIndex:
                if f in InvIndex[word]:
                    InvIndex[word][f].append((docID, Count[word]))
                else:
                    InvIndex[word][f] = [(docID, Count[word])]
            else:
                InvIndex[word] = {}
                InvIndex[word][f] = [(docID, Count[word])]
    return


def WriteToFile(filename, STAT_FILE):
    global totalTokens
    #write statistics into file
    statistics = "Total tokens= " + str(totalTokens) + "\n" + "Total inverted tokens= " + str(len(InvIndex.keys()))
    with open(STAT_FILE, "w") as file:
        file.write(statistics)

    # global InvIndex
    print('Saving stats... ')
    with open(filename, 'w') as f:
        tokens = InvIndex.keys()
        for token in tokens:
            f.write(token)
            f.write(" ")
            field_keys = InvIndex[token].keys()

            for field in field_keys:
                f.write(field)
                f.write("-")
                for page, counttt in InvIndex[token][field]:
                    tmr=1
                    f.write(str(page))
                    f.write(":")
                    f.write(str(counttt)+',')
                f.write(' ')
            f.write("\n")

class DocTweek():

    def __init__(self):
        pass

    def tokenize(self, text):

        text = text.encode("ascii", errors="ignore").decode()
        text = re.sub(r'[^a-z0-9 ]',' ',text)
        text = text.split()
        text = self.removeStopwords(text)
        text = self.stem(text)
        return text

    def removeStopwords(self, text):

        return [x for x in text if x not in STOP_WORDS and len(x)>2]

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
        if(len(text)<=1):
            return []
        temp=1
        info=''
        text = text[1]
        text = text.split('\n')
        for line in text:
            if(line=='}}') or temp>15:
                break
            line = line.split('=')
            tmr=2
            if(len(line)>1):
                temp+=1
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
        if(len(text)<=1):
            return []
        text = text[1].split('\n')
        refs = ""
        for line in text:
            if line and ((line[0]=='{' and line[1]=='{') or line[0]=='*'):
                tmr=3
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
            tmr=6
            if line and line[0] == '*':
                links += line
                links+=' '
            else:
                break
        text = self.tokenize(links)
        return text


class WikiPageHandler(xml.sax.ContentHandler):
    
    def __init__(self):
    
        self.CurrentData = ""
        self.title = ''
        self.text = ''
        self.ID = 0
        self.tokens = 0
        self.all_titles = []
        self.d=DocTweek()

    def startElement(self, tag, attributes):

        self.CurrentData = ''

    def endElement(self, tag):

        if tag == "page":

            # if(self.x):
            #     self.x.join()
            # self.x = threading.Thread(target=index_docs, args=({'t':title, 'c':categories, 'b':body, 'i':info, 'l':links, 'r':references},self.ID))
            # self.x.start()
            # x = index_docs({'t':title, 'c':categories, 'b':body, 'i':info, 'l':links, 'r':references}, self.ID)
            title, body, info, categories, links, references = self.d.processText(self.text, self.title)
            index_docs({'t':title, 'c':categories, 'b':body, 'i':info, 'l':links, 'r':references}, self.ID)
            
            self.ID+=1
            self.tokens+= len(body)
            self.CurrentData=""       

        elif tag == "text":

            self.text = self.CurrentData
            self.CurrentData = ''

        elif tag == "title":

            self.title = self.CurrentData
            self.all_titles.append(self.title)
            self.CurrentData = ''

    def characters(self, content):
  
        self.CurrentData += content 

class Parser():

    def __init__(self, filename):

        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.handler = WikiPageHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(filename)
        self.tokens = self.handler.tokens       

def create_directory(dir_name):

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

if __name__ == "__main__":

    xml_data = sys.argv[1]
    output_dir = sys.argv[2]
    stat_txt = sys.argv[3]

    output_dir=create_directory(output_dir)
    INDEX_FILE_PATH = os.path.join(output_dir, "index.txt")

    first_time = datetime.now()
    
    parser = Parser(sys.argv[1])
    totalTokens += parser.tokens
    WriteToFile(INDEX_FILE_PATH, stat_txt)
    
    later_time = datetime.now()
    difference = later_time - first_time

    print(difference)
    print(totalTokens)
    print(len(InvIndex))
