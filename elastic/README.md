# ElasticSearch

## Pre-requireemnts

* OpenStack clients (`sudo snap install openstackclients`) 5.4.x
* Kubectl 1.28.x
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
* Read in the RC file (insert the OpenStack password when requested);
```shell
. ./<your project name>-openrc.sh
```
* Create a Kubernetes cluster named "elastic" with the MRC Dashboard (1 master node of a `r3.small` flavor, at least 3 worker nodes of `r3.medium`);
* NOTE: how a single student can have enough resources for the whole team?
* Check whether the cluster has been created healthy:
```shell
o coe cluster show elastic --fit-width
```
(`health_status` should be 'HEALTHY' and `coe_version` should be `1.23.x`);
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
elastic-42ehxxqwt3lv-node-3     Ready    <none>   25h   v1.25.9
```


## Accessing the Kubernetes Dashboard

FIXME: the dashboard does not work following the instruction on [NeCTAR](https://tutorials.rc.nectar.org.au/kubernetes/03-administer-cluster) 
(the token does not seem to be generated).


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
  -f ./values.yaml \
  --set esJavaOpts='-Xms2g -Xmx6g' \
  --set replicas=3 \
  elasticsearch elastic/elasticsearch
```

kubectl patch sts elastic-operator -n elastic -p '{"spec":{"template":{"spec":{"containers":[{"name":"manager", "resources":{"limits":{"memory":"2Gi"}}}]}}}}'


## ElasticSearch Cluster Removal

```shell
helm uninstall elasticsearch -n elastic
``` 
