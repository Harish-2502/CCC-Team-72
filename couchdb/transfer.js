const twitterDB = `http://${process.env.user}:${process.env.pass}@${process.env.masternode}:5984/twitter`;
const twitterpartDB = `http://${process.env.user}:${process.env.pass}@${process.env.masternode}:5984/twitterpart`;
const http = require ('http');

// Read all documents in the partioned database
http.request (`${twitterDB}/_all_docs?include_docs=true`, {method: 'GET'}, (res) => {
  if (res.statusCode !== 200) {
    console.log (`*** Error in requesting all documents: ${res.statusCode}`);
    process.exit (1);
  }

  let resBody = '';
  res.on ('data', (chunk) => {
    resBody += chunk
  });
  res.on ('error', (err) => {
    console.log(`ERROR ${JSON.stringify(err)}`);
  });

  // Once all the docments ha ve been read
  res.on ('end', (chunk) => {

    // For every document
    JSON.parse (resBody).rows.forEach ((row) => {

      // Avoids partittioning documents without a screen_name (such us CouchDB Design documents)
      if (row.doc.user && row.doc.user.screen_name) {

        // Remove the Document ID and Revision coming from the old database
        delete row.doc._id;
        delete row.doc._rev;

        // Add the new document with a partioned ID (the prefix 'T-' is to avoid starting the
        // Document ID with an underscore, which is illegal in CouchDB
        http.request (`${twitterpartDB}/T-${row.doc.user.screen_name}:${row.doc.id}`,
          {method: 'PUT'},
          (res) => {
            if (res.statusCode !== 201) {
              console.log (`*** Error ${res.statusCode} in adding document ${row.id}`);
            }
          }
        ).end (JSON.stringify (row.doc));
        // Add all non-tweets document to the unpartitioned database
      } else {
        console.log (`Skipping document ${row.id}`);
      }
    });
  });
}).end ();



