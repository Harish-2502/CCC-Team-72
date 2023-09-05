# ElasticSearch

## Pre-requireemnts

* OpenStack clients (`sudo snap install openstackclients`)
* Kubectl


## Kubernetes Cluster Provisioning

Create a directory that will hold your cluster configuration:
````shell
mkdir <mycluster>
cd <mycluster>
```

NOTE: how a single student can have enough resources for the whole team?

* Create a cluster with the MRC Dashboard named "elastic";
* Download the OpenStack RC file from the Dashboard the directory you are in;
* Add an alias to simplify typing
```shell
alias o='/snap/bin/openstack'
alias k=$(which kubectl)
```
* Read in the RC file (insert the Dashboard password when requested);
```shell
. ./BDCEX-openrc.sh
```
* Set the Kuberetes configuration file:
```shell
export KUBECONFIG="${PWD}/config"
```
* Create the configuration:
```shell
o coe cluster config <mycluster>
```
* Check the cluster namespaces:
```shell
k get namespaces
```

It should show:
```shell
NAME              STATUS   AGE
default           Active   4h2m
kube-node-lease   Active   4h2m
kube-public       Active   4h2m
kube-system       Active   4h2m
```


## Accessing the Kubernetes Dashboard

FIXME:
```shell
k create clusterrolebinding kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
SECRET_NAME=$(k -n kube-system get secret | grep kubernetes-dashboard-csrf | cut -f1 -d ' ')
k -n kube-system describe secret $SECRET_NAME | grep -E '^token' | cut -f2 -d':' | tr -d " "
k proxy
```

Point your web-browser to: `http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/` and insert the `SECRET_NAME`.





