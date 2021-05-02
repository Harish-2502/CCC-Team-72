# Build and deployment of Spark 2 on Docker

These are the steps to follow in order to simulate a Spark cluster on a single computer.


## Requirements

* Python 3.6 (I did it with (https://docs.conda.io/en/latest/miniconda.html)[Miniconda3 4.5.4])


# Building of spark image

```shell script
docker build --tag spark:latest\
   --build-arg SPARK_VERSION=3.1.1 --build-arg HADOOP_VERSION=2.7\
   spark-image 
```

```shell script
curl -LO https://raw.githubusercontent.com/bitnami/bitnami-docker-spark/master/docker-compose.yml
docker-compose up
```

docker cp ../spark-image/wc.py bitnami_spark_1:/tmp docker cp ../spark-image/wc.txt bitnami_spark_1:/tmp

## Cluster creation and start (1 master, 1 worker)

```shell script
docker-compose up
```

## Word-count example on generated data

Open a new shell to execute these commands

```shell script
docker exec -ti spark_spark-master_1 /bin/bash
pyspark
exec(open('/tmp/wc.py', "rb").read())
exit()
exit
```

To have a look at the cluster workers, point your browser to: `http://173.17.2.1:8080`

## Cluster stop and re-start

```shell script
  docker-compose stop
  docker-compose start
```

## Topic Modeling

https://medium.com/@connectwithghosh/topic-modelling-with-latent-dirichlet-allocation-lda-in-pyspark-2cb3ebd5678e
https://github.com/hacertilbec/LDA-spark-python/blob/master/SparkLDA.py
https://u.cs.biu.ac.il/~koppel/BlogCorpus.htm

Copy the corpus over to the master container:
```shell
docker cp blogs.tar.gz spark_spark-master_1:/tmp
docker exec spark_spark-master_1 /bin/bash -c '\
  cd /tmp;\
  tar xvfz blogs.tar.gz'

for s in $(docker ps --quiet); do
  echo ${s}
  docker exec ${s} bash -c '\
    pip install pandas numpy nltk lxml;\
    python -m nltk.downloader -d /usr/local/share/nltk_data stopwords;\
    python -m nltk.downloader -d /usr/local/share/nltk_data punkt;\
    ls /root\
  '
done  
```

Access the master container:
```shell
docker exec -ti spark_spark-master_1 bash
```

Start an interactive PySpark session:
```shell
pyspark --master spark://0.0.0.0:7077 --deploy-mode client 
```

Proceed to perform the topic modelling in Python:

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

Show processing in the Sparl webamdin, point your browser to:
* `http://173.17.2.2:8080/`
* `http://173.17.2.2:4040/`
* `http://173.17.2.3:8081/`

Describe the top topics and show their top (stemmed) words:
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


