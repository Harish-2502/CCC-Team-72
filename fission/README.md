# Fission FaaS

## Pre-requireemnts

* A cluster on NeCTAR (see the "elastic" directory)
* ElasticSearch already installed (see above)
* "k" and "o" aliases defined (see above)
* RC file (with password inserted) read (see above)
* "KUBECONFIG" environment variable set (see above)


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

Create the Python environment on the cluster with the Python builder (it allows to extend the base Python image):
```shell
fission env create --name python --image fission/python-env --builder fission/python-builder
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
fission function create --name health --env python --code ./functions/health.py
fission function test --name health | jq '.' 
```

Create an ingress so that the function can be accessed from outside the cluster:
```shell
fission route create --url /health --function ./functions/health --createingress
```

Grab the IP address of the router and send a request:
```shell
IP=$(k get svc -n fission | grep router | tr -s " " | cut -f 4 -d' ')
curl "http://${IP}/health" -vvv
````


## Create a Fission Function that harvests Data from the Bureau of Meteorology and stores them in ElasticSearch

```shell
fission function create --name bom --env python --code ./functions/bom.py
fission function test --name bom | jq '.' 
```


## Call the function at interval using a timer trigger

```shell
fission timer create --name everyminute --function bom --cron "@every 1m"
fission function log -f --name bom
```

Delete the timer:
```shell
fission timer delete --name everyminute
```


## Create a function that uses additional Python libraries

The function used so far are very simple and do not require any additional Python libraries: let's
see how we can pack libraries together with a function source code.

In order to do so, a `requirements.txt` file must be created in the same directory as the function, then
a `build.sh` command must be created to install the libraries and finally the function must be packaged in a ZIP file.

```shell
zip -jr adddoc.zip functions/adddoc/
```

Creation of a function with dependencies:
```shell
fission package create --sourcearchive adddoc.zip\
  --env python\
  --name adddoc\
  --buildcmd './build.sh'
```

Check the package has been created:
```shell
fission package list | grep adddoc 
```

Function creation:
```shell
fission fn create --name adddoc\
  --pkg adddoc\
  --entrypoint "adddoc.main" # Function name and entrypoint
```

Test the function:
```shell
fission function test --name adddoc | jq '.'
```


## Create a function composition

TO DO


## Harvest Data from the Bureau of Meteorology

List of stations:
http://reg.bom.gov.au/vic/observations/melbourne.shtml

Single station observations: 
http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json


