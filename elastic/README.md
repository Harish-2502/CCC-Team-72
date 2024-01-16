# ElasticSearch

## Pre-requirements

* OpenStack clients (`sudo snap install openstackclients`) 5.4.x
* JQ 1.6.x (`apt install jq`)
* MRC project with enough resources to create a Kubernetes cluster
* Kubectl 1.28.x (installation instructions)[https://kubernetes.io/docs/tasks/tools/]
* Helm 3.6.x (installation instructions)[https://helm.sh/docs/intro/install/]
* Have the University of Melbourne VPN client installed and connected to the VPN


## Client Configuration

* Download the OpenStack RC file from the MRC Dashboard the directory you are in;
* Add an alias to simplify typing
```shell
alias o='/snap/bin/openstack'
alias k=$(which kubectl)
```
* Insert the OpenStack password  in the `./<your project name>-openrc.sh` file
* Read in the RC file in your shell:
```shell
. ./<your project name>-openrc.sh
```


## Cluster Template Creation

```shell
o coe cluster template create\
  --keypair "lmorandiniATisenbrandt2"\
  --labels "container_infra_prefix=registry.rc.nectar.org.au/nectarmagnum/;\
master_lb_floating_ip_enabled=false;\
cinder_csi_enabled=true;\
docker_volume_type=standard;\
ingress_controller=octavia;\
container_runtime=containerd;\
containerd_version=1.6.20;\
containerd_tarball_sha256=1d86b534c7bba51b78a7eeb1b67dd2ac6c0edeb01c034cc5f590d5ccd824b416;\
kube_tag=v1.26.8;\
flannel_tag=v0.21.5;\
cloud_provider_tag=v1.26.3;\
cinder_csi_plugin_tag=v1.26.3;\
k8s_keystone_auth_tag=v1.26.3;\
octavia_ingress_controller_tag=v1.26.3;\
coredns_tag=1.10.1;\
csi_snapshotter_tag=v6.2.1;\
csi_attacher_tag=v4.2.0;\
csi_resizer_tag=v1.7.0;\
csi_provisioner_tag=v3.4.1;\
csi_node_driver_registrar_tag=v2.8.0;\
availability_zone=melbourne-qh2-uom;\
fixed_subnet_cidr=192.168.10.0/24"\
  --floating-ip-disabled\
  --master-lb-enabled\
  --master-flavor='5d8b8337-dc22-4ac7-9d4c-fda749d364bf'\
  --flavor='5d8b8337-dc22-4ac7-9d4c-fda749d364bf'\
  --server-type='vm'\
  --external-network='melbourne'\
  --image='fedora-coreos-37'\
  --volume-driver='cinder'\
  --docker-storage-driver='overlay2'\
  --network-driver='flannel'\
  --coe='kubernetes'\
  --dns-nameserver='128.250.201.5,128.250.66.5'\
kubernetes-melbourne-qh2-uom-nofloat-v1.26.8
```


## Kubernetes Cluster Provisioning

* Create a Kubernetes cluster named "elastic" with the newlt created template (1 master node and 3 worker nodes):
```shell
o coe cluster create\
  --keypair "<your keypair from the MRC dashboard>"\
  --cluster-template "kubernetes-melbourne-qh2-uom-nofloat-v1.26.8"\
  --flavor "uom.mse.2c9g"\
  --master-flavor "uom.mse.2c9g"\
  --node-count 3\
  --master-count 1\
  --floating-ip-disabled\
  elastic
```
* Check whether the cluster has been created healthy (it may take several minutes):
```shell
o coe cluster show elastic --fit-width
```
(`health_status` should be 'HEALTHY' and `coe_version` should be `1.26.8`);
* Create a VM named "bastion" with the following features (the VM can be created using the MRC Dashboard)):
    - Flavor: `uom.mse.1c4g`;
    - Image: `NeCTAR Ubuntu 22.04 LTS (Jammy) amd64 (with Docker)`;
    - Networks: `qh2-uom-internal` and `elatic` (the Kubernetes cluster network);
    - Security group: `default` and `ssh`.
* Once the VM has been created successfully, open an SSH tunnel that allows the connection of your laptop to the Kubernetes cluster:
```shell
ssh -N -L 6443:<ip addres of the kubernetes master node>:6443 ubuntu@<bastion vm ip address>
```
(the tunnel must run throughout the session, in case of malfunctions it has to be restarted.)
* Create the Kubernetes configuration file to access the cluster:
```shell
o coe cluster config elastic
```
* Modify the `config` file by changing the IP address os the server to `127.0.0.1` (as in `server: https://127.0.0.1:6443`)
* Set the Kubernetes configuration file environment variable
```shell
export KUBECONFIG="${PWD}/config"
```
* Check the cluster nodes:
```shell
k get nodes
```
it should return a master node and the required number of nodes:
```
NAME                            STATUS   ROLES    AGE     VERSION
elastic-4spknhuyv5bf-master-0   Ready    master   6m16s   v1.26.8
elastic-4spknhuyv5bf-node-0     Ready    <none>   3m27s   v1.26.8
elastic-4spknhuyv5bf-node-1     Ready    <none>   3m9s    v1.26.8
elastic-4spknhuyv5bf-node-2     Ready    <none>   3m31s   v1.26.8
```

Sometimes the overlay network component is not started correctly, hence it is better to drop and recreate it:
FIXME: ????
```shell
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
. ./<your project name>-openrc.sh
```
The script above has to be executed (`. ./<script name>`) whenever a new shell is opened.


## ElasticSearch Storage Class creation 

FIXME: ????
To retain the disk volumes after the cluster deletion, a storage class has to be created that set the reclaim policy to "retain".
```shell
k apply -f ./storage-class.yaml
```


## ElasticSearch cluster deployment

Set the ElasticSearch version to be used `export ES_VERSION="8.5.1"`, then install ElasticSearch:
```shell
k create namespace elastic
helm repo add elastic https://helm.elastic.co
helm repo update
helm upgrade --install \
  --version=${ES_VERSION} \
  --namespace elastic \
  --set replicas=2 \
  --set secret.password="elastic"\
  elasticsearch elastic/elasticsearch
```
(By default every ElasticSearch node has 30GB of storage.)

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
curl -XPUT -k "https://localhost:9200/students/_doc/1234567"\
  --header 'Content-Type: application/json'\
  --data '{
        "name": "John Smith",
        "course": "Cloud Computing",
        "mark": 80
  }'\
  --user 'elastic:elastic' | jq '.'
curl -XPUT -k "https://localhost:9200/students/_doc/0123456"\
  --header 'Content-Type: application/json'\
  --data '{
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
(The use of a body in a GET request is not ReSTful, and hardly supported by HTTP... but it is allowed by ElasticSearch.)


## Create a data view from Kibana

Go to Kibana, create a data view named "students" with pattern "student*", and check that the documents have been
added to the index by going to "Analysis / Discover".

Now Kibana can be used to test search queries or to have a look at data.


## ElasticSearch parent-child join

To avoid repeating data about the course, it is possible to create a parent-child relationship between the student and the course.
with some limitations.

Let's first delete the `students` index:
```shell
curl -XDELETE -k 'https://0.0.0.0:9200/students'\
   --user 'elastic:elastic' | jq '.'
```

Then let's re-create the database with a mapping that defines the parent-child relationship:
```shell
curl -XPUT -k 'https://0.0.0.0:9200/students' \
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
            "uomid": {
                "type": "text"
            },
            "name": {
                "type": "text"
            },
            "mark": {
                "type": "short"
            },
            "coursedescription": {
                "type": "text"
            },
            "relation_type": {
                "type": "join",
                "relations": {
                    "parent": "child"
                }
            }
        }
    }
}' \
  --user 'elastic:elastic' | jq '.'
```

Let's insert some data about courses and students that use the parent-child relationship:
```shell
curl -XPUT -k "https://localhost:9200/students/_doc/1?routing=comp90024"\
  --header 'Content-Type: application/json'\
  --data '{
        "name": "COMP90024",
        "coursedescription": "Cloud Computing",
        "relation_type": {
          "name": "parent"
        }
    }'\
  --user 'elastic:elastic' | jq '.' 
curl -XPUT -k "https://localhost:9200/students/_doc/2?routing=comp90024"\
  --header 'Content-Type: application/json'\
  --data '{
        "name": "John Smith",
        "uomid": "1234567",
        "mark": 80,
        "relation_type": {
          "name": "child",
          "parent": 1
        }
  }'\
  --user 'elastic:elastic' | jq '.'
curl -XPUT -k "https://localhost:9200/students/_doc/3?routing=comp90024"\
  --header 'Content-Type: application/json'\
  --data '{
        "name": "Jane Doe",
        "uomid": "0123456",
        "mark": 90,
        "relation_type": {
          "name": "child",
          "parent": 1
        }
      }'\
  --user 'elastic:elastic' | jq '.' 
```

Example of a query that returns all students of a give course that have a mark greater than 80:
```shell
curl -XGET -k "https://localhost:9200/students/_search"\
  --header 'Content-Type: application/json'\
  --data '{
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "mark": {
                            "gt": 80
                        }
                    }
                },
                {
                    "has_parent": {
                        "parent_type": "parent",
                        "query": {
                            "match": {
                                "name": "comp90024"
                            }
                        }
                    }
                }
            ]
        }
    }
}'\
  --user 'elastic:elastic' | jq '.'
```


## Use of ElasticSearch as a vector DBMS

TODO.



## Removal

### ElasticSearch Cluster Removal

```shell
helm uninstall kibana -n elastic
helm uninstall elasticsearch -n elastic
``` 


### Kubernetes Cluster Removal


```shell
o coe cluster delete elastic
```


