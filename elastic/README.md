# ElasticSearch

## Pre-requireemnts

* OpenStack clients (`sudo snap install openstackclients`) 5.4.x
* Kubectl 1.28.x
* A NeCTAR project with enough resources to create a Kubernetes cluster
* An Open RC file for the project (named `openrc.sh`)
* Helm 3.6.x


## Kubernetes Cluster Provisioning

* Create a directory that will hold your cluster configuration:
```shell
mkdir <mycluster>
cd <mycluster>
```
* Download the OpenStack RC file from the Dashboard the directory you are in;
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
. ./openrc.sh
```
* Create a Kubernetes cluster named "elastic" with the MRC Dashboard with template `kubernetes-melbourne-v1.23.8` (1 master node of a `r3.small` flavor, at least 3 worker nodes of `r3.medium`);
* NOTE: how a single student can have enough resources for the whole team?
* Check whether the cluster has been created healthy:
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
it should return a master node and the required number of worker nodes:
```shell
NAME                            STATUS   ROLES    AGE   VERSION
elastic-42ehxxqwt3lv-master-0   Ready    master   25h   v1.25.9
elastic-42ehxxqwt3lv-node-0     Ready    <none>   25h   v1.25.9
elastic-42ehxxqwt3lv-node-1     Ready    <none>   25h   v1.25.9
elastic-42ehxxqwt3lv-node-2     Ready    <none>   25h   v1.25.9
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
. ./openrc.sh
```


## ElasticSearch Storage Class 

```shell
k apply -f ./storage-class.yaml
```


## ElasticSearch Cluster Deployment

```shell
k create namespace elastic
helm repo add elastic https://helm.elastic.co
helm repo update
helm upgrade --install \
  --version=8.5.1 \
  --namespace elastic \
  -f ./elastic-values.yaml \
  --set replicas=3 \
  --set secret.password="elastic"\
  elasticsearch elastic/elasticsearch
```

Check all ElasticSearch pods are running before proceeding:
```shell
k get pods -l release=elasticsearch -n elastic
```

```shell
helm upgrade --install \
  --version=8.5.1 \
  --namespace elastic \
  -f ./kibana-values.yaml \
  kibana elastic/kibana
```

Check all ElasticSearch pods are running before proceeding:
```shell
k get pods -l release=kibana -n elastic
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

To access services on the cluster, one has to use the `port-forward` command of `kubectl`:
```shell 
k port-forward service/elasticsearch-master -n elastic 9200:9200
```

To access the Kibana user interface, one has to use the `port-forward` command of `kubectl`:
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

Go to Kibana, create a data view named "students" with pattern "student*", and check that the documents have been 
added to the index by going to "Analysis / Discover".

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
(The use of a body in a GET request is not RESTful, but it is allowed by ElasticSearch).


## Install Fission FaaS on the Cluster

```shell
FISSION_VERSION='1.19.0'
k create namespace fission
k create -k "github.com/fission/fission/crds/v1?ref=v${1.19.0}"
helm repo add fission-charts https://fission.github.io/fission-charts/
helm repo update
helm install --version v1.19.0 --namespace fission fission fission-charts/fission-all
```

Wait for all pods to have started:
```shell
k get pods -n fission
```

Wait for the external IP address to be assigned:
```shell
k get svc -n fission | grep router
```


## Install Fission FaaS Client on your Laptop

Mac:
```shell
curl -Lo fission https://github.com/fission/fission/releases/download/v${1.19.0}/fission-v${1.19.0}-darwin-amd64\
   && chmod +x fission && sudo mv fission /usr/local/bin/
```

Linux:
```shell
curl -Lo fission https://github.com/fission/fission/releases/download/v${1.19.0}/fission-v${1.19.0}-linux-amd64\
   && chmod +x fission && sudo mv fission /usr/local/bin/
```

Windows:
For Windows, you can use the linux binary on WSL, or you can download this windows executable:
https://github.com/fission/fission/releases/download/v${1.19.0}/fission-v${1.19.0}-windows-amd64.exe


## Create a Fission Function and Expose it as a Service

Create the Python environment on the cluster:
```shell
fission env create --name python --image fission/python-env
```

Find the Kubernetes ElasticSearch service:
```shell
k get svc -n elastic
```

The name of the service is `elasticsearch-master` and the port is `9200`; to this we have to add the
namespace and the suffix that the Kubernetes DNS uses to route services within the cluster.
`elasticsearch-master` becomes `elasticsearch-master.elastic.svc.cluster.local`.

The `health.py` source code checks the stato of thee ElasticSearch cluster and returns it:

Test the function:
```shell
fission function create --name health --env python --code health.py
fission function test --name health | jq '.' 
```

Create an ingress so that the function can be accessed from outside the cluster:
```shell
fission route create --url /health --function health-py --createingress
```

Grab the IP address of the router and send a request:
```shell
IP=$(k get svc -n fission | grep router | tr -s " " | cut -f 4 -d' ')
curl "http://${IP}/health" -vvv
````


## Create a Fission Function that Harvests Data from the Bureau of Meteorology and stores them in ElasticSearch

```shell
fission function create --name bom --env python --code bom.py
fission function test --name bom | jq '.' 
```


## Call the function at interval using a timer trigger

```shell
fission timer create --name everyminute --function bom --cron "@every 1m"
```


## Harvest Data from the Bureau of Meteorology

List of stations:
http://reg.bom.gov.au/vic/observations/melbourne.shtml

Single station observations: 
http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json


## ElasticSearch Cluster Removal

```shell
helm uninstall kibana -n elastic
helm uninstall elasticsearch -n elastic
``` 

https://elastic:elastic@elasticsearch-master.elastic.svc.cluster.local:9200/_cluster/health
