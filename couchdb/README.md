# Installation and usage of a CouchDB cluster

The following instructions details how to setup a cluster of CouchDB databases on
Docker containers simulating independent nodes.


## Cluster setup
 
Pulls Docker image 
```
docker pull couchdb:2.1.1
```

Sets node IP addresses, electing the first as "master node"
and admin credentials
```
export declare -a nodes=(172.17.0.2 172.17.0.3 172.17.0.4)
export masternode=`echo ${nodes} | cut -f1 -d' '`
export othernodes=`echo ${nodes[@]} | sed s/${masternode}//`
export size=${#nodes[@]}
export user=admin
export pass=admin
```

Create Docker containers
```
for node in ${nodes[@]}}; do docker create couchdb:2.1.1 -–ip=${node}; done
```

Puts in conts the Docker container IDs
```
declare -a conts=(`docker ps --all | grep couchdb | cut -f1 -d' ' | xargs -n${size} -d'\n'`)
```

Starts the containers
```
for cont in "${conts[@]}"; do docker start ${cont}; done
sleep 3
```

Writes the cookie name and node name to the CouchDB configuration on every node
```
for (( i=0; i<${size}; i++ )); do
    docker exec ${conts[${i}]} \
      bash -c "echo \"-setcookie couchdb_cluster\" >> /opt/couchdb/etc/vm.args"
    docker exec ${conts[${i}]} \
      bash -c "echo \"-name couchdb@${nodes[${i}]}\" >> /opt/couchdb/etc/vm.args"
done
```

Restarts containers to pick-up changes to CouchDB configurations
```
for cont in "${conts[@]}"; do docker restart ${cont}; done
sleep 3
```

Sets the CouchDB cluster (deleting the default nonode@nohost node from the configuration)
```
for node in "${nodes[@]}"; do     
    curl -XPUT "http://${node}:5984/_node/_local/_config/admins/${user}" --data "\"${pass}\""    
    curl -XPUT "http://${user}:${pass}@${node}:5984/_node/couchdb@${node}/_config/chttpd/bind_address" --data '"0.0.0.0"'
done
for node in "${nodes[@]}"; do     
    curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json" \
      --data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \
        \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\", \
        \"remote_node\": \"${node}\", \
        \"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"
done
for node in "${nodes[@]}"; do     
    curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json" \
      --data "{\"action\": \"add_node\", \"host\":\"${node}\", \
        \"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"
done
curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" --data "{\"action\": \"finish_cluster\"}" 
rev=`curl -XGET "http://172.17.0.2:5986/_nodes/nonode@nohost" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
curl -X DELETE "http://172.17.0.2:5986/_nodes/nonode@nohost?rev=${rev}"  --user "${user}:${pass}"
```

Checks the correct cluster configuration
```
for node in "${nodes[@]}"; do  curl -X GET "http://${user}:${pass}@${node}:5984/_membership"; done
```

Adding a database to one node of the cluster cause it to be created on all other nodes as well
```
curl -XPUT "http://${user}:${pass}@${masternode}:5984/twitter"
for node in "${nodes[@]}"; do  curl -X GET "http://${user}:${pass}@${node}:5984/_all_dbs"; done
```

Adds Twitter data
```
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_bulk_docs " --header "Content-Type: application/json" \
  --data @./couchdb/twitter/data.json
```

Add a design document with MapReduce Views, Lists and Shows functions
```
grunt couch-compile
```

Tries out a MapReduce View
```
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_view/language?reduce=true&group_level=2"
```

Tries a show function returning HTML
```
docid=`curl -XGET "http://${masternode}:5984/twitter/_all_docs?limit=1" | jq '.rows[].id' | sed 's/"//g'`
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_show/html/${docid}"
```

Tries a list function returning HTML
```
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_list/html/language?reduce=true&group_level=2"
```

Tries a list function returning GeoJSON
```
curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_design/language/_list/geojson/language?reduce=false&include_docs=true" | jq '.' > /tmp/twitter.geojson"
```
You can now load the GeoJSON in a tetx editor, or display them on a map using QGIS


## TBD
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_find" \
--header "Content-Type: application/json" --data '{
   "fields" : ["_id", "text", "user.screen_name"],
   "selector": {
      "user.lang": {"$eq": "ja"}
   }
}'  | jq '.' -M

curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_find" --header "Content-Type: application/json" --data '{
   "fields" : ["_id", "user.lang", "user.screen_name", "text"],
   "selector": {
      "$and": [
        {"user.lang": {"$eq": "en"}},
        {"user.screen_name": {"$gt": "pin"}}
      ]
   }
}' | jq '.' -M
   ,"sort": [{"user.screen_name": "asc"}]

curl -XPOST "http://${user}:${pass}@${masternode}:5984/twitter/_index" \
--header "Content-Type: application/json" --data '{
   "ddoc": "indexes",
   "index": {
      "fields": ["user.lang", "user.screen_name"]
   },
   "name": "lang-screen-index",
   "type": "json"
}'

curl -XGET "http://${user}:${pass}@${masternode}:5984/twitter/_index" | jq '.' -M

curl -XDELETE "http://${user}:${pass}@${masternode}:5984/twitter/_index/indexes/json/lang-screen-index"

# Shutdowns the cluster nicely 
for cont in "${conts[@]}"; do docker stop ${cont}; done

# Starts the cluster 
declare -a conts=(`docker ps --all | grep couchdb | cut -f1 -d' ' | xargs -n${size} -d'\n'`)
for cont in "${conts[@]}"; do docker start ${cont}; done

# Deletes the cluster containers
declare -a conts=(`docker ps --all | grep couchdb | cut -f1 -d' ' | xargs -n${size} -d'\n'`)
for cont in "${conts[@]}"; do docker rm --force ${cont}; done

# Docker container with full-text search
https://github.com/neutrinity/ntr-couch-docker
