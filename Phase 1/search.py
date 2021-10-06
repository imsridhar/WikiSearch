import os
from Stemmer import Stemmer
import sys
import json
posting = {}
stemmer = Stemmer('porter')
mp = {"t":"Title","i":"Infobox","b":"Body","c":"Category","r":"References","l":"External Links"}            
def result(wordlist, field=None):

    for word in wordlist:
        print(word)
        word = word.lower()
        word = stemmer.stemWord(word)
        
        try:
            # if field:
            # print('\n')
            #     if field in posting[word]:
            #         index=posting[word].find(field)
            #         ans= posting[word][index:].split(' ')
            #         jsonstr = json.dumps(ans)
            #         print(jsonstr)
            #     else:
                    # print("No results found")
            # else:
            lst = posting[word].split()
            ans = {}
            for cat in lst:
                f = cat[0]
                cat = cat[2:].split(',')
                docs = [x.split(":")[0] for x in cat]
                if docs[-1]=="":
                    docs = docs[:-1]
                ans[mp[f]] = docs
            print(json.dumps(ans))
        except:
            print("No results found")

if __name__ == "__main__":
    
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.split(' ',1)
            posting[line[0]] = line[1]
    
    print('Seaching your Query')
    search = sys.argv[2]
    if ':' in search:
        flag = True
        while flag:
            index = search.find(':')
            if index==-1:
                flag = False
                break
            
            field = search[index-1]
            search = search[index+1:]
            index = search.find(":")
            if index == -1:
                search = search.split()
                result(search,field)
                flag = False
                break
            
            else:    
                query = search[:index-1]
                query = query.split()
                # print(query)
                result(query, field)
                search = search[index-1:]
    else:
        # print('else kaam kiya')
        search = search.split(" ")
        # print(search)
        result(search)