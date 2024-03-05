# Fission FaaS

## Pre-requirements

- OpenStack RC file and API password obtained and sourced in current shell (see [here](../elastic/README.md#client-configuration))
- A Kubernetes cluster created on NeCTAR (see [here](../elastic/README.md#elasticsearch))
- Connect to [Campus network](https://studentit.unimelb.edu.au/wifi-vpn#uniwireless) if on-campus or [UniMelb Student VPN](https://studentit.unimelb.edu.au/wifi-vpn#vpn) if off-campus
- Kubernetes cluster is accessible (see [here](../elastic/README.md#accessing-the-kubernetes-cluster))
- ElasticSearch installed (see [here](../elastic/README.md#elasticsearch))

> Note: the code used here is for didactic purposes only. It has no error handling, no testing, and is not production-ready.

## Installation of Fission FaaS

> Note: make sure the SSH tunnel has been established to the Kubernetes cluster (see [here](../elastic/README.md#accessing-the-kubernetes-cluster)).

```shell
export FISSION_VERSION='1.20.0'
kubectl create -k "github.com/fission/fission/crds/v1?ref=v${FISSION_VERSION}"

helm repo add fission-charts https://fission.github.io/fission-charts/
helm repo update
helm upgrade fission fission-charts/fission-all --install --version v${FISSION_VERSION} --namespace fission \
  --create-namespace --set routerServiceType='ClusterIP'
```

> Note: for detailed instructions see [here](https://fission.io/docs/installation/)

After the installation, wait for all pods to have started. (This command will watch the pods' status. You can use `Ctrl + C` to stop watching once you see the pods are in `Running` state.)

```shell
kubectl get pods -n fission --watch
```

## Fission FaaS Client installation

Mac & Linux:

```shell
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
curl -Lo fission https://github.com/fission/fission/releases/download/v$FISSION_VERSION/fission-v$FISSION_VERSION-$OS-amd64 \
   && chmod +x fission && sudo mv fission /usr/local/bin/
```

Windows:

For Windows, you can use the linux binary on WSL, or you can download this windows executable: `https://github.com/fission/fission/releases/download/v$FISSION_VERSION/fission-v$FISSION_VERSION-windows-amd64.exe`

## Basic Fission

### Create a Fission Function and Expose it as a Service

First, let's create the Python environment on the cluster with the Python builder (it allows to extend the base Python image),
and the Node.js environment and builder:

```shell
fission env create --name python --image fission/python-env --builder fission/python-builder
fission env create --name nodejs --image fission/node-env --builder fission/node-builder
```

Find the Kubernetes ElasticSearch service:

```shell
kubectl get svc -n elastic
```

The name of the service is `elasticsearch-master` and the port is `9200`; to this we have to add the
namespace and the suffix that the Kubernetes DNS uses to route services within the cluster.
`elasticsearch-master` becomes `elasticsearch-master.elastic.svc.cluster.local`.

The `health.py` source code checks the state of the ElasticSearch cluster and returns it:

Test the function:

```shell
fission function create --name health --env python --code ./functions/health.py
fission function test --name health | jq '.'
```

Create an ingress so that the function can be accessed from outside the cluster:

```shell
fission route create --url /health --function health --name health --createingress
```

Start a port forward from the Fission router in different shell:

```shell
kubectl port-forward service/router -n fission 9090:80
```

In a new terminal, invoke the function from port `9090` of your laptop:

```shell
curl "http://127.0.0.1:9090/health" | jq '.'
```

(You can have a look at the function log with `fission function log --name health`.)

### Create a Fission Function that harvests Data from the Bureau of Meteorology

```shell
fission function create --name wharvester --env python --code ./functions/wharvester.py
fission function test --name wharvester
```

### Call the function at interval using a timer trigger

```shell
fission timer create --name everyminute --function wharvester --cron "@every 1m"
fission function log -f --name wharvester
```

(Every minute a new log line should appear.)

Delete the timer:

```shell
fission timer delete --name everyminute
```

## Fission with advanced functions

### Create a function that uses additional Python libraries

#### Build an index to hold weather observations

In a new terminal, start a port forward from ElasticSearch:

```shell
kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
```

Create the index:

```shell
curl -XPUT -k 'https://127.0.0.1:9200/observations' \
   --user 'elastic:elastic' \
   --header 'Content-Type: application/json' \
   --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 2
        }
    },
    "mappings": {
        "properties": {
            "stationid": {
                "type": "text"
            },
            "timestamp": {
                "type": "date"
            },
            "geo": {
                "type": "geo_point"
            },
            "name": {
                "type": "text"
            },
            "local_date_time": {
                "type": "text"
            },
            "air_temp": {
                "type": "float"
            },
            "rel_hum": {
                "type": "float"
            },
            "pm10": {
                "type": "float"
            },
            "pm2p5": {
                "type": "float"
            },
            "ozone": {
                "type": "float"
            }
        }
    }
}'  | jq '.'
```

#### Create a function that stores data in ElasticSearch

The function used so far are very simple and do not require any additional Python libraries: let's
see how we can pack libraries together with a function source code.

In order to do so, a `requirements.txt` file must be created in the same directory as the function, then
a `build.sh` command must be created to install the libraries and finally the function must be packaged in a ZIP file.

```shell
zip -jr addobservations.zip functions/addobservations/
```

Creation of a function with dependencies (this function depends on the ElasticSearch client package to add data to ElasticSearch):

```shell
fission package create --sourcearchive addobservations.zip\
  --env python\
  --name addobservations\
  --buildcmd './build.sh'
```

(Use `package update` to update a package that already exists.)

Check that the package has been created:

```shell
fission package list
```

Function creation:

```shell
fission fn create --name addobservations\
  --pkg addobservations\
  --env python\
  --entrypoint "addobservations.main" # Function name and entrypoint
```

(Use `function update` to update a function that already exists.)

The addition of observations can be tested by looking at the Kibana WebAdmin.

## Use of YAML specifications to deploy functions

### Re-creation of functions with YAML specifications

Let's start by deleting functions, packages, triggers, and even the environments we have created so far:

```shell
fission httptrigger delete --name health
fission function delete --name addobservations
fission function delete --name health
fission function delete --name wharvester
fission package delete --name addobservations
fission environment delete --name python
fission environment delete --name nodejs
```

Creation of a directory to hold our specifications (by default it is named `specs`):

```shell
fission specs init
```

From now on our actions will add YAML files under the `specs` directory (not the `spec` argument),
and the YAML files will then be applied to the cluster with the `kubectl apply` command.

Let's start by creating the specs for the Python and Node.js environments:

```shell
fission env create --spec --name python --image fission/python-env --builder fission/python-builder
fission env create --spec --name nodejs --image fission/node-env --builder fission/node-builder
```

Let's create the specification file for a function:

```shell
fission function create --spec --name health --env python --code ./functions/health.py
```

A file named `function-health.yaml` will be created under the `specs` directory, but so far no actions
has been taken on the cluster.

Let's create the spec for a route to this function:

```shell
fission route create --spec --url /health --function health --name health --createingress
```

Let's check everything is fine with our specs:

```shell
fission spec validate
```

Provided no errors are reported, we can now apply the specs to the cluster:

```shell
fission spec apply --wait
```

`health` function and related route test:

```shell
curl "http://127.0.0.1:9090/health" | jq '.'
```

### Passing of parameters to functions with config maps

Parameters (such as username and passwords) can be passed to functions through the environment
rather than be hard-coded in the source code (which has to be avoided, especially for sensitive information).

A common to share parameters in Kubernetes is through `configmaps`, which are key-value pairs that can be
accessed by all pods within a namespace.
Fission functions can read configmaps as files, so we can create a configmap with the ElasticSearch username and password.

Let's start by creating a configmap as `shared-data.yaml` file under `specs`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: default
  name: shared-data
data:
  ES_USERNAME: elastic
  ES_PASSWORD: elastic
```

Since config maps are not directly managed by Fission, we have to apply it to the cluster with `kubectl`:

```shell
kubectl apply -f specs/shared-data.yaml
```

To use these values we have to modify the `health.py` file to read the config map:

```python
from flask import request, current_app
import requests, logging

def config(k):
    with open(f'/configs/default/shared-data/{k}', 'r') as f:
        return f.read()

def main():
    r = requests.get('https://elasticsearch-master.elastic.svc.cluster.local:9200/_cluster/health',
        verify=False,
        auth=(config('ES_USERNAME'), config('ES_PASSWORD')))
    current_app.logger.info(f'Status ES request: {r.status_code}')
    return r.json()
```

In addition, we have to change the function definition (file `function-health.yaml`) so that the config map is mounted as volume `/configs/default/shared-data`:

```shell
rm specs/function-health.yaml
fission function create --spec --name health --env python --code ./functions/health.py --configmap shared-data
```

To apply the changes we have to run the following command:

```shell
fission spec apply --wait
```

We can now test the function (after waiting for all the pods to have been updated) to see if the environment variables
have been passed correctly:

```shell
fission fn log -f --name health
```

And (in another shell):

```shell
curl "http://127.0.0.1:9090/health"  | jq '.'
```

Fission can read secrets as well, which are better suited to hold sensitive information (such as passwords).

### Creation of a RestFUL API with YAML specifications

Fission HTTPTrigger can be used to create a RESTful API that allows a further decoupling between the function and the
way it is invoked.

For instance, let's suppose we want to query ElasticSearch for the average temperature on a given day for one station or
for all stations.

A ReSTful API may look like:

```
/temperature/{date}
/temperature/{date}/{station}
```

#### Route creation

We start by using the fission commands to create the YAML files defining the routes/HTTPTriggers:

```shell
fission route create --spec --name avgtempday --function avgtemp \
  --method GET \
  --url '/temperature/days/{date:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}'

fission route create --spec --name avgtempdaystation --function avgtemp \
  --method GET \
  --url '/temperature/days/{date:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/stations/{station:[a-zA-Z0-9]+}'
```

#### Function creation

Let's create the function and related package specs:

```shell
fission package create --spec --name avgtemp \
  --source ./functions/avgtemp/*.py \
  --source ./functions/avgtemp/*.txt \
  --source ./functions/avgtemp/*.sh \
  --env python \
  --buildcmd './build.sh'

fission fn create --spec --name avgtemp \
  --pkg avgtemp \
  --env python \
  --entrypoint "avgtemp.main"
```

(From the function point of view the path parameters `date` and `station` are headers prefixed by `X-Fission-Params`.)

Let's apply the specs to the cluster:

```shell
fission spec apply --wait
```

#### ReSTful API test

```shell
curl "http://localhost:9090/temperature/days/2024-01-25" | jq '.'
curl "http://localhost:9090/temperature/days/2024-01-25/stations/95936" | jq '.'
```

(The port forwarding from the Fission router must be running.)

## Development of an Event-driven architecture with Fission

TODO

### Installation of Kafka and Keda

```shell
export KEDA_VERSION='2.9'
export STRIMZI_VERSION='0.38.0'

helm repo add kedacore https://kedacore.github.io/charts
helm repo add ot-helm https://ot-container-kit.github.io/helm-charts/
helm repo add strimzi https://strimzi.io/charts/
helm repo update

helm upgrade keda kedacore/keda --install --namespace keda --create-namespace --version ${KEDA_VERSION}
helm upgrade kafka strimzi/strimzi-kafka-operator --install --namespace kafka --create-namespace --version ${STRIMZI_VERSION}
```

Wait for all pods to have started:

```shell
kubectl get pods -n keda --watch
kubectl get pods -n kafka --watch
```

### Creation of a Kafka cluster and topics

```shell
kubectl apply -f  "https://raw.githubusercontent.com/strimzi/strimzi-kafka-operator/${STRIMZI_VERSION}/examples/kafka/kafka-persistent-single.yaml" \
  -n kafka
```

Wait for all pods to have started:

```shell
kubectl get pods -n kafka --watch
```

The Kafka cluster `my-cluster` is now ready to be used; it has a single broker and a single Zookeeper node.

```shell
kubectl get kafka -n kafka
```

### Kafka web-admin installation

```shell
helm repo add kafka-ui https://provectus.github.io/kafka-ui-charts
helm repo update
helm upgrade kafka-ui kafka-ui/kafka-ui --install --namespace default -f kafka-ui-config.yaml
```

Wait for the pod to start:

```shell
kubectl get pods --watch
```

Forward the pod port to the localhost (in a different shell):

```shell
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka-ui,app.kubernetes.io/instance=kafka-ui" -o jsonpath="{.items[0].metadata.name}")
kubectl --namespace default port-forward $POD_NAME 8080:8080
```

Point your browser to `http://localhost:8080`

### Development of an event-driven application

Functions can be composed for added flexibility and reuse (message queues are used to bind them together).

Let's create a mini-application that:

- harvest meteorological data from the Bureau of Meteorology;
- harvest pollution from the Air Quality project;
- store the data in ElasticSearch.

Since AIRQ and BoM data have different structures, we need to have an intermediate function that filters and splits the data
into a standardized structure that can be added to ElasticSearch.

#### Functions

We would reuse the `wharvester` and `addobservation` functions we introduced earlier, but have also to add:

- an `aharvester` function to get data from the Air Quality project;
- a `Wprocessor` function to filter, convert, and split the BoM data into a simpler structure;
- an `aprocessor` function to filter, convert, and split the AIRQ data into a simpler structure;
- an `enqueue` function to add data to a queue (Kafka topic).

```shell
fission function create --name aharvester --env python --code ./functions/aharvester.py
fission function create --name wprocessor --env nodejs --code ./functions/wprocessor.js
fission function create --name aprocessor --env nodejs --code ./functions/aprocessor.js

zip -jr enqueue.zip functions/enqueue/

fission package create --sourcearchive enqueue.zip \
  --env python \
  --name enqueue \
  --buildcmd './build.sh'

fission fn create --name enqueue \
  --pkg enqueue \
  --env python \
  --entrypoint "enqueue.main"
```

#### Message queues

These functions communicate amongst them by storing and reading messages in queues. In Kafka queues are called "topics",
and for this application we need to create the following topics:

- a `weather` topic that contains the raw data from the BoM;
- an `airquality` topic that contains raw data from the Air Quality project;
- a `observations` topic that contains the documents to be added to ElasticSearch;
- an `errors` topic that contains possible queueing errors.

```shell
kubectl apply -f ./topics/weather.yaml --namespace kafka
kubectl apply -f ./topics/airquality.yaml --namespace kafka
kubectl apply -f ./topics/observations.yaml --namespace kafka
kubectl apply -f ./topics/errors.yaml --namespace kafka
```

To list all the Kafka topic just created:

```shell
kubectl get kafkatopic -n kafka
```

#### Triggers

To bind all these functions and queues together, we have now to create triggers:

- a `weather-ingest` timer trigger to capture BoM data;
- an `airquality-ingest` timer trigger to capture pollution data;
- an `enqueue` HTTP trigger to add data to a message queue;
- a `weather-processing` queue trigger to process meteorological data from a message queue;
- an `airquality-processing` queue trigger to process pollution data from a message queue;
- an `add-observations` queue trigger to add observations to ElasticSearch.

```shell
fission timer create --name weather-ingest --function wharvester --cron "@every 1m"
fission timer create --name airquality-ingest --function aharvester --cron "@every 1m"

fission httptrigger create --name enqueue --url "/enqueue/{topic}" --method POST --function enqueue

fission mqtrigger create --name weather-processing \
   --function wprocessor \
   --mqtype kafka \
   --mqtkind keda \
   --topic weather \
   --resptopic observations \
   --errortopic errors \
   --maxretries 3 \
   --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092 \
   --metadata consumerGroup=my-group \
   --cooldownperiod=30 \
   --pollinginterval=5

fission mqtrigger create --name airquality-processing \
   --function aprocessor \
   --mqtype kafka \
   --mqtkind keda \
   --topic airquality \
   --resptopic observations \
   --errortopic errors \
   --maxretries 3 \
   --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092 \
   --metadata consumerGroup=my-group \
   --cooldownperiod=30 \
   --pollinginterval=5

fission mqtrigger create --name add-observations \
   --function addobservations \
   --mqtype kafka \
   --mqtkind keda \
   --topic observations \
   --errortopic errors \
   --maxretries 3 \
   --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092 \
   --metadata consumerGroup=my-group \
   --cooldownperiod=30 \
   --pollinginterval=5
```

From the logs you should now be able to see the data flowing from the harvesters to the processors and finally to ElasticSearch
(you can also have a look at the queues with the Kafka-UI).

After a while enough data would be harvested to be able to query ElasticSearch.

NOTE: depending on how we define the document ID in the `addpbservations` function, the same document may be added multiple times
(if we were to omit the document Id a new one will be generated automatically by ElasticSearch).

#### Create a data view from Kibana

Go to Kibana, create a data view named "observations" with pattern "observation\*" and timestamp field "timestamp", and check that the documents have been
added to the index by going to "Analysis / Discover".

Now Kibana can be used to test search queries or to have a look at the data.

## Harvesting requests

### Harvest Data from the Bureau of Meteorology

List of stations:
http://reg.bom.gov.au/vic/observations/melbourne.shtml

Single station observations:
http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json

### Harvest data from the Air Quality Project

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

## Un-installation of the software stack

```shell
for e in $(kubectl get function -o=name) ; do
    kubectl delete ${e}
done

for e in $(kubectl get package -o=name) ; do
    kubectl delete ${e}
done

for e in $(kubectl get environment -o=name) ; do
    kubectl delete ${e}
done

for crd in $(kubectl get crd --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}' | grep fission) ; do
    kubectl delete crd ${crd}
done

helm uninstall fission --namespace fission

for p in $(kubectl get pods -o=name) ; do
    kubectl delete ${p}
done

for p in $(kubectl get kafkatopic -n kafka -o=name) ; do
    kubectl delete ${p} -n kafka
done

kubectl delete -k "github.com/fission/fission/crds/v1?ref=v${FISSION_VERSION}"
helm uninstall keda --namespace keda
helm uninstall kafka-ui
kubectl delete kafka my-cluster --namespace kafka
helm uninstall kafka --namespace kafka
```
