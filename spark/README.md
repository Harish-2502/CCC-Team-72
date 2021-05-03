# Build and deployment of Spark on Docker

These are the steps to follow in order to simulate a Spark cluster on a single computer.

Note to MacOS users: the memory available to Docker (say, on Docker Desktop) has to be set at least to 4GB to run thw workshop code.


# Building of a spark image

```shell script
docker build --tag spark:latest\
   --build-arg SPARK_VERSION=3.1.1\
   spark-image 
```


## Cluster creation and start (1 master, 2 workers)

```shell script
docker-compose up
```


## Word-count example on generated data

Open a new shell to execute these commands

```shell script
docker cp data/wc.py spark_spark-master_1:/tmp
docker cp data/wc.txt spark_spark-master_1:/tmp
docker exec -ti spark_spark-master_1 /bin/bash
pyspark
exec(open('/tmp/wc.py', "rb").read())
exit()
exit
```

To have a look at the cluster workers, point your browser to: `http://173.17.2.2:8080`
(`http://0.0.0.0:8080` on MacOS)


## Cluster stop and re-start

```shell script
  docker-compose stop
  docker-compose start
```


## Topic Modelling

Topic modelling is a problem that can be solved by using clustring techniques such
as Latent Dirichlet Allocation.

I took inspiraiton from [this blog entry](https://medium.com/@connectwithghosh/topic-modelling-with-latent-dirichlet-allocation-lda-in-pyspark-2cb3ebd5678e)
to develop am LDA implementaiton in Python for Spark. 

The corpus (1,000 bloggers) are taken from [this repository](https://u.cs.biu.ac.il/~koppel/BlogCorpus.htm) 


### Cluster set-up for the LDA

```shell
docker cp blogs.tar.gz spark_spark-master_1:/tmp
docker exec spark_spark-master_1 /bin/bash -c '\
  cd /tmp;\
  tar xvfz blogs.tar.gz'
```

Libraries installation on every node of the cluster:
```shell
for s in $(docker ps --quiet); do
  echo ${s}
  docker exec ${s} bash -c '\
    pip install pandas numpy nltk lxml;\
    python -m nltk.downloader -d /usr/local/share/nltk_data stopwords;\
    python -m nltk.downloader -d /usr/local/share/nltk_data punkt;\
    python -m nltk.downloader -d /usr/local/share/nltk_data averaged_perceptron_tagger;\
  '
done  
```


### Start of the PySpark session

Access the master container:
```shell
docker exec -ti spark_spark-master_1 bash
```

Start an interactive PySpark session:
```shell
pyspark --master spark://0.0.0.0:7077 --deploy-mode client 
```


### Topic modelling execution:

Package imports:
```python
import pandas as pd
import re 
import pyspark
import nltk
from os import listdir
from lxml import etree
from nltk.corpus import stopwords
from pyspark.ml.feature import CountVectorizer, IDF
from pyspark.mllib.linalg import Vector, Vectors
from pyspark.mllib.clustering import LDA, LDAModel
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
```

Read corpus documents from XML files: 
```python
corpusDir= '/tmp/blogs'
documents= []
for f in listdir(corpusDir):
  try:
    tree = etree.parse(corpusDir + '/' + f)
    for child in tree.getroot():
      if child.tag == 'post':
        documents.append(etree.tostring(child, method="text", encoding='utf-8')\
          .decode('utf-8').strip().lower())
  except etree.ParseError:      
    pass
```

Topic modelling parameters:
```python
minWordLength= 4
numTopics= 10
maxIterations= 100
wordNumbers= 5
vocabSize= 5000
minDF= 10.0 # Minimum number of docs the term has to appear in   
```

Initial text processing:
```python
stemmer= PorterStemmer()
engStopwords= stopwords.words('english')
tokens = sc.parallelize(documents)\
    .map(lambda document: word_tokenize(document)) \
    .map(lambda document: [x[0] for x in nltk.pos_tag(document) if x[1][0:1] == 'N']) \
    .map(lambda document: [x for x in document if x.isalpha()]) \
    .map(lambda document: [x for x in document if len(x) >= minWordLength] ) \
    .map(lambda document: [x for x in document if x not in engStopwords]) \
    .map(lambda document: list(map(lambda token: stemmer.stem(token), document)))\
    .zipWithIndex()
```

Compute metrics:
```python
df_txts = sqlContext.createDataFrame(tokens, ['list_of_words', 'index'])    
cv = CountVectorizer(inputCol='list_of_words', outputCol='raw_features',\
   vocabSize=vocabSize, minDF=minDF)
cvmodel = cv.fit(df_txts)
vocabArray= cvmodel.vocabulary
result_cv = cvmodel.transform(df_txts)  

idf = IDF(inputCol='raw_features', outputCol='features')
idfModel = idf.fit(result_cv)
result_tfidf = idfModel.transform(result_cv) 
```

Train the model:
```python
lda_model = LDA.train(result_tfidf[['index','features']].rdd\
   .mapValues(Vectors.fromML)\
   .map(list), k=numTopics, maxIterations=maxIterations)
```


### Display of results

Show processing in the Spark webamdin, point your browser to:
* `http://173.17.2.2:8080/` (`http://0.0.0.0:8080` on MacOS)
* `http://173.17.2.2:4040/` (`http://0.0.0.0:4040` on MacOS)
* `http://173.17.2.3:8081/` (It does not work under MacOS)
* `http://173.17.2.4:8081/` (It does not work under MacOS)

NOTE: the `4040` application is active only when a job is running (such as when there is a PySpark session active).

Describe the top topics and show their top (stemmed) words in the PySpark shell:
```python
topicIndices = sc.parallelize(lda_model.describeTopics(maxTermsPerTopic=wordNumbers))

def topic_render(topic):
    terms = topic[0]
    result = []
    for i in range(wordNumbers):
      result.append(vocabArray[terms[i]])
    return result

topics_final = topicIndices.map(lambda topic: topic_render(topic)).collect()

for topic in range(len(topics_final)):
    print ('Topic {}: {}'.format(str(topic), topics_final[topic]))   
```

Given the probabilistic nature of LDA, different runs may yield slightly different topics.


