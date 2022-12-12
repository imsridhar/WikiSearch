# WikiSearch
Wrote code to compress any standard Wikipedia dump to an inverted index of 1/4th the size. Can further process the index to return top matching results for any search query based on tf-idf score. Supports ﬁeld queries.

## Wikipedia Search Engine

### Project Objective
In this project, primary task is to build a scalable and efficient search engine on Wikipedia pages. This constitutes two stages - inverted index creation and query search mechanism, where the scope of performance in the second stage relies heavily on the quality of index built in its preceding stage. Throughout the project, efforts have been made to build a system optimized for search time, search efficiency (i.e. the quality of results), indexing time and index size. We have used Wikipedia dumps of size 80GB in XML format, which is parsed to get Wikipedia pages.

### Constructing the Inverted Index
+ Parsing: SAX Parser is used to parse the XML corpus.
+ Casefolding: Converting Upper Case to Lower Case.
+ Tokenisation: It is done using regex.
+ Stop Word Removal: Stop words are removed by referring to the stop word list returned by nltk.
+ Stemming: A python library PyStemmer is used for this purpose.
+ Creating various index files with word to field postings.
+ Multi-way External sorting on the index files to create field based files along with their respective offsets.

### Searching:
+ The query given is parsed, processed and given to the respective query handler(simple or field).
+ One by one word is searched in vocabulary and the file number is noted.
+ The respective field files are opened and the document ids along with the frequencies are noted.
+ The documents are ranked on the basis of TF-IDF scores.
+ The title of the documents are extracted using title.txt

### Files Produced
+ index*.txt (intermediate files) : It consists of words with their posting list. Eg. <word> d1b2t4c5 d5b3t6l1
+ title.txt : It consist of id-title mapping.
+ queries_op.txt : stores output of queries  

### Features:
* Support for Field Queries . Fields include Title, Infobox, Body, Category, Links, and
References of a Wikipedia page. This helps when a user is interested in searching for
the movie ‘Up’ where he would like to see the page containing the word ‘Up’ in the title
and the word ‘Pixar’ in the Infobox. You can store field type along with the word when
you index.

| FIELD | Title | Info | Category | Body | References | External Links |
| ------ | ------ |------ | ------ |------ | ------ |------ | 
| **SYMBOL** | t | i | c | b | r | l |

  **Plain query examples :** `Lionel Messi`, `Barcelona`  
  **Field query examples :** `t:World Cup i:2018 c:Football` – search for ”World Cup” in Title, ”2018” in Infobox and ”Football” in Category
* Index size should be less than 1⁄4 of dump size. 
* Scalable index construction 
* Search Functionality
  * Index creation time: less than 60 secs for Java, CPP and for python it’s less than 150
secs.
  * Inverted index size: 1/4th of entire wikipedia corpus
* Advanced search as mentioned above.


### Index Creation
For creating indexes use the following command : 
```
python3 indexer.py ../enwiki-20210720-pages-articles-multistream.xml ./inverted_indexes
```

### Query Search
For each query string, it returns the top 10 results, each result consisting of the document id and title of the page.  The queries will be provided in a queries.txt file. It can be run as: 
```
python search.py ./inverted_indexes
```

Code writes the search output for the given queries in a `queries_op.txt` file.
**1. queries.txt**
This file given to you will contain each query string printed on a single line.
A dummy queries.txt:
~~~
t:World Cup i:2019 c:cricket
the two Towers
~~~
**2. queries_op.txt**
In this file, for each query, you will have the results printed on 10 lines, each line containing the document id (which is a number specific to your implementation) and title of the corresponding Wikipedia page. The title will be the original page title as contained in the XML dump.
**Dummy results for the above queries:**
~~~
7239, cricket world cup
4971952, 2019 cricket world cup
57253320, 2019 cricket world cup final
.
.
.
(10 lines of retrieved document id - title pairs)
5
63750, the two towers
173944, lord of the rings: the two towers
.
.
.
(10 lines of retrieved document id - title pairs)
2
~~~
### Challenges
- Difficult to process large data of 80 GB
- Can not store word & its posting list into a main memory, So Used K-way Merge sort
- Can not Load full final index into main memory, So Bild Secondary Index on top of Primary Index (Posting List)


### Download links to Wikipedia dumps of languages for the project

| Language | Link |
| ---- | ---- |
| English | https://dumps.wikimedia.org/enwiki/20210720/enwiki-20210720-pages-articles-multistream.xml.bz2 |
| Hindi | https://dumps.wikimedia.org/hiwiki/20210720/hiwiki-20210720-pages-articles-multistream.xml.bz2 |
| Urdu | https://dumps.wikimedia.org/urwiki/20210720/urwiki-20210720-pages-articles-multistream.xml.bz2 |
| Punjabi | https://dumps.wikimedia.org/pawiki/20210720/pawiki-20210720-pages-articles-multistream.xml.bz2 |
| Bengali | https://dumps.wikimedia.org/bnwiki/20210720/bnwiki-20210720-pages-articles-multistream.xml.bz2 |
| Oriya | https://dumps.wikimedia.org/orwiki/20210720/orwiki-20210720-pages-articles-multistream.xml.bz2 |
| Assamese | https://dumps.wikimedia.org/aswiki/20210720/aswiki-20210720-pages-articles-multistream.xml.bz2 |
| Gujarati | https://dumps.wikimedia.org/guwiki/20210720/guwiki-20210720-pages-articles-multistream.xml.bz2 |
| Marathi | https://dumps.wikimedia.org/mrwiki/20210720/mrwiki-20210720-pages-articles-multistream.xml.bz2 |
| Kannada | https://dumps.wikimedia.org/knwiki/20210720/knwiki-20210720-pages-articles-multistream.xml.bz2 |
| Telugu | https://dumps.wikimedia.org/tewiki/20210720/tewiki-20210720-pages-articles-multistream.xml.bz2 |
| Tamil | https://dumps.wikimedia.org/tawiki/20210720/tawiki-20210720-pages-articles-multistream.xml.bz2 |
| Malayalam | (https://dumps.wikimedia.org/mlwiki/20210720/mlwiki-20210720-pages-articles-multistream.xml.bz2) |
