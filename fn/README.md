# Build and deployment of Fn

These are the steps to follow in order to deploy an Fn instance running on a single computer.


## Install and start Fn

```shell script
curl -LSs https://raw.githubusercontent.com/fnproject/cli/master/install | sh
fn start --log-level DEBUG
```

(For instructions on operating systems othe than Linux, see [Quickstart](https://github.com/fnproject/fn#quickstart).
Also, you may need to prefix all the the `docker` and `fn` commands with `sudo`, depending
on your Docker installation type.)


Check the Fn server has started by opening another shell:
```shell script
docker ps
```


### Development of a Sample Function (Node,js)

Sample function creaation:
```shell script
fn init --runtime node --trigger http wcmp 
```

A new directory name `wcmp` should have been added; a few editings has to be done to its contensts:

Create a `Dockerfile` file with the contents:
```dockerfile
FROM fnproject/node:dev as build-stage
WORKDIR /function
ADD package.json /function/
RUN npm install

FROM fnproject/node
WORKDIR /function
ADD . /function/
COPY --from=build-stage /function/node_modules/ /function/node_modules/
ENTRYPOINT ["node", "func.js"]
```

Replace `func.js` with:
```javascript
const fdk = require ('@fnproject/fdk');

fdk.handle (function (input) {
  let counts = {};
  input.toLowerCase ()
    .split(/\W+/)
    .filter ((w) => {
      return w.length > 1;
    })
    .forEach ((w) => {
      counts[w] = (counts[w] ? counts[w] + 1 : 1);
    });
  return counts;
})
```

In the `func.yaml` file, change `runtime: node` to `runtime: docker`.

Create an Fn `app` (group of functions):
```shell script
fn create app wcapp
```

Function build and deployment on the lcoal Fn server:
```shell script
fn deploy --app wcapp --local wcmp
fn list functions wcapp 
```

Function invokation:
```shell script
curl -XPOST 'http://localhost:8080/t/wcapp/wcmp' --data 'lorem ipsum'
```


## Start the Fn Web-admin

Start the Fn webadmin user interface:
```shell
docker run --rm -it --link fnserver:api -p 4000:4000 -e FN_API_URL=http://api:8080 -e FN_LISTENER=unix:/iofs/lsnr.sock fnproject/ui
```

Point your browser to `http://0.0.0.0:4000`. 


## Testing Fn scalability

In another shell, download Wikipedia pages for the test

```shell script
pages="italy china france germany australia brazil denmark mexico zambia thailand"
for page in ${pages};
   do curl "https://en.wikipedia.org/w/api.php?format=xml&action=parse&prop=wikitext&page=${page}"\
      -o /tmp/${page}.xml      
done
```

Call the word-count functions on the downloaded pages concurently whilelooking at the `wcapp` 
app statistics on the UI:
```shell script
for i in {1..100};
  do
    for page in ${pages};
      do curl -XPOST 'http://localhost:8080/t/wcapp/wcmp' --data @/tmp/${page}.xml &      
    done
  done
```

On the UI window, the number of replicas can be observed to raise, and then fall.


### Development of a Sample Function (Python)

Sample function creaation:
```shell script
fn init --runtime python --trigger http pywcmp 
```

A new directory name `pywcmp` should have been added; a few editings has to be done to its contensts:

Replace `func.py` with:
```python
import json
import io
from fdk import response
async def handler(ctx, data: io.BytesIO=None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(str(ex))
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "Hello {0}".format(name)}), 
        headers={"Content-Type": "application/json"}
    )
```

Function build and deployment on the lcoal Fn server:
```shell script
fn deploy --app wcapp --local pywcmp
fn list functions wcapp 
```

Function invokation:
```shell script
curl -XPOST 'http://localhost:8080/t/wcapp/pywcmp' --data 'lorem ipsum'
```
