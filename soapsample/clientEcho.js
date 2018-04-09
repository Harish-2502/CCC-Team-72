require("soap").createClient(
    "./EchoService.wsdl",
    function(err, client) {
      client.EchoService.EchoService.SayHi
      ({
        Hi : "Hello class!"
      }, function(err, result) {
        console.log(JSON.stringify(result));
      });
    });