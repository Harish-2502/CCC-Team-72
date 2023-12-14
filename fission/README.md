# Fission FaaS

## Pre-requireemnts

* A cluster on NeCTAR (see the "elastic" directory)
* ElasticSearch already installed (see above)
* "k" and "o" aliases defined (see above)
* RC file (with password inserted) read (see above)
* "KUBECONFIG" environment variable set (see above)


## Software stack

## Installation of the software stack

```shell
export FISSION_VERSION='1.20.0'
export KEDA_VERSION='2.9'
export STRIMZI_VERSION='0.38.0'
k create -k "github.com/fission/fission/crds/v1?ref=v${FISSION_VERSION}"
helm repo add fission-charts https://fission.github.io/fission-charts/
helm repo add kedacore https://kedacore.github.io/charts
helm repo add ot-helm https://ot-container-kit.github.io/helm-charts/
helm repo add strimzi https://strimzi.io/charts/
helm repo update
helm upgrade fission fission-charts/fission-all --install --version v${FISSION_VERSION} --namespace fission --create-namespace 
helm upgrade keda kedacore/keda --install --namespace keda --create-namespace --version ${KEDA_VERSION}
helm upgrade kafka strimzi/strimzi-kafka-operator --install --namespace kafka --create-namespace --version ${STRIMZI_VERSION}
 
```

[Detailed instructions](https://fission.io/docs/installation/)

Wait for all pods to have started:
```shell
k get pods -n fission --watch
k get pods -n keda --watch
k get pods -n kafka --watch
```

Wait for the external IP address to be assigned (wait until is no longer "pending"):
```shell
k get svc -n fission | grep router
```


### Creation of a Kafka cluster and topics

```shell
k apply -f https://strimzi.io/examples/latest/kafka/kafka-persistent-single.yaml -n kafka
```

Wait for all pods to have started:
```shell
k get pods -n kafka --watch
```

The Kafka cluster `my-cluster` is now ready to be used; it has a single broker and a single Zookeeper node.
```shell
k get pods -n kafka
k get kafka -n kafka
k get kafkatopic -n kafka
```


### Kafka web-admin installation

```shell
helm repo add kafka-ui https://provectus.github.io/kafka-ui-charts
helm repo update
helm upgrade kafka-ui kafka-ui/kafka-ui --install --namespace kafka -f kafka-ui-config.yaml
```

Forward the pod port to the localhost:
```shell
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka-ui,app.kubernetes.io/instance=kafka-ui" -o jsonpath="{.items[0].metadata.name}")
k --namespace default port-forward $POD_NAME 8080:8080
````
Point your browser to `http://localhost:8080`


### Un-installation of the software stack

```shell
helm uninstall fission --namespace fission 
helm uninstall keda --namespace keda
helm uninstall kafka-ui --namespace kafka 
helm uninstall kafka --namespace kafka
```


## Install Fission FaaS Client on your Laptop

Mac:
```shell
curl -Lo fission https://github.com/fission/fission/releases/download/v${FISSION_VERSION}/fission-v${FISSION_VERSION}-darwin-amd64\
   && chmod +x fission && sudo mv fission /usr/local/bin/
```

Linux:
```shell
curl -Lo fission https://github.com/fission/fission/releases/download/v${FISSION_VERSION}/fission-v${FISSION_VERSION}-linux-amd64\
   && chmod +x fission && sudo mv fission /usr/local/bin/
```

Windows:
For Windows, you can use the linux binary on WSL, or you can download this windows executable:
https://github.com/fission/fission/releases/download/v${FISSION_VERSION}/fission-v${FISSION_VERSION}-windows-amd64.exe


## Create a Fission Function and Expose it as a Service

* Add an alias to simplify typing
```shell
alias f=$(which fission)
```

Create the Python environment on the cluster with the Python builder (it allows to extend the base Python image),
and the Node.js environment and builder:
```shell
f env create --name python --image fission/python-env --builder fission/python-builder
f env create --name nodejs --image fission/node-env --builder fission/node-builder
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
f function create --name health --env python --code ./functions/health.py
f function test --name health | jq '.' 
```

Create an ingress so that the function can be accessed from outside the cluster:
```shell
f route create --url /health --function health --createingress
```

Grab the IP address of the router and send a request:
```shell
IP=$(k get svc -n fission | grep router | tr -s " " | cut -f 4 -d' ')
curl "http://${IP}/health" | jq '.'
````


## Create a Fission Function that harvests Data from the Bureau of Meteorology and stores them in ElasticSearch

```shell
f function create --name bom --env python --code ./functions/bom.py
f function test --name bom | jq '.' 
```


## Call the function at interval using a timer trigger

```shell
f timer create --name everyminute --function bom --cron "@every 1m"
f function log -f --name bom
```

Delete the timer:
```shell
f timer delete --name everyminute
```


## Create a function that uses additional Python libraries

The function used so far are very simple and do not require any additional Python libraries: let's
see how we can pack libraries together with a function source code.

In order to do so, a `requirements.txt` file must be created in the same directory as the function, then
a `build.sh` command must be created to install the libraries and finally the function must be packaged in a ZIP file.

```shell
zip -jr addobservation.zip functions/addobservation/
```

Creation of a function with dependencies:
```shell
f package create --sourcearchive addobservation.zip\
  --env python\
  --name addobservation\
  --buildcmd './build.sh'
```

Check the package has been created:
```shell
f package list | grep addobservation 
```

Function creation:
```shell
f fn create --name addobservation\
  --pkg addobservation\
  --entrypoint "addobservation.main" # Function name and entrypoint
```

Test the function:
```shell
f function test --name addobservation | jq '.'
```

## Build an index to hold weather observations

Start a port redirct in a shell:
```shell
curl -k 'https://0.0.0.0:9200' --user 'elastic:elastic' | jq '.'

```

Create the index:
```shell
curl -XPUT -k 'https://0.0.0.0:9200/observations'\
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
            "wmo": {
                "type": "integer"
            },
            "name": {
                "type": "text"
            },
            "geo": {
                "type": "point"
            },
            "local_date_time": {
                "type": "text"
            },
            "local_date_time_full": {
                "type": "text"
            },
            "air_temp": {
                "type": "short"
            },
            "rel_hum": {
                "type": "short"
            }
        }
    }
}'\
   --user 'elastic:elastic' | jq '.'

```


## Function composition using message queues

Functions can be composed for added flexibility and reuse. For example, let's create a function that
reads a BOM weather report and extracts the meteorological data for a given day at am individual location, 
then another that splits each observation as single document, then another that adds the documents to ElasticSearch.

To do this, we need to create three topics (queues) in Kafka:
* a `weather` topic that contains the raw data from the BOM;
* a `documents` topic that contains the documents to be added to ElasticSearch;
* an `errors` topic that contains possible errors.

```shell
k apply -f ./topics/weather.yaml -n kafka
k apply -f ./topics/documents.yaml -n kafka
k apply -f ./topics/errors.yaml -n kafka
```

Let's start be defining a function that transform BOM weather observation JSON into s simpler document that 
retains only temperature, location (in a format ElasticSearch can digest), and time data in an array:

```shell
f function create --name splitter --code functions/splitter.js --env nodejs
f function test --name splitter
f route create --url /splitter --function splitter --createingress 
```

```shell
zip -jr wharvester.zip functions/wharvester/
f package create --sourcearchive wharvester.zip\
  --env python\
  --name wharvester\
  --buildcmd './build.sh'
  
f fn create --name wharvester\
  --pkg wharvester\
  --entrypoint "wharvester.main" # Function name and entrypoint

f function test --name wharvester | jq '.'
```

Let's create a workflow than connects the functions that grabs data from the BOM, the one that splits and
simplifies, and the one that stores the data in ElasticSearch:

```shell
f mqtrigger create --name weather-split\
   --function splitter\
   --mqtype kafka\
   --mqtkind keda\
   --topic weather\
   --resptopic documents\
   --errortopic errors\
   --maxretries 3\
   --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092\
   --metadata consumerGroup=my-group\
   --cooldownperiod=30\
   --pollinginterval=5

f mqtrigger create --name weather-ingest\
   --function addobservation\
   --mqtype kafka\
   --mqtkind keda\
   --topic documents\
   --errortopic errors\
   --maxretries 3\
   --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092\
   --metadata consumerGroup=my-group\
   --cooldownperiod=30\
   --pollinginterval=5
```


## Remove Fission FaaS from the Cluster

```shell
helm uninstall fission
kubectl delete -k "github.com/fission/fission/crds/v1?ref=v${FISSION_VERSION}"
```


## Harvest Data from the Bureau of Meteorology

List of stations:
http://reg.bom.gov.au/vic/observations/melbourne.shtml

Single station observations: 
http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json


## Air Quality observations:

```shell
curl -XGET -G "https://naqd.eresearch.unimelb.edu.au/geoserver/wfs"\
  --data-urlencode service='WFS'\
  --data-urlencode version='2.0.0'\
  --data-urlencode request='GetFeature'\
  --data-urlencode typeName='geonode:vic_observations_2023'\
  --data-urlencode outputFormat='application/json'\
  --data-urlencode cql_filter="site_name='Mildura' and time_stamp>=2023-07-11T00:00:00Z and time_stamp<2023-07-12T00:00:00Z"\
  | jq '.'
```
