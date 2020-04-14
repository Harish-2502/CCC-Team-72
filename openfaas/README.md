# Build and deployment of OpenFaaS on Docker

These are the steps to follow in order to deploy an OpenFaaS instance running on Docker Swarm in a single computer.


## Install and start OpenFaaS

```shell script
git clone https://github.com/openfaas/faas
docker swarm init
cd faas
./deploy_stack.sh
```
(Take note of the credentails that have been generated).

Check all Docker services have started:

```shell script
docker service ls
```
(There should be six services listed.)


### Command-Line Interface installation:

Linux:

```shell script
curl -sSL https://cli.openfaas.com | sudo sh
```

MacOS:

```shell script
brew install faas-cli # or curl -sSL https://cli.openfaas.com | sudo sh
```


### Login to the cluster

Use the username and password generated during installation.

```shell script
faas-cli login -u admin -p <password>
```


## Admin UI (optional)

Point your browser to:

```shell script
http://0.0.0.0:8080/ui/
```

...and insert the credentials (`admin` and password) generated during installation.


## Creating of a function from a template

(Make sure you are in the `faas` directory, the one where OpenFaaS was installed.)

```shell script
faas-cli template pull # Grab all the tamplates in different languages
faas-cli new wcmp --lang=node # Creates a new function in Node.js
cd wcmp # Goes into the newly created function (only package.json and handler.js there)
```


## Word-count function 

Replace `handler.js` with the following code:

```javascript
"use strict";
module.exports = (context, callback) => {
  let counts = {};
  context.toLowerCase ()
    .split (/[ \/\!\-\+\#\$\%\(\)\`\'\":;\.,\{\}\[\]\=\|\*\<\>\t\n]+/)
    .filter ((w) => {
      return w.length > 1;
    })
    .forEach ((w) => {
      counts[w] = (counts[w] ? counts[w] + 1 : 1);
    });
  callback (undefined, counts);
};
```


## Build and Deployment of wcmp function

```shell script
faas-cli build --image=wcmpimage --lang=node --handler=./ --name=wcmp # Build image
faas-cli deploy --image=wcmpimage --name=wcmp # Deploy function to local OpenFaaS instance
curl -XPOST "http://0.0.0.0:8080/function/wcmp" --data 'italy' # Call the function 
```


## Testing OpenFaas scalability

Execute the following (every second it will show the actual and desired function replicas)

(On MacOS, `watch` may need to be installed first with `brew install watch`)

```shell script
watch -n 1 docker service ls
```

In another shell, download Wikipedia pages for the test

```shell script
pages="italy china france germany australia brazil denmark mexico zambia thailand"
for page in ${pages};
   do curl "https://en.wikipedia.org/w/api.php?format=xml&action=parse&prop=wikitext&page=${page}"\
      -o /tmp/${page}.xml      
done
```

Call the word-count functions on the downloaded pages repeateadly  

```shell script
for i in {1..100};
  do
    for page in ${pages};
      do text=`cat /tmp/${page}.xml`; curl -XPOST "http://0.0.0.0:8080/function/wcmp" --data '${text}' -o /dev/null -s -w "%{http_code} `date`\n"       
    done
  done
```

In the other shell window, the number of replicas can be observed to raise, and then fall.+
By default the scaling-up (and down) function counts the number of successful (HTTP stastus of 200) function
invocations per function replica in 10 seconds and scale when there are more than 5 of them.
(Every time the number of new function replicas is 20% of the maximum allowed).
  
This rule can be altered changing `openfaas/faas/prometheus/alert.rules.yml` and rebuilding/redeploying  the prometheus service. 
The parameters can be different for every function, and are set as Docker image labels.
  
