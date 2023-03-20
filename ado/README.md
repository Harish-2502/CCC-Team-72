# ADO API workshop\


## INstllation

* Create a `secrets.sh` file with this contents:
```shell
export ADO_API_KEY="<api key>"
export MASTODON_ACCESS_TOKEN="<access token>>"
```
* Go to [Mastodon.py installation page](https://pypi.org/project/Mastodon.py/#files) and download the WHL file;
* Unzip the downloaded file into this directory.


## ADO login

```python
import os, requests

ado_url = 'https://devapi.ado.eresearch.unimelb.edu.au'
res = requests.post(f'{ado_url}/login', auth = requests.auth.HTTPBasicAuth('apikey', os.environ['ADO_API_KEY']))
headers = {'Authorization': f'Bearer {res.text}', 'Content-Type': 'application/json'}
   
print(requests.get(f'{ado_url}/version', headers = headers).text)
```

If the API key is enabled, the script should print the version of the development API.


## Mastodon login

Load the secrets file and start the Python interpreter:
```shell
. ./secrets.sh
python
```

Test API:
```python
from mastodon import Mastodon
import os

mastodon = Mastodon(api_base_url='https://mastodon.online', access_token = os.environ['MASTODON_ACCESS_TOKEN'])
mastodon.retrieve_mastodon_version()
mastodon.status("109666136628267939")["content"]
```

If the Mastodon API version and the content of a post are printed out, the Mastodon library has been instaled successfully and the
login on the Mastodon server has succeeded.


## Retrieval of post belonging to the same topic in ADO

After the login to ADO API, and before the JWT (JSON Web Token) expires, topics containing a 
top term (`router` in this case) can be looked up and their Tweet IDs can be downloaded
using the following script:
```python
import json

res = requests.get(f'{ado_url}/analysis/nlp/collections/twitter/topics',\
   headers = headers,\
   params = {'startDate' : '2021-07-01' , 'endDate':'2021-07-22', 'fullResult' : False})
   

sel_topics=[]

for d in res.json():
   for t_ind, t in enumerate(d['topics']):
      for term in t['terms']:
         if term[0] == 'router':
            id = d['time'].split('-')
            sel_topics.append(f'{id[1]}{int(id[2]):02d}{int(id[3]):02d}-{t_ind + 1}')
            
res = requests.post(f'{ado_url}/analysis/nlp/collections/twitter/topicposts',\
   headers = headers,\
   json = sel_topics)

            
with open('ado-download-topics.json', 'w') as json_file: 
   json_file.write(json.dumps(res.json()))
```


## Twitter posts "hydration"


## Mastodon posts "hydration"

The Mastodon post IDs downloaded uaing the ADO API are in the format:
`<hostname>`/<user handle>/<post id>`
and wrapped in a CSV format (one post ID per line).

Therefore, the data retrieved from the CSV file have to be split and fed into the Mastodon API to 
retrieve the posts.

An example of a script that does it (assuming the post DIs were downloaded in a file called `ado-download-mastodon.csv`):
```python
from mastodon import Mastodon, MastodonNotFoundError, MastodonRatelimitError
import csv, os, time

with open('ado-download-mastodon.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    for line in csv_reader:
        id = line[0].split('/')
        print(f'\nPost complete ID: {id}')
        try:
           print(Mastodon(api_base_url=f"https://{id[0]}",
                   access_token = os.environ["MASTODON_ACCESS_TOKEN"]
                 ).status(id[2])["content"]
                )
        except MastodonNotFoundError:
            print('*** Post not found')
            continue
        except MastodonRatelimitError:
            print('*** Request rate exceeded')
            time.sleep(2)
            continue
```

Some posts may have been deleted in the meantime and return 404; in addition, there are limitations
to the number of requests a Mastodon server accepts in a given unit of time, raising the `MastodonRatelimitError` exception
(please see the Mastodon API documentation).
