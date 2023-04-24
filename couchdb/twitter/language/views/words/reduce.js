function (keys, values, rereduce) {
  var langs = {};

  /* Example of keys and values with rereduce == false
 keys:
[
	[
		["at", "tr"], "51f39676462cca21859bd92d8e085745"
	],
	[
		["at", "en"], "51f39676462cca21859bd92d8e1f53bb"
	],
	[
		["at", "en"], "51f39676462cca21859bd92d8e1eaad6"
	],
  ...
	[
		["at", "en"], "51f39676462cca21859bd92d8e0031c2"
	]
]
 values:
 [1, 1, 1, 1, 1, ... 1, 1, 1, 1, 1]
   */

  /* Example of keys and values with rereduce == true
[
   {
  	"en": 13
   },
   {
	  "en": 21
   },
   {
	   "en": 23
   },
   {
	  "tr": 1,
	  "en": 44
   }
]
  */

  // If this is the first iteration (no aggregation, just the output of the map function)
  if (!rereduce) {
    log(`FIRSTREDUCE ${JSON.stringify(keys)} ${JSON.stringify(values)}`);
    keys.forEach(function (key) {
      // key is an array of rows that have the same key (first element of key is the word, second the language).
      var lang = key[0][1];

      // If the language (second component of the key) is not already present in langs, increment
      // the counter (aince it is always 1, not need to check values)
      if (langs[lang]) {
        langs[lang]++;
      } else {
        langs[lang]= 1;
      }

    });
    // If this a successive reduce step
  } else {
    // Merge the partial count contained in values (keys is null for a re-reduce step)
    // and add the word count for every language
    log(`REREDUCE ${JSON.stringify(values)}`);
    values.forEach(function (value) {
      Object.keys(value).forEach(function (lang) {
        if (langs[lang]) {
          langs[lang] += value[lang];
        } else {
          langs[lang]= value[lang];
        }
      });
    });
  }

  return langs;
}
