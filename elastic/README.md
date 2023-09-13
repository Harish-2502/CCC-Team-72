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
curl -k 'https://0.0.0.0:9200/_cat/nodes' --user 'elastic:elastic'
```

Test the Kibana user interface by pointing the browser to: `http://0.0.0.0:5601/` (the default credentials are `elastic:elastic`).


Adding access to the API:
```shell
k -f ingress.yaml -n elastic
```


## Install Fission FaaS on the Cluster

```shell
k create namespace fission
k create -k "github.com/fission/fission/crds/v1?ref=v1.19.0"
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
curl -Lo fission https://github.com/fission/fission/releases/download/v1.19.0/fission-v1.19.0-darwin-amd64 && chmod +x fission && sudo mv fission /usr/local/bin/
```

Linux:
```shell
curl -Lo fission https://github.com/fission/fission/releases/download/v1.19.0/fission-v1.19.0-linux-amd64 && chmod +x fission && sudo mv fission /usr/local/bin/
```

Windows:
For Windows, you can use the linux binary on WSL. Or you can download this windows executable: https://github.com/fission/fission/releases/download/v1.19.0/fission-v1.19.0-windows-amd64.exe


## Create a Fission Function and Expose it as a Service

```shell
fission env create --name nodejs --image fission/node-env
curl https://raw.githubusercontent.com/fission/examples/master/nodejs/hello.js > hello.js
fission function create --name hello --env nodejs --code hello.js
fission route create --url /hello --function hello --createingress
```

Test the function:
```shell
IP=$(k get svc -n fission | grep router | tr -s " " | cut -f 4 -d' ')
curl "http://${IP}/hello" -vvv
```


## Harvest Data from the Bureau of Meteorology
TBD:
http://www.bom.gov.au/catalogue/anon-ftp.shtml
IDY03023	Latest Observations from Victoria (hourly update)
IDV60034	Latest Melbourne Observations (VIC)

ftp://ftp.bom.gov.au/anon/gen/fwo/


## ElasticSearch Cluster Removal

```shell
helm uninstall kibana -n elastic
helm uninstall elasticsearch -n elastic
``` 
