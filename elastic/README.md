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
k port-forward service/elasticsearch-master 9200:9200
```

To access the Kibana user interface, one has to use the `port-forward` command of `kubectl`:
```shell
k port-forward service/kibana-kibana 5601:5601
```

The port forwarding can be stopped by pressing `Ctrl-C` (each has to start in a different terminal window) and
when not used it stops and has to be restarted.


## ElasticSearch Cluster Removal

```shell
helm uninstall kibana -n elastic
helm uninstall elasticsearch -n elastic
``` 
