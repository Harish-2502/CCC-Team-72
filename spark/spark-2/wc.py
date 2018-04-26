from pyspark import SparkConf, SparkContext
import re

words= re.split('\W+', open("/root/wc.txt").read())
wordsRDD= sc.parallelize(words)
countsRDD = wordsRDD.map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b)

wc = countsRDD.collect()
print(wc)    