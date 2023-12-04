module.exports = async function (context) {
  console.log ('Item picked up');
  return {
    status: 200,
    body: JSON.stringify (context.request.body.observations.data.map ((obs) => {
        return {
          wmo: obs.wmo,
          name: obs.name,
          geo: [obs.lon, obs.lat],
          local_date_time: obs.local_date_time,
          local_date_time_full: obs.local_date_time_full,
          air_temp: obs.air_temp,
          rel_hum: obs.rel_hum
        };
      }
    ))
  };
}
