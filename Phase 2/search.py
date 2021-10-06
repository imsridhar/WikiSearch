import os
from Stemmer import Stemmer
import sys
import json
import time
from nltk.util import pr
from datetime import datetime
posting = {}
stemmer = Stemmer('porter')
mp = {"t": "Title", "i": "Infobox", "b": "Body",
      "c": "Category", "r": "References", "l": "External Links"}

search_results = open('queries_op.txt', 'w')
firstToken = []


def file_search(word, l, r):
    while l <= r:
        mid = int((l+r)/2)
        if word < firstToken[mid]:
            r = mid-1
        else:
            l = mid+1
    return l
# b: cake pink
# def result(wordlist, field = ['b','t']):


def getfileName(w, fileName, word):
    # print(fileName)
    idx = open(fileName, 'r')
    l = idx.readline()
    # find the word from the index file list
    while l:
        l = l.strip()
        token = l.split()[0]
        if token == word:
            w = l
            break
        l = idx.readline()
    idx.close
    return w


def result(wordlist, field=None, outputcount=10):

    ranking = {}
    first_time = datetime.now()
    j = 0

    for word in wordlist:
        # print(word)
        word = word.lower()
        word = stemmer.stemWord(word)

        # find word range from top tokens of each file
        fileNum = file_search(word, 0, len(firstToken)-1)

        if fileNum == 0:
            print('no result found')
            continue

        fileName = 'index/' + str(fileNum) + '.txt'

        # to contain details of word to be found
        w = ''

        w = getfileName(w, fileName, word)

        # # print(fileName)
        # idx = open(fileName, 'r')
        # l = idx.readline().strip()

        # # find the word from the index file list
        # while l:
        #     token = l.split()[0]
        #     if token == word:
        #         w = l
        #         break
        #     l = idx.readline().strip()
        # idx.close

        if w == '':
            continue

        w = w.split()
        w.pop(0)
        # print(w)

        for i in w:
            weight = 1
            if field != None and i[0] != field[j]:
                weight = 0.05 * weight
            i = i.split('-')[1]
            i = i.split(',')
            i.pop()
            temp = 1
            for doc in i:
                docID = doc.split(':')[0]
                tf_idf = float(doc.split(':')[1])*weight
                temp = 0
                if docID in ranking:
                    ranking[docID] += tf_idf
                else:
                    ranking[docID] = tf_idf
        j += 1

    ranking = sorted(ranking.items(), reverse=True,
                     key=lambda kv: (kv[1], kv[0]))
    # res = 10
    k = 10
    for doc in ranking:
        doc_id = int(doc[0])
        title_file = int(doc_id/10000) + 1
        line_num = (doc_id-1) % 10000
        temp = 1
        fil = 'title/' + str(title_file) + '.txt'
        f = open(fil, encoding="utf8")
        l = f.readlines()
        nm = l[line_num]
        temp = 1
        print(doc[0], nm)
        search_results.write(doc[0] + ', ' + nm)
        k -= 1
        if(k == 0):
            # search_results.write(str(time.time()-start) +
            #                      ', ' + str((time.time()-start)/10) + '\n\n')
            break
    
    later_time = datetime.now()
    difference = later_time - first_time
    
    print(difference)


if __name__ == "__main__":

    with open('top_tokens_file.txt', 'r') as TS:
        firstToken = TS.readlines()
        # print(firstToken)

    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
        for line in lines:
            # given to print 10 results for each query
            # if number of outputs to be provided in the query file
            # outputcount = int(line.split(',',1)[0])

            outputcount = 10
            print('Seaching your query: ' + line)
            search = line.strip()
            querylist = []
            fieldList = []
            if ':' in search:
                flag = True
                while flag:
                    # loop breaker, no more fields left
                    index = search.find(':')
                    if index == -1:
                        flag = False
                        break

                    # find which field and what query for that field
                    # and send that to result function- query and field
                    field = search[index-1]
                    search = search[index+1:]
                    index = search.find(":")

                    # if this is the last field query
                    if index == -1:
                        search = search.split()
                        for token in search:
                            print(token)
                            querylist.append(token)
                            fieldList.append(field)
                        # result(search, field, outputcount)
                        flag = False
                        break

                    # more field queries are left
                    else:
                        query = search[:index-1]
                        query = query.split()
                        # print(query)
                        for token in query:
                            querylist.append(token)
                            fieldList.append(field)
                        # result(query, field, outputcount)
                        search = search[index-1:]
                result(querylist, fieldList, outputcount)

            else:
                search = search.split(" ")
                result(search)
