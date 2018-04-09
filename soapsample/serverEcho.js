var http = require("http");
var soap = require("soap");
var fs = require("fs");

var echoService = {
  EchoService : {
    EchoService : {
      SayHi : function(args) {
        console.log("Received: " + args.Hi);
        return {
          SayHiResponse : args.Hi
        };
      }
    }
  }
};

var xml = fs.readFileSync("EchoService.wsdl", "utf8"), server = http
    .createServer(function(request, response) {
      response.end("404: Not Found: " + request.url);
    });

server.listen(8000);
soap.listen(server, "/EchoService", echoService, xml);
console.log("Started EchoService");
