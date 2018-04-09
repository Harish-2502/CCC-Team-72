require("soap").createClient(
    "http://www.webservicex.com/globalweather.asmx?WSDL",
    function(err, client) {
      client.GlobalWeather.GlobalWeatherSoap12.GetCitiesByCountry({
        CountryName : "Australia"
      }, function(err, result) {
        console.log(result.GetCitiesByCountryResult);
      });
    });