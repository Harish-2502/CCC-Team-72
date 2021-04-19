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
