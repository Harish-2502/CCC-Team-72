# Installation and usage of a CouchDB cluster

The following instructions details how to setup a cluster of CouchDB databases on
Docker containers simulating independent nodes.


## Prerequirements

A Linux-based system. (MacOS scripts to install the CouchDB cluster are provided under the `macos` directory.)


## Cluster setup
 
The following instructions apply only to Linux-based systems; for MacOS please move to the `macos` directory and execute `run.sh`. 

Set node IP addresses, electing the first as "master node"
and admin credentials (make sure you have no other Docker containers running):
```shell script
export declare -a nodes=(172.17.0.4 172.17.0.3 172.17.0.2)
export masternode=`echo ${nodes} | cut -f1 -d' '`
export declare -a othernodes=`echo ${nodes[@]} | sed s/${masternode}//`
export size=${#nodes[@]}
export user='admin'
export pass='admin'
export VERSION='3.2.1'
export cookie='a192aeb9904e6590849337933b000c99'
```
(Ignore the `bash: export: `-a': not a valid identifier` error if it were to appear.)

```shell script
docker pull ibmcom/couchdb3:${VERSION}
```

Create Docker containers (stops and removes the current ones if existing):
```shell script
for node in "${nodes[@]}" 
  do
    if [ ! -z $(docker ps --all --filter "name=couchdb${node}" --quiet) ] 
       then
         docker stop $(docker ps --all --filter "name=couchdb${node}" --quiet) 
         docker rm $(docker ps --all --filter "name=couchdb${node}" --quiet)
    fi 
done

for node in "${nodes[@]}" 
  do
    docker create\
      --name couchdb${node}\
      --env COUCHDB_USER=${user}\
      --env COUCHDB_PASSWORD=${pass}\
      --env COUCHDB_SECRET=${cookie}\
      --env ERL_FLAGS="-setcookie \"${cookie}\" -name \"couchdb@${node}\""\
      ibmcom/couchdb3:${VERSION}
done
```

Put in `conts` the Docker container IDs:
```shell script
declare -a conts=(`docker ps --all | grep couchdb | cut -f1 -d' ' | xargs -n${size} -d'\n'`)
```

Start the containers (and wait a bit while they boot):
```shell script
for cont in "${conts[@]}"; do docker start ${cont}; done
```


Set up the CouchDB cluster:
```shell script
for node in ${othernodes} 
do
    curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json"\
      --data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\",\
             \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\",\
             \"remote_node\": \"${node}\", \"node_count\": \"$(echo ${nodes[@]} | wc -w)\",\
             \"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"
done

for node in ${othernodes}
do
    curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup"\
      --header "Content-Type: application/json"\
      --data "{\"action\": \"add_node\", \"host\":\"${node}\",\
             \"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"
done
```

(Ignore the `{"error":"setup_error","reason":"Cluster setup unable to sync admin passwords"}` message.)

Finish the cluster setup
```shell
curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup"\
    --header "Content-Type: application/json" --data "{\"action\": \"finish_cluster\"}"
```

Check whether the cluster configuration is correct:
```shell script
for node in "${nodes[@]}"; do  curl -X GET "http://${user}:${pass}@${node}:5984/_membership"; done
```

Adding a database to one node of the cluster makes it to be created on all other nodes as well:
```shell script
curl -XPUT "http://${user}:${pass}@${masternode}:5984/twitter"
for node in "${nodes[@]}"; do  curl -X GET "http://${user}:${pass}@${node}:5984/_all_dbs"; done
```


## Cluster nodes on different VMs

To deploy a CouchDB cluster on different VMs (say, on MRC), the steps above have to be changed significantly:
* Docker commands have to be run on each node
* Security groups have to set up to allow communications between nodes;
* IP address have to follow the ones assigned by MRC.

(For more details [https://docs.couchdb.org/en/latest/setup/cluster.html](https://docs.couchdb.org/en/latest/setup/cluster.html).)   


## Cluster management

For Linux-based system first run the "Set node IP addresses, electing the first as "master node" 
and admin credentials" above.  For MacOS, change the IP addresses as needed, using the ones specified in the `run.sh` script under the `macos` directory.  

Fauxton user interface (`http://172.17.0.2:5984/_utils`).

Put in `conts` the Docker container IDs
```shell script
declare -a conts=(`docker ps --all | grep couchdb | cut -f1 -d' ' | xargs -n${size} -d'\n'`)
```

Starts the cluster 
```shell script
for cont in "${conts[@]}"; do docker start ${cont}; done
```

Shutdowns the cluster nicely
```shell script
for cont in "${conts[@]}"; do docker stop ${cont}; done
```

Deletes the cluster containers
```shell script
for cont in "${conts[@]}"; do docker rm --force ${cont}; done
```


## Loading of sample data

Once the cluster is started, some data can be added:
```shell script
(
  cd couchdb
  curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_bulk_docs " --header "Content-Type: application/json" \
    --data @./twitter/data.json
)
```


## MapReduce views, and list/show functions

Add a design document with MapReduce Views, Lists and Shows functions.
```shell script
(
  cd couchdb
  export dbname='twitter'
  grunt couch-compile
  grunt couch-push
)  
```

Request a MapReduce View
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_view/language?reduce=true&group_level=1"
```

Request a show function returning HTML
```shell script
docid=`curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_all_docs?limit=1" | jq '.rows[].id' | sed 's/"//g'`
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_show/html/${docid}"
```

Request a list function returning HTML
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_list/html/language?reduce=true&group_level=2"
```

Request a list function returning GeoJSON
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_list/geojson/language?reduce=false&include_docs=true" | jq '.' > /tmp/twitter.geojson
```
You can now load the GeoJSON in a text editor, or display them on a map using QGIS


## Mango queries and indexes

Mango query request
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_find" \
--header "Content-Type: application/json" --data '{
   "fields" : ["_id", "text", "user.screen_name"],
   "selector": {
      "user.lang": {"$eq": "ja"}
   }
}'  | jq '.' -M
```

Mango query explanation (use of indexes, or lack-there-of, etc)
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_explain" \
--header "Content-Type: application/json" --data '{
   "fields" : ["_id", "text", "user.screen_name"],
   "selector": {
      "user.lang": {"$eq": "ja"}
   }
}'  | jq '.' -M
```

More complex Mango query, with tweets sorted by screen_name (it should return a warning, 
because no index has been defined for the sort field):
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_find" --header "Content-Type: application/json" --data '{
   "fields" : ["_id", "user.lang", "user.screen_name", "text"],
   "selector": {
      "$and": [
        {"user.lang": {"$eq": "en"}},
        {"user.screen_name": {"$gt": "pin"}}
      ]
   }, 
   "sort": [{"user.screen_name": "asc"}]
}' | jq '.' -M
```

Create index for lang and screen_name, hence the above query runs faster, but, still,
it cannot efficiently sort by screen_name, since this index order documents for the combination
of lang and screen_name, not for either field taken in isolation (same as SQL DBSMes) 
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_index" \
--header "Content-Type: application/json" --data '{
   "ddoc": "indexes",
   "index": {
      "fields": ["user.lang", "user.screen_name"]
   },
   "name": "lang-screen-index",
   "type": "json"
}'
```

Create index for just the screen_name, now the query should be faster 
(not that one can notice with just 1,000 documents withoud instrumentation, but you get the idea):
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_index" \
--header "Content-Type: application/json" --data '{
   "ddoc": "indexes",
   "index": {
      "fields": ["user.screen_name"]
   },
   "name": "screen-index",
   "type": "json"
}'
```

Get the list of indexes
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_index" | jq '.' -M
```
(Partial indexes selector may be used to exclude some documents from indexing, in order to speed up indexing.)

Indexes can be deleted as well:
```shell script
curl -XDELETE "http://${user}:${pass}@${masternode}:5984/twitter/_index/indexes/json/lang-screen-index"
```

## Spatial indexes

Index by location (works only for points, and it is higly inefficient, but it works for small datasets).
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_index" \
--header "Content-Type: application/json" --data '{
   "ddoc": "indexes",
   "index": {
      "fields": ["coordinates.coordinates"]
   },
   "name": "coordinates",
   "type": "json"
}'
```

Query data by their longitude (the index is now built, analogously to the MapReduce views)
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_find" --header "Content-Type: application/json" --data '{
   "fields" : ["_id", "user.lang", "user.screen_name", "text", "created_at", "coordinates"],
   "selector": {
      "$and": [
        {"coordinates.coordinates": {"$gt": [115.3]}},
        {"coordinates.coordinates": {"$lt": [115.6]}}
      ]
   }
}' | jq '.' -M
```
(Only the longitude is part of the query since Mango indexes only the first element of an array
-`coordinates.coordinates` is an array.)


## Full-text search (search indexes)

Create a search index:
```shell script
curl -XPUT "http://${user}:${pass}@${masternode}:5984/twitter/_design/textsearch"\
  --header 'Content-Type:application/json'\
   --data @./couchdb/twitter/textsearch/text.json
```

Query all the tweets in Japanese:
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_design/textsearch/_search/text"\
  --header 'Content-Type:application/json'\
  --data '{"q": "language:ja"}' | jq '.'
```

Query all the tweets in English that contains the words 'weekend' and 'days';
```shell script
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_design/textsearch/_search/text"\
  --header 'Content-Type:application/json'\
  --data '{"q": "language:en AND (text:weekend AND text:days)"}' | jq '.'
```


## Creation and use of partitioned database

Create a partitioned database:
```shell script
curl -XPUT "http://${user}:${pass}@${masternode}:5984/twitterpart?partitioned=true"
```

Transfer the tweets to the partitioned database partitioning by user's screen name:
```shell script
node ./couchdb/transfer.js
```
(The program above is a simplified code that is not optimized for large databases.)


Get some information on a partition:
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitterpart/_partition/T-ABCrusader" | jq '.'
```

List all the documents in a given partition (should return all the tweets of user `ABCrusader`):
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitterpart/_partition/T-ABCrusader/_all_docs" | jq '.'
```
 
Since partitioned databases cannot use custom `reduce` functions, we cannot just use the design document of the other database.
 
Add a design document with MapReduce Views, Lists and Shows functions
```shell script
export dbname='twitterpart'
curl -X PUT http://${user}:${pass}@${masternode}:5984/${dbname}/_design/language\
   --data '{"views":{"language":{"map":"function(doc) { emit([doc.user.lang], 1); }", "reduce":"_count"}}}'\
   --header 'Content-Type:application/json'
```

Executes a partitioned query:
```shell script
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitterpart/_partition/T-ABCrusader/_design/language/_view/language?reduce=true&group_level=2" | jq '.'
```

Non-partitioned views have to be explicitly declared during the creation of a design document, by adding `partitioned: false` to their `options` property.
(By default, all views in a partitioned database are partitioned.)

