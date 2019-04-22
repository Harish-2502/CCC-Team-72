# Build and deployment of OpenFaaS on Docker

These are the steps to follow in order to deploy an OpenFaaS instance running on Docker Swarm in a single computer.


## Prerequirements

1. Install Docker CE `https://docs.docker.com/engine/installation/`
2. Install Docker Compose `https://docs.docker.com/compose/install/`
3. About 2GB of RAM available for this deployment
4. A Linux-based shell


## Install and start OpenFaaS

```bash
git clone https://github.com/openfaas/faas
docker swarm init
cd faas
./deploy_stack.sh
```
(Take note of the credentails that have been generated).

Check all Docker services have started:
```bash
docker service ls
```
(There should be six services listed.)


## Admin UI

Point your browser to:
```bash
http://0.0.0.0:8080/ui/
```
and insert the credentials (username and password) generated during installation.


## Creating of a function from a template

(Make sure you are in the `faas` directory, the one where OpenFaaS was installed.)
```bash
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


## Build and Deployment of Word-count function

```bash
# Build and deploy the just-modified function 
faas-cli build --image=wcmpimage --lang=node --handler=./ --name=wcmp # Build image
faas-cli deploy --image=wcmpimage --name=wcmp # Deploy function to local OpenFaaS instance
# Call the function (it shoud return 
curl -XPOST "http://0.0.0.0:8080/function/wcmp" --data 'italy'
```


## Testing OpenFaas scalability

Execute the following (every second it will show the actual and desired function replicas)
```bash
watch -n 1 docker service ls
```

In another shell, download Wikipedia pages for the test
```bash
pages="italy china france germany australia brazil denmark mexico zambia thailand"
for page in ${pages};
   do curl "https://en.wikipedia.org/w/api.php?format=text&action=parse&prop=wikitext&page=${page}"\
      -o /tmp/${page}.html      
done
```

Call the word-count functions on the downloaded pages repeateadly  
```bash
for i in {1..100};
  do
    for page in ${pages};
      do text=`cat /tmp/${page}.html`; curl -XPOST "http://0.0.0.0:8080/function/wcmp" --data "${text}" -o /dev/null -s -w "%{http_code} `date`\n"       
    done
  done
```

In the other shell window, the number of replicas can be observed to raise, and then fall.+
By default the scaling-up (and down) function counts the number of successful (HTTP stastus of 200) function
invocations per function replica in 10 seconds and scale when there are more than 5 of them.
(Every time the number of new function replicas is 20% of the maximum allowed).
  
This rule can be altered changing `openfaas/faas/prometheus/alert.rules.yml` and rebuilding/redeploying  the prometheus service. 
The parameters can be different for every function, and are set as Docker image labels.
  
