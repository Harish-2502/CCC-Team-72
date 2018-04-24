# Build and deployment of Spark 2 on Docker

These are the steps to follow in order to simulate a Spark cluster on a single computer.


## Prerequirements

1. Install Docker CE `https://docs.docker.com/engine/installation/`
2. Install Docker Compose `https://docs.docker.com/compose/install/`
3. About 2GB of RAM available for this cluster


## Building of spark image

```
  docker build spark-2 --tag spark-2:2.1.0
```


## Cluster creation and start (1 master, 1 worker)

```
  docker-compose up
```


## Word-count example on generated data

Open a new shell to execute these commands
  
```
export mastercont=`docker ps | grep spark-master | cut -f1 -d' '`
docker exec -ti ${mastercont} /bin/bash
pyspark
execfile('/root/wc.py')
exit()
exit
```

To look at the computation tasks and stages, point your browser
to: `http://localhost:4040`

To look at the cluster workers, point your browser to: `http://localhost:8080`


## Interactive Spark session with the Python shell

```
export mastercont=`docker ps | grep spark-master | cut -f1 -d' '`
docker exec -ti ${mastercont} /bin/bash
pyspark
```
(Execute `exit()` to leave the shell.)


## Cluster stop and re-start

```
  docker-compose stop
  docker-compose start
```

