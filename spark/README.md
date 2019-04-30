# Build and deployment of Spark 2 on Docker

These are the steps to follow in order to simulate a Spark cluster on a single computer.


## Prerequirements

1. Install Docker CE `https://docs.docker.com/engine/installation/`
2. Install Docker Compose `https://docs.docker.com/compose/install/`
3. About 2GB of RAM available for this cluster
4. A Linux-based shell (it works with MacOS as well)


## Building of spark image

```bash
docker build --tag spark-2:2.4.1 spark-2 
```


## Cluster creation anpwdpwdd start (1 master, 1 worker)

```bash
docker-compose up
```


## Word-count example on generated data

Open a new shell to execute these commands
  
```bash
docker exec -ti spark_spark-master_1 /bin/bash
pyspark
execfile('/root/wc.py')
exit()
exit
```

To have a look at the cluster workers, point your browser to: `http://173.17.2.1:8080`


## Interactive Spark session with the Python shell

```bash
docker exec -ti spark_spark-master_1 /bin/bash
pyspark
```

To execute the word count example and have a look on how it is done:
```python
execfile('/root/wc.py')
```

To have a look at the computation tasks and stages, point your browser
to: `http://173.17.2.1:4040`

(Execute `exit()` to leave the pySpark shell, then `exit` again to leave the Docker container Bash shell.)


## Cluster stop and re-start

```bash
  docker-compose stop
  docker-compose start
```

