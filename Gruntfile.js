module.exports = function (grunt) {
  grunt
    .initConfig({
      "couch-compile": {
        dbs: {
          files: {
            "/tmp/twitter.json": "couchdb/twitter/language"
          }
        }
      },
      "couch-push": {
        options: {
          user: process.env.user,
          pass: process.env.pass
        },
        twitter: {
          files: {
            "http://172.17.0.2:5984/twitter": "/tmp/twitter.json"
          }
        }
      }
    });

  grunt.loadNpmTasks("grunt-couch");
};
