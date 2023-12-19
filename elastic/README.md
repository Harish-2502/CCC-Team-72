# ElasticSearch

## Pre-requireemnts

* OpenStack clients (`sudo snap install openstackclients`) 5.4.x
* JQ 1.6.x (`apt install jq`)
* NeCTAR project with enough resources to create a Kubernetes cluster
* Kubectl 1.28.x (installation instructions)[https://kubernetes.io/docs/tasks/tools/]
* Helm 3.6.x (installation instructions)[https://helm.sh/docs/intro/install/]


## Kubernetes Cluster Provisioning

* Download the OpenStack RC file from the MRC Dashboard the directory you are in;
* Add an alias to simplify typing
```shell
alias o='/snap/bin/openstack'
alias k=$(which kubectl)
```
* Set the Kubernetes configuration file:
```shell
export KUBECONFIG="${PWD}/config"
```
* Insert the OpenStack password  in the `./<your project name>-openrc.sh` file 
* Read in the RC file;
```shell
. ./<your project name>-openrc.sh
```
* Create a Kubernetes cluster named "elastic" using the MRC Dashboard with template `kubernetes-melbourne-v1.23.8` (1 master node of a `r3.small` flavor, at least 3 worker nodes of `r3.medium`);
* NOTE: how a single student can have enough resources for the whole team?
* Check whether the cluster has been created healthy (it may take several minutes):
```shell
o coe cluster show elastic --fit-width
```
(`health_status` should be 'HEALTHY' and `coe_version` should be `1.23.8`);
* Create the configuration:
```shell
o coe cluster config elastic
```
* Check the cluster nodes:
```shell
k get nodes
```
it should return a master node and the required number of nodes:
```
NAME                            STATUS   ROLES    AGE   VERSION
elastic-kgzzr5zed2xj-master-0   Ready    master   5m40s   v1.23.8
elastic-kgzzr5zed2xj-node-0     Ready    <none>   2m29s   v1.23.8
elastic-kgzzr5zed2xj-node-1     Ready    <none>   2m31s   v1.23.8
elastic-kgzzr5zed2xj-node-2     Ready    <none>   2m30s   v1.23.8
```

Sometimes the overlay network component is not started correctly, hence it is better to drop and recreate it:
```shell script
k delete pod -l app=flannel -n kube-system
```

Check that all Flannel pods are back running:
```shell
k get pod -l app=flannel -n kube-system
```

It may be convenient to use a script to automate all necessary steps to interact with the cluster:
```shell
#!/bin/bash

alias o='/snap/bin/openstack'
alias k=$(which kubectl)
export KUBECONFIG="${PWD}/config"
export ES_VERSION="8.5.1"
. ./<your project name>-openrc.sh
```


## ElasticSearch Storage Class creation 

```shell
k apply -f ./storage-class.yaml
```


## ElasticSearch cluster deployment

```shell
k create namespace elastic
helm repo add elastic https://helm.elastic.co
helm repo update
helm upgrade --install \
  --version=${ES_VERSION} \
  --namespace elastic \
  -f ./elastic-values.yaml \
  --set replicas=3 \
  --set secret.password="elastic"\
  elasticsearch elastic/elasticsearch
```

Check all ElasticSearch pods are running before proceeding:
```shell
k get pods -l release=elasticsearch -n elastic --watch
```


## Kibana deployment

```shell
helm upgrade --install \
  --version=${ES_VERSION} \
  --namespace elastic \
  -f ./kibana-values.yaml \
  kibana elastic/kibana
```

Check all ElasticSearch pods are running before proceeding:
```shell
k get pods -l release=kibana -n elastic --watch
```

Check all services are running before proceeding:
```shell
k get service -n elastic
```

It should show something like:
```shell
NAME                            TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
elasticsearch-master            ClusterIP   10.254.75.27   <none>        9200/TCP,9300/TCP   17h
elasticsearch-master-headless   ClusterIP   None           <none>        9200/TCP,9300/TCP   17h
kibana-kibana                   ClusterIP   10.254.50.97   <none>        5601/TCP            17h
```


## Accessing the ElasticSearch API and the Kibana User Interface

To access services on the cluster, one has to use the `port-forward` command of `kubectl` in a different shell:
```shell 
k port-forward service/elasticsearch-master -n elastic 9200:9200
```

To access the Kibana user interface, one has to use the `port-forward` command of `kubectl` (another shell):
```shell
k port-forward service/kibana-kibana -n elastic 5601:5601
```

The port forwarding can be stopped by pressing `Ctrl-C` (each has to start in a different terminal window) and
when not used it stops and has to be restarted.

Test the ElasticSearch API:
```shell
curl -k 'https://0.0.0.0:9200' --user 'elastic:elastic' | jq '.'
curl -k 'https://0.0.0.0:9200/_cluster/health' --user 'elastic:elastic' | jq '.'
```

Test the Kibana user interface by pointing the browser to: `http://0.0.0.0:5601/` (the default credentials are `elastic:elastic`).


## Create an ElasticSearch Index

```shell
curl -XPUT -k 'https://0.0.0.0:9200/students'\
   --header 'Content-Type: application/json'\
   --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 2
        }
    },
    "mappings": {
        "properties": {
            "id": {
                "type": "text"
            },
            "name": {
                "type": "text"
            },
            "course": {
                "type": "text"
            },
            "mark": {
                "type": "short"
            }
        }
    }
}'\
   --user 'elastic:elastic' | jq '.'
```

The index should now be shown in the Kibana dashboard. 

Let's try to add a document to the newly created index:
```shell
curl -XPUT -k "https://localhost:9200/students/_doc/1"\
  --header 'Content-Type: application/json'\
  --data '{
       "id": "1",
        "name": "John Smith",
        "course": "Cloud Computing",
        "mark": 80
  }'\
  --user 'elastic:elastic' | jq '.'
curl -XPUT -k "https://localhost:9200/students/_doc/2"\
  --header 'Content-Type: application/json'\
  --data '{
       "id": "2",
        "name": "Jane Doe",
        "course": "Cloud Computing",
        "mark": 90
    }'\
  --user 'elastic:elastic' | jq '.' 
```

You can now do a full text search by just typing "John" in the search box and pressing enter.

Let's do a search via the API:
```shell
curl -XGET -k "https://localhost:9200/students/_search"\
  --header 'Content-Type: application/json'\
  --data '{
    "query": { 
      "match": { 
        "course": "cloud*" 
      } 
    }
  }'\
  --user 'elastic:elastic' | jq '.'
```
(The use of a body in a GET request is not ReSTful, but it is allowed by ElasticSearch).


## Crete a data view from Kibana

Go to Kibana, create a data view named "students" with pattern "student*", and check that the documents have been
added to the index by going to "Analysis / Discover".

Now Kibana can be used to test search queries or to have a look at data..


## ElasticSearch Cluster Removal

```shell
helm uninstall kibana -n elastic
helm uninstall elasticsearch -n elastic
``` 

