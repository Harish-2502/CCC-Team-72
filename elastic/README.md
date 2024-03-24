# ElasticSearch

## Pre-requirements

- OpenStack RC file and API password obtained and sourced in current shell (see [here](../installation/README.md#client-configuration))
- A Kubernetes cluster created on NeCTAR (see [here](../installation/README.md#elasticsearch))
- Connect to [Campus network](https://studentit.unimelb.edu.au/wifi-vpn#uniwireless) if on-campus or [UniMelb Student VPN](https://studentit.unimelb.edu.au/wifi-vpn#vpn) if off-campus
- Kubernetes cluster is accessible (see [here](../installation/README.md#accessing-the-kubernetes-cluster))
- ElasticSearch is installed (see [here](../installation/README.md#elasticsearch))

> Note: the code used here is for didactic purposes only. It has no error handling, no testing, and is not production-ready.

## Accessing the ElasticSearch API and the Kibana User Interface

To access services on the cluster, one has to use the `port-forward` command of `kubectl` in a new terminal window.

```shell
kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
```

> Note: This command will start the port forwarding so please keep this terminal open and do not close it.

```shell
kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
```

To access the Kibana user interface, one has to use the `port-forward` command of `kubectl` (another terminal window):

```shell
kubectl port-forward service/kibana-kibana -n elastic 5601:5601
```

> Note: This command will start the port forwarding so please keep this terminal open and do not close it.
> Note: The port forwarding can be stopped by pressing `Ctrl + C` and closing the terminal window. The port forwarding is only active when the terminal window is open. Once it is stopped, you need to re-run the command to start the port forwarding again.

Test the ElasticSearch API:

```shell
curl -k 'https://127.0.0.1:9200' --user 'elastic:elastic' | jq '.'
curl -k 'https://127.0.0.1:9200/_cluster/health' --user 'elastic:elastic' | jq '.'
```

Test the Kibana user interface by pointing the browser to: `http://127.0.0.1:5601/` (the default credentials are `elastic:elastic`).

## Create an ElasticSearch Index

```shell
curl -XPUT -k 'https://127.0.0.1:9200/students'\
   --header 'Content-Type: application/json'\
   --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 1
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
curl -XPUT -k "https://127.0.0.1:9200/students/_doc/1234567"\
  --header 'Content-Type: application/json'\
  --data '{
        "name": "John Smith",
        "course": "Cloud Computing",
        "mark": 80
  }'\
  --user 'elastic:elastic' | jq '.'

curl -XPUT -k "https://127.0.0.1:9200/students/_doc/0123456"\
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
curl -XGET -k "https://127.0.0.1:9200/students/_search"\
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

Go to Kibana, create a data view named "students" with pattern "student\*", and check that the documents have been
added to the index by going to "Analysis / Discover".

Now Kibana can be used to test search queries or to have a look at data.

## ElasticSearch parent-child join

To avoid repeating data about the course, it is possible to create a parent-child relationship between the student and the course.
with some limitations.

Let's first delete the `students` index:

```shell
curl -XDELETE -k 'https://127.0.0.1:9200/students'\
   --user 'elastic:elastic' | jq '.'
```

Then let's re-create the database with a mapping that defines the parent-child relationship:

```shell
curl -XPUT -k 'https://127.0.0.1:9200/students' \
  --header 'Content-Type: application/json' \
  --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 1
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
curl -XPUT -k "https://127.0.0.1:9200/students/_doc/1?routing=comp90024"\
  --header 'Content-Type: application/json'\
  --data '{
        "name": "COMP90024",
        "coursedescription": "Cloud Computing",
        "relation_type": {
          "name": "parent"
        }
    }'\
  --user 'elastic:elastic' | jq '.'

curl -XPUT -k "https://127.0.0.1:9200/students/_doc/2?routing=comp90024"\
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

curl -XPUT -k "https://127.0.0.1:9200/students/_doc/3?routing=comp90024"\
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
curl -XGET -k "https://127.0.0.1:9200/students/_search"\
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

### Data setup

Create an ElasticSearch Index to hold temperatures

```shell
curl -XPUT -k 'https://127.0.0.1:9200/temperatures'\
   --header 'Content-Type: application/json'\
   --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 1
        }
    },
    "mappings": {
        "properties": {
            "date": {
                "type": "keyword"
            },
            "temperature": {
                "type": "dense_vector",
                "dims": 24,
                "index": true,
                "similarity": "cosine",
                "index_options": {
                    "type": "hnsw",
                    "m": 16,
                    "ef_construction": 100
                }
            }
        }
    }
}'\
   --user 'elastic:elastic' | jq '.'
```

Load temperatures data

```shell
node loadTemperature.js
```

### Vector search

Search for the most similar temperature vector to a vector of typical Vancouver temperatures in the month of January (expressed in Kelvin).

```shell
curl -XGET -k "https://127.0.0.1:9200/temperatures/_search"\
  --header 'Content-Type: application/json'\
  --data '{
  "knn": {
    "field": "temperature",
    "query_vector": [274.62,275.18,275.9,276.74,277.65,278.56,279.4,280.12,280.68,281.03,281.15,281.03,280.68,280.12,279.4,278.56,277.65,276.74,275.9,275.18,274.62,274.27,274.15,274.27],
    "k": 10,
    "num_candidates": 100
  },
  "fields": [ "date" ]
}'\
  --user 'elastic:elastic' | jq '.'
```
